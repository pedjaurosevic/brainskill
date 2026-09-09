"""Runner for BrainSkill Confirmatory Matrix (v3.0).

Protocol:
- Conditions: cot, verify, dual, high_c
- RAG: OFF, ON (frozen packets from dataset.json)
- Dual gate: canonical disagreement triggers conflict re-solve
- Model API: OpenAI-compatible via TABBY_API_URL (operators set real local URL privately; do not commit real ports).
  Default fallback: http://127.0.0.1:8000/v1
- Allowlisted tools: read-only inspection tools on Domain 2 items
- Append-only JSONL logging
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Ensure brainskill root is on sys.path
BENCHMARK_DIR = Path(__file__).resolve().parent
ROOT_DIR = BENCHMARK_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.compiler import compile_messages, load_conditions  # noqa: E402
from modules.grader import answers_disagree, canonicalize, grade_response  # noqa: E402

DATASET_PATH = BENCHMARK_DIR / "dataset.json"
CONDITIONS_PATH = ROOT_DIR / "types" / "conditions.json"

DEFAULT_API_URL = os.environ.get("TABBY_API_URL", "http://127.0.0.1:8000/v1")
DEFAULT_MODEL = os.environ.get("TABBY_MODEL", "Muse-Glimmer-30B-exl3-2.00bpw")

# Inspection tools allowlisted for Domain 2 (fake/simulated outputs for benchmark safety and reproducibility)
INSPECTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash_inspect",
            "description": "Execute a read-only shell diagnostic command (e.g., df, btrfs filesystem df, ss, dmesg, systemctl status).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The read-only diagnostic command to run.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a system status or configuration file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to inspect.",
                    }
                },
                "required": ["path"],
            },
        },
    },
]

# Simulated outputs for Domain 2 inspection tools (ensures benchmark determinism & no side effects)
SIMULATED_OUTPUTS = {
    "d2.01": {
        r"btrfs.*(?:fi|filesystem).*df": "Data, single: total=50.00GiB, used=5.00GiB\nSystem, single: total=32.00MiB, used=16.00KiB\nMetadata, single: total=1.00GiB, used=1.00GiB (ENOSPC)\nGlobalReserve, single: total=16.00MiB, used=0.00B",
        r"dmesg.*BTRFS": "[12345.67] BTRFS critical (device nvme0n1p2): unable to allocate metadata chunk, remounting read-only",
        r"df\s+-h": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/nvme0n1p2   50G  5.0G   45G  10% /",
    },
    "d2.02": {
        r"journalctl|systemctl": "uwsm: hyprctl dispatched before socket /run/user/1000/hypr/.../hyprland.sock created. Error: cannot connect to socket",
        r"ls.*/run/user": "socket created 45ms after exec-once phase",
    },
    "d2.03": {
        r"ss\s+|lsof|fuser": "State  Recv-Q  Send-Q  Local Address:Port   Peer Address:Port  Process\nLISTEN 0       128     127.0.0.1:18765      0.0.0.0:*          users:((\"python3-worker\",pid=4812,fd=4))",
        r"ps\s+": "PID 4812: python3 -m background_worker (holding port 18765)",
    },
    "d2.04": {
        r"nvidia-smi": "GPU 0: NVIDIA GeForce RTX 3060 12GB\nMemory-Usage: 11400MiB / 12288MiB\nProcesses: TabbyAPI (11200MiB)",
    },
    "d2.05": {
        r"waybar|valgrind": "waybar: JSON parse error at line 1 column 42: invalid control character or missing quote",
    },
    "d2.06": {
        r"df\s+-i": "Filesystem      Inodes   IUsed   IFree IUse% Mounted on\n/dev/nvme0n1p3 1000000 1000000       0  100% /var",
        r"df\s+-h": "Filesystem      Size  Used Avail Use% Mounted on\n/dev/nvme0n1p3   50G   10G   40G   20% /var",
    },
    "d2.07": {
        r"ss\s+": "State  Recv-Q  Send-Q  Local Address:Port  Peer Address:Port\nLISTEN 0       128          *:8080              *:*\n# note: socket is IPv6 [::]:8080; ipv6only=1 so 127.0.0.1:8080 is refused",
        r"sysctl.*ipv6|cat.*/proc/sys/net/ipv6": "net.ipv6.bindv6only = 1",
        r"curl|nc\s+": "connect to 127.0.0.1 port 8080: Connection refused\nconnect to ::1 port 8080: succeeded",
    },
    "d2.08": {
        r"systemctl\s+show|systemctl\s+cat": "After=network-online.target\nWants=\nRequires=\n# After= orders only if both units start; it does not pull network-online.target",
        r"cat.*/etc/systemd|network-online": "[Unit]\nDescription=example\nAfter=network-online.target\n# missing Wants=/Requires=network-online.target",
    },
    "d2.09": {
        r"getent|host\s+|dig\s+|nslookup": ";; connection timed out; no servers could be reached\nNXDOMAIN or SERVFAIL for db.internal",
        r"resolv\.conf|cat.*/etc/resolv": "nameserver 10.255.255.1\n# no search domain; resolver unreachable from this namespace",
        r"nsswitch|ping\s+": "PING 10.0.0.12: 64 bytes from 10.0.0.12: icmp_seq=1 ttl=64\ngetent hosts db.internal: (empty)",
    },
    "d2.10": {
        r"getfacl": "# file: secret.txt\nuser::rw-\nuser:user:---\ngroup::r--\nmask::r--\nother::r--",
        r"lsattr": "----i---------e---- secret.txt",
        r"ausearch|journalctl.*(?:apparmor|selinux)|aa-status|getenforce": "apparmor=\"DENIED\" operation=\"open\" profile=\"example\" name=\"/home/researcher/secret.txt\"",
    },
    "d2.11": {
        r"dmesg|journalctl": "Memory cgroup out of memory: Killed process 9911 (worker) total-vm:8192000kB, anon-rss:7800000kB\nmemory.max for cgroup /system.slice/worker.service = 2G",
        r"systemctl\s+show|MemoryMax|memory\.max": "MemoryMax=2G\nMemoryHigh=1.5G\n# host free RAM is irrelevant once the cgroup limit is hit",
        r"free\s+-h": "Mem:  total 32Gi  used 8Gi  free 20Gi  available 22Gi\nSwap: total 8Gi  used 0B  free 8Gi",
    },
    "d2.12": {
        r"locale|echo\s+\$L": "LANG=\nLC_ALL=\n# cron environment often has empty LANG (C / ASCII)",
        r"crontab|cron": "SHELL=/bin/sh\nPATH=/usr/bin:/bin\n# no LANG=C.UTF-8 — interactive shell had LANG=en_US.UTF-8",
        r"python|backup": "UnicodeEncodeError: 'ascii' codec can't encode character '\\xf6' in position 12",
    },
}



def simulate_tool_execution(item_id: str, tool_name: str, arguments: dict[str, Any]) -> str:
    """Return deterministic simulation result for allowlisted inspection tools."""
    item_sims = SIMULATED_OUTPUTS.get(item_id, {})
    cmd_or_path = arguments.get("command") or arguments.get("path") or ""
    for pattern, output in item_sims.items():
        if re.search(pattern, cmd_or_path, re.IGNORECASE):
            return output
    return f"[simulated execution: {tool_name}({cmd_or_path})] status=0 (inspection complete, no anomalies found)"


def call_chat_completion(
    api_url: str,
    api_key: str | None,
    model: str,
    messages: list[dict[str, Any]],
    *,
    temperature: float = 0.2,
    top_p: float = 0.9,
    seed: int | None = None,
    tools: list[dict[str, Any]] | None = None,
    timeout: int = 120,
    max_attempts: int = 2,
) -> dict[str, Any]:
    """POST /chat/completions. Retry once on transport/HTTP failure (same seed/payload)."""
    url = f"{api_url.rstrip('/')}/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
    }
    if seed is not None:
        payload["seed"] = seed
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = json.dumps(payload).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
    assert last_error is not None
    raise last_error


def run_single_turn(
    api_url: str,
    api_key: str | None,
    model: str,
    item: dict[str, Any],
    condition_id: str,
    rag_on: bool,
    seed: int,
    *,
    conflict: bool = False,
    allow_tools: bool = False,
    conditions_spec: dict[str, Any] | None = None,
    max_tool_steps: int = 3,
) -> dict[str, Any]:
    """Run one completion attempt (including tool loop if triggered and allowed)."""
    packet = item.get("rag") if rag_on else None
    messages = compile_messages(
        condition_id=condition_id,
        user_prompt=item["prompt"],
        rag_on=rag_on,
        rag_packet=packet,
        conflict=conflict,
        conditions=conditions_spec,
    )

    tools = INSPECTION_TOOLS if (allow_tools and item.get("tools_allowed")) else None
    tool_calls_logged: list[dict[str, Any]] = []
    total_start = time.perf_counter()

    for step in range(max_tool_steps + 1):
        resp = call_chat_completion(
            api_url=api_url,
            api_key=api_key,
            model=model,
            messages=messages,
            seed=seed,
            tools=tools if step < max_tool_steps else None,
        )
        choice = resp["choices"][0]
        msg = choice.get("message", {})
        raw_content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls or not tools:
            # Reached terminal response
            elapsed = time.perf_counter() - total_start
            return {
                "content": raw_content,
                "tool_calls": tool_calls_logged,
                "wall_clock_seconds": elapsed,
                "finish_reason": choice.get("finish_reason"),
            }

        # Handle tool calls
        messages.append(msg)
        for tc in tool_calls:
            func = tc.get("function", {})
            name = func.get("name", "unknown")
            try:
                args = json.loads(func.get("arguments") or "{}")
            except Exception:
                args = {"raw": func.get("arguments")}

            sim_res = simulate_tool_execution(item["id"], name, args)
            tool_calls_logged.append({
                "tool": name,
                "arguments": args,
                "output": sim_res,
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", f"call_{len(tool_calls_logged)}"),
                "content": sim_res,
            })

    elapsed = time.perf_counter() - total_start
    return {
        "content": raw_content,
        "tool_calls": tool_calls_logged,
        "wall_clock_seconds": elapsed,
        "finish_reason": choice.get("finish_reason"),
    }


def run_trial(
    api_url: str,
    api_key: str | None,
    model: str,
    item: dict[str, Any],
    condition_id: str,
    rag_on: bool,
    seed: int,
    *,
    conditions_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a complete scored trial, managing dual-process disagreement gate if condition == 'dual'."""
    trial_meta = {
        "item_id": item["id"],
        "domain": item["domain"],
        "condition": condition_id,
        "rag": "ON" if rag_on else "OFF",
        "seed": seed,
        "timestamp": time.time(),
    }

    allow_tools = bool(item.get("tools_allowed"))

    if condition_id != "dual":
        turn = run_single_turn(
            api_url=api_url,
            api_key=api_key,
            model=model,
            item=item,
            condition_id=condition_id,
            rag_on=rag_on,
            seed=seed,
            allow_tools=allow_tools,
            conditions_spec=conditions_spec,
        )
        grade = grade_response(item, turn["content"])
        return {
            **trial_meta,
            "conflict": None,
            "scored_draft": "single",
            "raw_response": turn["content"],
            "wall_clock_seconds": turn["wall_clock_seconds"],
            "tool_calls": turn["tool_calls"],
            "tool_used": len(turn["tool_calls"]) > 0,
            "grade": grade,
        }

    # Dual process condition:
    # 1. Sample Draft A with seed
    draft_a = run_single_turn(
        api_url=api_url,
        api_key=api_key,
        model=model,
        item=item,
        condition_id="dual",
        rag_on=rag_on,
        seed=seed,
        conflict=False,
        allow_tools=False,  # dual draft pass discourages tools
        conditions_spec=conditions_spec,
    )
    grade_a = grade_response(item, draft_a["content"])

    # 2. Sample Draft B with seed + 10_000
    draft_b = run_single_turn(
        api_url=api_url,
        api_key=api_key,
        model=model,
        item=item,
        condition_id="dual",
        rag_on=rag_on,
        seed=seed + 10_000,
        conflict=False,
        allow_tools=False,
        conditions_spec=conditions_spec,
    )
    grade_b = grade_response(item, draft_b["content"])

    # 3. Check canonical disagreement
    ans_a = grade_a.get("extracted", "")
    ans_b = grade_b.get("extracted", "")
    conflict = answers_disagree(item, ans_a, ans_b)

    if not conflict:
        # Agreement: grade draft A
        total_time = draft_a["wall_clock_seconds"] + draft_b["wall_clock_seconds"]
        return {
            **trial_meta,
            "conflict": False,
            "scored_draft": "draft_a",
            "raw_response": draft_a["content"],
            "draft_b_response": draft_b["content"],
            "wall_clock_seconds": total_time,
            "tool_calls": draft_a["tool_calls"],
            "tool_used": len(draft_a["tool_calls"]) > 0,
            "grade": grade_a,
        }

    # Conflict detected: sample Draft C using system_on_conflict (verification protocol)
    draft_c = run_single_turn(
        api_url=api_url,
        api_key=api_key,
        model=model,
        item=item,
        condition_id="dual",
        rag_on=rag_on,
        seed=seed + 20_000,
        conflict=True,
        allow_tools=allow_tools,
        conditions_spec=conditions_spec,
    )
    grade_c = grade_response(item, draft_c["content"])
    total_time = draft_a["wall_clock_seconds"] + draft_b["wall_clock_seconds"] + draft_c["wall_clock_seconds"]

    return {
        **trial_meta,
        "conflict": True,
        "scored_draft": "draft_c",
        "raw_response": draft_c["content"],
        "draft_a_response": draft_a["content"],
        "draft_b_response": draft_b["content"],
        "wall_clock_seconds": total_time,
        "tool_calls": draft_c["tool_calls"],
        "tool_used": len(draft_c["tool_calls"]) > 0,
        "grade": grade_c,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="BrainSkill confirmatory matrix runner.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help=f"Base API URL (default: {DEFAULT_API_URL})")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"), help="API key (optional)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model identifier (default: {DEFAULT_MODEL})")
    parser.add_argument("--dataset", default=str(DATASET_PATH), help="Path to dataset.json")
    parser.add_argument("--output", default="benchmark_results.jsonl", help="Path to output JSONL file")
    parser.add_argument("--conditions", nargs="+", default=["cot", "verify", "dual", "high_c"])
    parser.add_argument("--rag-states", nargs="+", default=["OFF", "ON"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--item-ids", nargs="+", default=None, help="Filter specific item IDs (e.g. d1.01 d2.01)")
    parser.add_argument("--dry-run", action="store_true", help="Print trial plan without executing requests")

    args = parser.parse_args()

    with open(args.dataset, encoding="utf-8") as f:
        dataset_data = json.load(f)
    items = dataset_data["items"]
    if args.item_ids:
        filter_set = set(args.item_ids)
        items = [it for it in items if it["id"] in filter_set]

    conditions_spec = load_conditions(CONDITIONS_PATH)

    trials_plan = []
    for it in items:
        for cond in args.conditions:
            for rag_state in args.rag_states:
                for seed in args.seeds:
                    trials_plan.append((it, cond, rag_state == "ON", seed))

    print(f"Total planned trials: {len(trials_plan)} ({len(items)} items × {len(args.conditions)} conditions × {len(args.rag_states)} RAG × {len(args.seeds)} seeds)")

    if args.dry_run:
        print("Dry run requested. Exiting without making API calls.")
        for it, cond, rag_on, seed in trials_plan[:5]:
            print(f"  Plan preview: {it['id']} | cond={cond} | RAG={'ON' if rag_on else 'OFF'} | seed={seed}")
        if len(trials_plan) > 5:
            print(f"  ... and {len(trials_plan) - 5} more trials.")
        return

    out_path = Path(args.output)
    print(f"Writing results append-only to: {out_path.resolve()}")

    completed = 0
    passed = 0
    for it, cond, rag_on, seed in trials_plan:
        print(f"[{completed + 1}/{len(trials_plan)}] Running {it['id']} | cond={cond} | RAG={'ON' if rag_on else 'OFF'} | seed={seed}...", end="", flush=True)
        try:
            result = run_trial(
                api_url=args.api_url,
                api_key=args.api_key,
                model=args.model,
                item=it,
                condition_id=cond,
                rag_on=rag_on,
                seed=seed,
                conditions_spec=conditions_spec,
            )
            correct = result["grade"]["correct"]
            if correct:
                passed += 1
            wall_time = result["wall_clock_seconds"]
            print(f" done in {wall_time:.2f}s | correct={correct} (conf={result['grade'].get('confidence')})")
            with out_path.open("a", encoding="utf-8") as out_f:
                out_f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception as exc:
            # Prereg: after retry-once inside call_chat_completion, record y=0 / parse_ok=false.
            print(f" ERROR: {exc}")
            fail_row = {
                "item_id": it["id"],
                "domain": it.get("domain"),
                "condition": cond,
                "rag": "ON" if rag_on else "OFF",
                "seed": seed,
                "timestamp": time.time(),
                "conflict": None,
                "scored_draft": "failed",
                "raw_response": "",
                "wall_clock_seconds": None,
                "tool_calls": [],
                "tool_used": False,
                "error": str(exc),
                "grade": {
                    "item_id": it["id"],
                    "correct": False,
                    "parse_ok": False,
                    "extracted": "",
                    "canonical": "",
                    "confidence": None,
                    "errors": [str(exc)],
                    "required_missing": [],
                    "forbidden_hit": [],
                },
            }
            with out_path.open("a", encoding="utf-8") as out_f:
                out_f.write(json.dumps(fail_row, ensure_ascii=False) + "\n")
        completed += 1

    print(f"\nFinished {completed} trials. Passed: {passed}/{completed} ({(passed/completed*100) if completed else 0:.1f}%)")


if __name__ == "__main__":
    main()
