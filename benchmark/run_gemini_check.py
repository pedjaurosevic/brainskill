#!/usr/bin/env python3
"""Run secondary substrate validation on Gemini Flash.

Preregistered protocol:
Items: d1.01–d1.10 (first 10 items of Domain 1: Thinking traps)
Conditions: cot, verify, dual, high_c
RAG: OFF
Seed: 42
Model: gemini-flash-latest via Google AI Studio OpenAI-compatible endpoint
Output: results/battery_gemini_flash.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Ensure brainskill root is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.compiler import compile_messages, load_conditions  # noqa: E402
from modules.grader import answers_disagree, grade_response  # noqa: E402

DEFAULT_DATASET = SCRIPT_DIR / "dataset.json"
DEFAULT_CONDITIONS = ROOT_DIR / "types" / "conditions.json"
DEFAULT_OUTPUT = ROOT_DIR / "results" / "battery_gemini_flash.jsonl"
GOOGLE_OPENAI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


def get_api_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    env_file = Path("/home/peterofovik/.env")
    if env_file.exists():
        with env_file.open(encoding="utf-8") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
                    return line.strip().split("=", 1)[1].strip("\"'")
    raise RuntimeError("GOOGLE_API_KEY not found in environment or /home/peterofovik/.env")


def call_gemini(
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.2,
    timeout: int = 40,
    max_retries: int = 3,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(GOOGLE_OPENAI_URL, data=body, headers=headers)
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries:
                time.sleep(5 * attempt)
                continue
            raise
        except Exception:
            if attempt < max_retries:
                time.sleep(2 * attempt)
                continue
            raise
    raise RuntimeError("Max retries exceeded")


def main() -> None:
    parser = argparse.ArgumentParser(description="Secondary Gemini Flash Direction Check.")
    parser.add_argument("--model", default="gemini-flash-latest", help="Google model identifier")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSONL path")
    args = parser.parse_args()

    api_key = get_api_key()
    with DEFAULT_DATASET.open(encoding="utf-8") as f:
        dataset_data = json.load(f)
    items = [it for it in dataset_data["items"] if it["id"] in [f"d1.{i:02d}" for i in range(1, 11)]]

    conditions_spec = load_conditions(DEFAULT_CONDITIONS)
    conditions = ["cot", "verify", "dual", "high_c"]

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

    print(f"Starting Gemini Flash check: {len(items)} items × {len(conditions)} conditions = {len(items)*len(conditions)} trials")
    print(f"Model: {args.model}")
    print(f"Output: {out_path}")

    results = []
    trial_idx = 0
    total_trials = len(items) * len(conditions)

    for it in items:
        for cond in conditions:
            trial_idx += 1
            print(f"[{trial_idx}/{total_trials}] Running {it['id']} | cond={cond}...", end="", flush=True)
            t0 = time.time()

            try:
                if cond != "dual":
                    messages = compile_messages(
                        condition_id=cond,
                        user_prompt=it["prompt"],
                        rag_on=False,
                        conditions=conditions_spec,
                    )
                    raw_content = call_gemini(api_key, args.model, messages)
                    grade = grade_response(it, raw_content)
                    elapsed = time.time() - t0
                    res = {
                        "item_id": it["id"],
                        "domain": it["domain"],
                        "condition": cond,
                        "rag": "OFF",
                        "seed": 42,
                        "model": args.model,
                        "raw_response": raw_content,
                        "wall_clock_seconds": elapsed,
                        "grade": grade,
                    }
                else:
                    # Dual process: Draft A and Draft B
                    messages_a = compile_messages("dual", it["prompt"], rag_on=False, conditions=conditions_spec)
                    raw_a = call_gemini(api_key, args.model, messages_a)
                    grade_a = grade_response(it, raw_a)
                    time.sleep(0.5)

                    raw_b = call_gemini(api_key, args.model, messages_a)
                    grade_b = grade_response(it, raw_b)

                    conflict = answers_disagree(it, grade_a.get("extracted", ""), grade_b.get("extracted", ""))
                    if not conflict:
                        elapsed = time.time() - t0
                        res = {
                            "item_id": it["id"],
                            "domain": it["domain"],
                            "condition": "dual",
                            "rag": "OFF",
                            "seed": 42,
                            "model": args.model,
                            "conflict": False,
                            "scored_draft": "draft_a",
                            "raw_response": raw_a,
                            "draft_b_response": raw_b,
                            "wall_clock_seconds": elapsed,
                            "grade": grade_a,
                        }
                    else:
                        messages_c = compile_messages("dual", it["prompt"], rag_on=False, conflict=True, conditions=conditions_spec)
                        raw_c = call_gemini(api_key, args.model, messages_c)
                        grade_c = grade_response(it, raw_c)
                        elapsed = time.time() - t0
                        res = {
                            "item_id": it["id"],
                            "domain": it["domain"],
                            "condition": "dual",
                            "rag": "OFF",
                            "seed": 42,
                            "model": args.model,
                            "conflict": True,
                            "scored_draft": "draft_c",
                            "raw_response": raw_c,
                            "draft_a_response": raw_a,
                            "draft_b_response": raw_b,
                            "wall_clock_seconds": elapsed,
                            "grade": grade_c,
                        }

                with out_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(res, ensure_ascii=False) + "\n")
                results.append(res)
                corr = res["grade"]["correct"]
                conf = res["grade"].get("confidence")
                print(f" done in {elapsed:.2f}s | correct={corr} (conf={conf})")
            except Exception as exc:
                print(f" ERROR: {exc}")

            time.sleep(0.8)  # respectful rate limiting

    print("\n=== GEMINI FLASH SUMMARY ===")
    by_cond = {}
    for r in results:
        c = r["condition"]
        by_cond.setdefault(c, []).append((r["grade"]["correct"], r["grade"].get("confidence", 0.5)))

    for c, vals in sorted(by_cond.items()):
        acc = sum(1 for corr, _ in vals if corr) / len(vals)
        mce = sum(abs(p - (1.0 if corr else 0.0)) for corr, p in vals) / len(vals)
        print(f"{c:7s}: Acc={acc:.3f} ({sum(1 for corr, _ in vals if corr)}/{len(vals)}), MCE={mce:.3f}")


if __name__ == "__main__":
    main()
