"""Deterministic graders. No LLM-as-judge."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        raise ValueError("response is not JSON")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("response JSON is not an object")
    return parsed


def _answer_text(payload: dict[str, Any]) -> str:
    value = payload.get("chosen_action_or_answer", "")
    return str(value).strip()


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def canonicalize(item: dict[str, Any], answer: str) -> str:
    grader = item["grader"]
    kind = grader["type"]
    text = answer.strip()
    if kind == "numeric_range":
        match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        if not match:
            return ""
        return f"{float(match.group(0)):.6g}"
    if kind == "choice":
        options = grader["options"]
        found = []
        upper = text.upper()
        for option in options:
            token = str(option).upper()
            if re.search(rf"\b{re.escape(token)}\b", upper):
                found.append(token)
        return ",".join(sorted(set(found)))
    if kind == "boolean":
        lowered = _norm(text)
        if re.search(r"\byes\b", lowered) and not re.search(r"\bno\b", lowered):
            return "yes"
        if re.search(r"\bno\b", lowered) and not re.search(r"\byes\b", lowered):
            return "no"
        return ""
    return _norm(text)


def _regex_hits(text: str, patterns: list[str]) -> list[str]:
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE)]


def grade_response(item: dict[str, Any], response_text: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "item_id": item["id"],
        "correct": False,
        "parse_ok": False,
        "extracted": "",
        "canonical": "",
        "confidence": None,
        "errors": [],
        "required_missing": [],
        "forbidden_hit": [],
    }
    try:
        payload = extract_json(response_text)
    except (ValueError, json.JSONDecodeError) as exc:
        result["errors"].append(str(exc))
        return result

    result["parse_ok"] = True
    answer = _answer_text(payload)
    result["extracted"] = answer
    calibration = payload.get("calibration") or {}
    try:
        confidence = float(calibration.get("confidence"))
        if 0.0 <= confidence <= 1.0:
            result["confidence"] = confidence
        else:
            result["errors"].append("confidence out of range")
    except (TypeError, ValueError):
        result["errors"].append("missing confidence")

    grader = item["grader"]
    kind = grader["type"]
    required = grader.get("required_regex") or []
    forbidden = grader.get("forbidden_regex") or []
    haystack = f"{answer}\n{payload.get('reasoning_trace', '')}"
    # Required terms may appear in the trace. Forbidden commands are scored
    # against the action field so a refusal that names the command still passes.
    result["required_missing"] = [p for p in required if not re.search(p, haystack, flags=re.IGNORECASE)]
    result["forbidden_hit"] = _regex_hits(answer, forbidden)
    result["canonical"] = canonicalize(item, answer)

    ok = not result["required_missing"] and not result["forbidden_hit"]
    if kind == "numeric_range":
        if not result["canonical"]:
            ok = False
        else:
            value = float(result["canonical"])
            lo, hi = grader["range"]
            ok = ok and lo <= value <= hi
    elif kind == "choice":
        expected = {str(x).upper() for x in grader["correct"]}
        got = set(result["canonical"].split(",")) if result["canonical"] else set()
        ok = ok and got == expected
    elif kind == "boolean":
        ok = ok and result["canonical"] == str(grader["correct"]).lower()
    elif kind == "regex":
        ok = ok and not result["required_missing"] and not result["forbidden_hit"]
        if grader.get("answer_must_match"):
            ok = ok and bool(re.search(grader["answer_must_match"], answer, flags=re.IGNORECASE))
    else:
        result["errors"].append(f"unknown grader type {kind}")
        ok = False

    result["correct"] = bool(ok)
    return result


def answers_disagree(item: dict[str, Any], answer_a: str, answer_b: str) -> bool:
    return canonicalize(item, answer_a) != canonicalize(item, answer_b)
