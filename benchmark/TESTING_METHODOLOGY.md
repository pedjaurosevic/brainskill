# BrainSkill Testing Methodology

**Document version:** 3.1
**Matches:** PLAN.md v3.1
**Substrate:** TabbyAPI on a local OpenAI-compatible inference server on loopback (host/port via env; not published), live id `Muse-Glimmer-30B-exl3-2.00bpw`

---

## 1. Objectives

Measure whether label-blind operational protocols change:

1. Accuracy under deterministic graders.
2. Verbal calibration (MCE, Brier).
3. Inspection-tool use on debugging items.
4. Destructive-action rate on safety items.
5. Dependence on a frozen evidence packet (GDI).

---

## 2. Matrix (the only one)

4 conditions × 2 RAG × 60 items × 3 seeds.

| Condition | Source |
| :--- | :--- |
| `cot` | `types/conditions.json` |
| `verify` | same |
| `dual` | same; runner disagreement gate |
| `high_c` | same |

There is no 16×2 Jungian matrix in the confirmatory study. Roleplay ("You are an INTJ genius") is not a baseline here; it would reintroduce stereotype priming. If someone wants it later, it is an exploratory extra, not Factor 1.

Fixed decoding: temperature 0.2, top_p 0.9, named seeds.

---

## 3. Battery

`benchmark/dataset.json` (60 items). Inventory:

- Domain 1: 24 checkable epistemic traps.
- Domain 2: 12 Linux/Omarchy debugging items, tools allowed.
- Domain 3: 12 safety refusals.
- Domain 4: 12 short-context sieves.

Domain 4 packets are short. Do not expand them to 10k–30k tokens without a new prereg.

---

## 4. Metrics

See PLAN.md §6. Confirmatory: accuracy, MCE, Brier, GDI, Domain-2 tool rate, Domain-3 forbidden-action rate. TIE is exploratory.

MCE is mean absolute error of the emitted `calibration.confidence` against the binary grade. It is not ECE unless we later bin; binning is exploratory.

---

## 5. Pipeline (built)

`benchmark/run_battery.py` **exists**. It is an OpenAI-compatible confirmatory runner with dual disagreement gate, allowlisted Domain-2 simulated tools, append-only JSONL logging, and `--dry-run` that plans the full 1,440-trial matrix without HTTP calls. Compiler and grader remain unit-tested (`python3 -m unittest modules.test_compiler` — 9 pass).

Actual steps per scored trial:

1. Load item `S` from `dataset.json`.
2. `compile_messages(condition, prompt, rag_on, packet)` via `modules/compiler.py` (denylist enforced).
3. POST `/v1/chat/completions` to TabbyAPI (or configured OpenAI-compatible base).
4. For `dual`, sample two drafts (seeds `s` and `s+10000`), canonicalize, escalate with `system_on_conflict` on disagreement; grade the chosen draft.
5. On Domain 2, allowlisted tools only (`bash_inspect`, `read_file`); execute against `SIMULATED_OUTPUTS`; log every call.
6. `grade_response(item, text)` via `modules/grader.py` (deterministic; no LLM-as-judge).
7. Append one JSONL row per scored trial (`--output`).

### Known gaps in the built pipeline

- `SIMULATED_OUTPUTS` currently cover **`d2.01`–`d2.06` only**; `d2.07`–`d2.12` fall through to a generic stub.
- HTTP **retry-once / fail-as-y=0** from PREREG is **not** yet wired in the runner exception path.
- Domain-2 tool-loop wall-clock not yet timed for the freeze checklist.
- No mixed-effects analysis script yet. Study not yet executed.
