# Preregistration Protocol: BrainSkill Study

**Title:** Label-blind operational protocols vs chain-of-thought on an edge LLM
**Registry target:** OSF / Zenodo (tree frozen; upload pending)
**Date of this draft:** 2026-09-09
**Status:** Tree **FROZEN** (`FREEZE.md`, tag `brainskill-freeze-v3.1`). OSF preregistration submitted: https://osf.io/gzjrd/overview (Pending approval). Project: https://osf.io/p9tcy/. Not a DOI yet. Confirmatory battery not run.

This file must match `PLAN.md` v3.1-freeze. If they diverge, PLAN.md wins until both are edited together.

---

## 1. Study information

### 1.1 Authors
Predrag Urošević (local research workstation)

### 1.2 Research questions
1. Do label-blind verification and high-verification protocols reduce verbal calibration error relative to chain-of-thought on a 2.00 bpw local model?
2. Does the verification protocol shrink the accuracy gap between frozen-packet RAG ON and RAG OFF?
3. On debugging items, does verification raise inspection-tool use without raising destructive actions on safety items?

---

## 2. Confirmatory hypotheses

- **H1:** Item-level MCE(`verify`) < MCE(`cot`) and MCE(`high_c`) < MCE(`cot`). One-sided, Holm-adjusted.
- **H1-secondary:** MCE(`dual`) < MCE(`cot`).
- **H2:** GDI(`verify`) < GDI(`cot`), where GDI = Acc(RAG ON) − Acc(RAG OFF).
- **H3:** On Domain 2, P(tool | `verify`) > P(tool | `cot`). On Domain 3, P(forbidden action | `verify`) ≤ P(forbidden action | `cot`) as a non-inferiority/descriptive companion: the confirmatory claim is that tool-rate gains are not bought with extra destructive actions. Report both rates; treat a higher destructive rate as a failed H3 even if tools increase.

No absolute MCE cutoffs. No 2× invocation rule as a hard number; the test is directional.

---

## 3. Design

4 conditions (`cot`, `verify`, `dual`, `high_c`) × 2 RAG × 60 items × 3 seeds.

Factor 1 is **not** seven paradigms. Jung / Luria / Friston / Sternberg are parked.

Blinding: model-facing strings are compiled from `types/conditions.json` and must pass the denylist. Experimenter labels never go to the model.

RAG ON uses the frozen packet on each item (1 true + 2 distractors). RAG OFF omits the packet. Tools remain available on Domain 2 in both RAG states.

`dual` gate: two drafts, canonicalize, escalate on disagreement (`PLAN.md` §3). Implemented in `benchmark/run_battery.py`.

---

## 4. Sampling, substrate, budget

- Battery: `benchmark/dataset.json` (60 items).
- Seeds: 3 per cell, temperature 0.2, top_p 0.9.
- Primary model: live TabbyAPI `Muse-Glimmer-30B-exl3-2.00bpw` on a local OpenAI-compatible inference server on loopback (host/port via env; not published).
- Timed smoke 2026-09-09: Domain 1 item `d1.01`, 15.035 s, answer 4.7%.
- Domain-2 tool-loop smoke 2026-09-09: `d2.01` cot RAG OFF seed 42, **73.34 s**, correct, 3 tool calls.
- Expected local wall-clock: 8–24 h sequential including dual extra drafts.
- Secondary: items `d1.01`–`d1.10`, RAG OFF, one seed, four conditions, Gemini 3.8 Flash and/or Grok.

Do not describe 1,440 rows as 1,440 independent items.

---

## 5. Analysis and stopping

- Mixed-effects with item as random intercept. Seeds are repeats.
- Primary metrics: accuracy, MCE, Brier, GDI, Domain-2 tool rate, Domain-3 forbidden-action rate.
- TIE is exploratory.
- α = 0.05, Holm on the confirmatory family.
- Stop after the planned trials. No rubric or prompt edits after freeze.
- One HTTP retry per trial; second failure scores y = 0. (**Specified; not yet implemented in the runner exception path.**)
- Mixed-effects analysis script is not yet in-tree.

---

## 6. Freeze checklist (all required)

1. `modules` compiler/grader tests pass. (**Done:** `python3 -m unittest modules.test_compiler` — 9 pass.)
2. `benchmark/dataset.json` hash recorded in the OSF snapshot. (Working hash exists in PLAN.md §12; not an OSF freeze.)
3. One Domain-2 tool-loop dry-run timed on the live model with allowlisted fake tools. (**Still required;** runner exists, timing not yet recorded.)
4. Live `/v1/models` id still matches the named substrate, or the name is updated before freeze.
5. Upload PLAN.md, this file, conditions.json, dataset.json, compiler, grader, and `run_battery.py`.
6. Domain-2 `SIMULATED_OUTPUTS` complete for `d2.01`–`d2.12` (currently `d2.01`–`d2.06` only).
7. HTTP retry-once / fail-as-y=0 wired in the runner exception path.
