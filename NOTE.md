# Scores

Rater: Grok 4.6 on the local research workstation. Method: read the tree, check cited papers, score ten axes at 100 each. Not a run of the study.

---

## v3.1 — 2026-09-09 — docs synced; full re-score pending Peđa review of WHITEPAPER

**Object:** PLAN.md v3.1 + aligned PREREG / red-team / methodology + `benchmark/run_battery.py` + WHITEPAPER.md (see below).
**What changed since v3.0:** docs now match the fact that the runner **exists** and `--dry-run` plans 1,440 trials; 9 unit tests still pass. Pre-freeze working hashes recorded for dataset / conditions / runner. WHITEPAPER.md written for review.

**On the old 716 / 1000:** that total is **outdated on the reproducibility axis** (v3.0 scored reproducibility 54 partly because `run_battery.py` was missing). Do **not** treat 716 as current. A new full 10-axis score is **pending Peđa review of WHITEPAPER.md** rather than invented precision here.

### Still honest gaps

- Domain-2 `SIMULATED_OUTPUTS` only `d2.01`–`d2.06`
- HTTP retry-once / fail-as-y=0 not in runner exception path
- No OSF freeze; no mixed-effects analysis script
- Instruction-length confound; Domain 2/4 regex construct validity
- Domain-2 tool-loop not yet timed for freeze checklist
- Study **not yet run** — no results

### Next physical work

1. Fill `d2.07`–`d2.12` sims; time one Domain-2 tool-loop dry-run.
2. Wire HTTP retry-once / fail-as-y=0.
3. Hash + OSF/Zenodo freeze; then execute the matrix.

---

## Freeze — 2026-09-09 — in-repo freeze complete

Tag `brainskill-freeze-v3.1`, see `FREEZE.md`. Domain-2 smoke 73.34 s. OSF/Zenodo registration still open. Study not run.


## v3.0 — 2026-09-09 — 716 / 1000

**Object:** PLAN.md v3.0 plus aligned PREREG, methodology, benchmark JSON, compiler, grader, SKILL.md, red-team closures.
**What changed:** one matrix, parked extra paradigms, directional hypotheses, computed dual gate, live model + timed trial, dataset.json with 60 items, denylist compiler with tests.

| Axis | /100 | Why |
| :--- | ---: | :--- |
| Thesis | 84 | Operational inductive bias vs roleplay is still the right question, now actually encoded in the compiler. |
| Construct validity | 68 | Labels stripped. Residual: longer "be careful" prompts vs CoT; regex Domain 2/4; dual is a runner policy more than a cognitive theory. |
| Experimental design | 78 | One 4×2×60×3 matrix. Four previous matrices deleted. Dual-process gate is two-draft disagreement, not `1-max P(token)`. |
| Statistical plan | 72 | Mixed-effects, item as unit, Holm family, no fake N=1400. Power is a stated assumption, not a calculation from a pilot. |
| Metrics | 66 | Accuracy + MCE + Brier + tool rate belong. TIE demoted. Verbal p still only a number in JSON. |
| Benchmark battery | 74 | 60 items exist with packets and graders. Domain 1 is real. Domain 2/4 remain keyword-ish. Not item-fuzzed beyond contract tests. |
| Controls / confounds | 78 | Blind prompts, frozen packets, dual substrate, no LLM-as-judge, freeze-after-prereg. Instruction-length confound named, not controlled. |
| Reproducibility | 54 | Compiler/grader/dataset in-tree. `run_battery.py` missing. Not OSF-frozen. |
| Feasibility | 68 | Live model is Glimmer, not Qwen3.6. `d1.01` smoke 15.035 s, answer 4.7%. Budget 8–24 h sequential. Tool-loop untimed. |
| Coherence / build-readiness | 74 | Docs agree. PLAN is complete. 9 unit tests pass. Still no runner. |
| **Total** | **716** | |

Band 600–749: runnable prereg after a coherence pass. v3 sits in that band. It is not methods-review ready (750+) because the runner, freeze, and a Domain-2 timing do not exist.

### Evidence for the feasibility axis

```
seconds: 15.035
finish: stop
chosen_action_or_answer: ≈ 4.7%
model: Muse-Glimmer-30B-exl3-2.00bpw
```

### Still not allowed

- Calling this a frozen OSF preregistration.
- Unparking Jung-16 / Luria / Friston / Sternberg inside the confirmatory ANOVA.
- Treating 1,440 rows as 1,440 items.
- Using SKILL.md named profiles as treatments.

### Next physical work

1. `benchmark/run_battery.py` (allowlisted tools, JSONL, dual gate).
2. Time one Domain-2 tool-loop dry-run.
3. Hash dataset.json + conditions.json and snapshot.

---

## v2.0 — 2026-09-09 — 512 / 1000

Historical. Object was PLAN.md v2.0 and the contradictory supporting specs. Empty `modules/`, truncated PLAN, four matrices, pseudoreplication, SKILL.md contamination, stale Qwen3.6 substrate.

Smallest path to ≥700 was: one matrix, four conditions, ≥60 items, mixed-effects, freeze dataset.json, align H1/H3, make SKILL.md the compiler, time one trial. That path is what v3 did.
