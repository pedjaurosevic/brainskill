"""Label-blind prompt compiler. Never emit psychological names to the model."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONDITIONS_PATH = ROOT / "types" / "conditions.json"


def load_conditions(path: Path | None = None) -> dict[str, Any]:
    target = path or CONDITIONS_PATH
    with target.open(encoding="utf-8") as handle:
        return json.load(handle)


def _contains_denied(text: str, denylist: list[str]) -> str | None:
    lowered = text.lower()
    for term in denylist:
        if re.search(re.escape(term.lower()), lowered):
            return term
    return None


def assert_blind(text: str, denylist: list[str], where: str) -> None:
    hit = _contains_denied(text, denylist)
    if hit:
        raise ValueError(f"psychological keyword {hit!r} leaked in {where}")


def format_rag_packet(packet: dict[str, Any], preamble: str) -> str:
    docs = [packet["ground_truth"], *packet.get("distractors", [])]
    blocks = [preamble, ""]
    for index, doc in enumerate(docs, start=1):
        title = doc.get("title", f"Document {index}")
        body = doc.get("text", "")
        blocks.append(f"[Document {index}: {title}]\n{body}")
        blocks.append("")
    return "\n".join(blocks).strip()


def compile_messages(
    condition_id: str,
    user_prompt: str,
    *,
    rag_on: bool = False,
    rag_packet: dict[str, Any] | None = None,
    conflict: bool = False,
    conditions: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    spec = conditions or load_conditions()
    denylist = spec["denylist"]
    condition = spec["conditions"][condition_id]
    if condition_id == "dual" and conflict:
        system_core = condition["system_on_conflict"]
        where = f"{condition_id}.system_on_conflict"
    else:
        system_core = condition["system"]
        where = f"{condition_id}.system"

    system = f"{system_core}\n\n{spec['shared_suffix']}"
    assert_blind(system, denylist, where)
    assert_blind(user_prompt, denylist, "user_prompt")

    user = user_prompt
    if rag_on:
        if not rag_packet:
            raise ValueError("RAG ON requires a frozen rag_packet")
        packet_text = format_rag_packet(packet=rag_packet, preamble=spec["rag_preamble"])
        assert_blind(packet_text, denylist, "rag_packet")
        user = f"{packet_text}\n\n---\n\n{user_prompt}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
