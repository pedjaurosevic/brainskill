---
name: brainskill
description: Label-blind prompt compiler for the BrainSkill confirmatory study. Builds operational protocols (chain-of-thought, verification, dual-process escalation, high-verification checklist) without psychological brand names. Use when compiling BrainSkill conditions or checking that a model-facing prompt stays on the denylist.
---

# BrainSkill compiler skill

This file is the **compiler manual**. It is not a treatment and not a persona pack.

Confirmatory runs load `types/conditions.json` through `modules/compiler.py`. The model receives only operational instructions plus the JSON response contract. Type names, Jung, Luria, Kahneman, System 1/2, OCEAN, and "act like" are denylisted.

## Conditions

| ID | What the compiler emits |
| :--- | :--- |
| `cot` | Think step by step. |
| `verify` | Claim, falsifier, tool if possible, update, calibrated confidence. |
| `dual` | Fast draft; on runner-detected disagreement, the verification protocol. |
| `high_c` | Checklist, conservative action, no guessing. |

`dual`'s gate is computed by the runner (two canonicalized answers). Do not describe gears or dual-process theory in the prompt.

## Response contract

```json
{
  "reasoning_trace": "string",
  "chosen_action_or_answer": "string",
  "calibration": {
    "confidence": 0.0,
    "weakest_premise": "string",
    "falsification_check": "string"
  }
}
```

## Grounding

- Local inferences: TabbyAPI on a local OpenAI-compatible inference server on loopback (host/port via env; not published). Live model is whatever `/v1/models` reports; as of 2026-09-09 that is `Muse-Glimmer-30B-exl3-2.00bpw`.
- RAG ON injects the frozen 3-document packet. RAG OFF does not.
- Never fabricate tool output. When the protocol requires a check, call a real tool or lower confidence.

## Explicitly forbidden in confirmatory strings

Do not activate `INTJ` or any profile from `types/jungian.json` as a model-facing prefix. That file is parked. If a product wants named profiles later, it is a different artifact from this study.
