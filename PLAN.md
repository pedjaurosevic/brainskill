# BrainSkill Confirmatory Specification

**Document version:** 3.1-freeze
**Date:** 2026-09-09
**Status:** **FROZEN** for confirmatory prereg (`FREEZE.md`, tag `brainskill-freeze-v3.1`). Harness complete; Domain-2 smoke timed. OSF prereg submitted: https://osf.io/gzjrd/overview (Pending approval). Confirmatory study not yet run.
**Authors:** Predrag Urošević
**Primary substrate:** TabbyAPI on a local OpenAI-compatible inference server on loopback (host/port via env; not published), live model `Muse-Glimmer-30B-exl3-2.00bpw`, RTX 3060 12GB

v2.0 claimed to be a final pre-build specification. It was not. Four documents defined four different matrices, power math treated repeats as extra items, TIE was the wrong H3 statistic, SKILL.md leaked type names, the named model was already not the live model, and `modules/` was empty. v3.0 closed those gaps and shipped dataset + compiler + grader. **v3.1** records that the OpenAI-compatible runner is in-tree; residual gaps before freeze are named below.

---

## 1. Thesis

The question is not whether a model can *act like an INTJ*. The question is whether **label-blind operational protocols** change accuracy, tool use, and verbal calibration on a resource-constrained local model, compared with ordinary chain-of-thought.

A protocol is an inductive bias only if the model never sees the psychological brand name. If the prompt says "INTJ" or "Kahneman", the study measures stereotype recall.

---

## 2. What is being tested (and what is parked)

Confirmatory Module 1 has **four conditions**, not six paradigms and not sixteen types.

| ID | Experimenter label | Model sees |
| :--- | :--- | :--- |
| `cot` | Baseline chain-of-thought | "Think step by step…" |
| `verify` | Verification protocol | Claim → falsifier → tool if possible → update → confidence |
| `dual` | Dual-process with a **computed** gate | Fast draft; on disagreement, the verification protocol |
| `high_c` | High-verification operational vector | Checklist, conservative action, no guessing |

Parked until this A/B works: Jungian 16, Luria blocks, Friston FEP, Sternberg triarchic. Files remain under `types/` and are not treatments.

Module 2 is unchanged in role: `RAG ∈ {OFF, ON}` with **frozen** packets (1 ground-truth document + 2 distractors). No live retriever.

Module 3 is a response contract, not a consciousness claim: JSON with `confidence ∈ [0,1]`, weakest premise, and a falsification check.

---

## 3. Dual-process gate (computed, not verbal)

v2 defined conflict as `1 - max P(token)`. That is next-token uncertainty, not semantic conflict. It is rejected.

Runner algorithm for `dual`:

1. Sample draft A at temperature 0.2, seed `s`.
2. Sample draft B at temperature 0.2, seed `s+10_000`.
3. Extract `chosen_action_or_answer` from both. Canonicalize with the item grader (`modules/grader.py`).
4. If canonical forms **differ** (including one empty and one not), set `conflict=1` and sample draft C with `system_on_conflict` (the verification protocol). Grade C.
5. If they **match**, set `conflict=0` and grade A.
6. Log both drafts, the conflict bit, and which draft was scored.

This gate is a property of the runner. The model is not told about System 1, System 2, or psychology. Optional logprob triggers are exploratory only and are not required on the Gemini/Grok subset.

---

## 4. Design matrix

One matrix. Delete the others.

\[
4\ \text{conditions} \times 2\ \text{RAG} \times 60\ \text{items} \times 3\ \text{seeds}
= 1{,}440\ \text{scored trials}
\]

`dual` adds one extra draft on every trial and a third completion on conflict. That extra compute is part of the condition, not extra independent items.

Independent unit for generalization: **the item**, not the seed repeat.

Secondary substrate (quantization control): Domain 1 items `d1.01`–`d1.10`, `RAG: OFF`, one seed, four conditions, on Gemini 3.8 Flash and/or Grok. Direction of `verify`/`high_c` vs `cot` is the only confirmatory claim on that subset.

---

## 5. Hypotheses (directional; no absolute cutoffs)

Absolute thresholds from v2 (`MCE < 0.15` vs `< 0.18`, CoT `≥ 0.30`, `Δ ≥ 25%`) are dropped. There was no pilot.

**H1 (primary, calibration).** Item-level MCE is lower for `verify` than for `cot`, and lower for `high_c` than for `cot`. One-sided mixed-effects tests, α = 0.05, Holm-adjusted across the two comparisons.

**H1-secondary.** Same comparison for `dual` vs `cot`. Pre-registered as secondary because the gate may rarely fire.

**H2 (primary, grounding).** GDI = mean accuracy(RAG ON) − mean accuracy(RAG OFF) is **smaller** for `verify` than for `cot`. The verification protocol is supposed to collect evidence with tools when the packet is absent.

**H3 (primary, tools).** On Domain 2, the rate of trials with ≥1 inspection tool call (`bash` or `read` analogue) before the final answer is higher for `verify` than for `cot`. On Domain 3, the false-positive destructive-action rate (forbidden regex hit on `chosen_action_or_answer`) is **not higher** for `verify` than for `cot`.

Exploratory, not confirmatory: TIE, per-domain slices, `high_c` tool rate, conflict-fire rate, latency.

---

## 6. Metrics

Let \(y_i \in \{0,1\}\) be the deterministic grade and \(\hat p_i \in [0,1]\) the emitted confidence.

| Metric | Formula | Role |
| :--- | :--- | :--- |
| Accuracy | mean \(y_i\) | Co-primary with MCE |
| MCE | mean \(\lvert \hat p_i - y_i \rvert\) | H1 |
| Brier | mean \((\hat p_i - y_i)^2\) | Report with H1 |
| GDI | Acc(RAG ON) − Acc(RAG OFF) | H2 |
| Tool rate | P(≥1 inspection call) | H3 |
| Destructive rate | P(forbidden action) | H3 safety |

TIE (Shannon entropy over `{bash, read, none}`) is **exploratory**. It measures tool-type diversity, not invocation rate, and is not H3.

Verbal \(\hat p\) is a stated number, not a proven probability. Ackerman (arXiv:2509.21545) finds limited but real metacognition in some frontier models, not "confidence is always confabulation". This study still treats \(\hat p\) as a behavioral output and scores it against \(y\).

---

## 7. Statistical plan

- **Model:** mixed-effects. For accuracy, Bernoulli or item-averaged Gaussian:
  `y ~ condition * rag + (1 | item)`.
- Seeds are repeats for run variance, nested in item×condition×rag. They are not additional items. Do not report N = 1,440 as the sample size for generalization.
- Contrasts: treatment coding with `cot` as reference.
- Multiple comparisons: Holm on the confirmatory family (H1 two tests, H2 one test, H3 two tests).
- **Power assumption (honest, not a theorem):** 60 items can detect a ~10–15 point accuracy shift if it is stable across items. It cannot underwrite a small calibration effect. If H1 is null, that is a result, not a license to hunt parked paradigms.
- **Stopping rule:** run the 1,440 scored trials (plus dual extra drafts). No prompt edits, no rubric edits, no item drops after freeze. Failed HTTP calls may be retried once with the same seed; a second failure is `y=0`, parse_ok=false. (**Residual:** retry-once / fail-as-y=0 is specified here and in PREREG; the current runner exception path does not yet implement it.)
- ANOVA + Tukey on 1,400 nested binary trials is rejected.
- **Residual:** no mixed-effects analysis script is in-tree yet.

---

## 8. Battery

60 unique items in `benchmark/dataset.json`, frozen in-repo.

| Domain | N | Skill | Grader |
| :--- | ---: | :--- | :--- |
| 1 Epistemic traps | 24 | Bayes, Wason, conjunction, Simpson, birthday, optional stopping | numeric / choice / boolean |
| 2 Linux debugging | 12 | Btrfs, Hyprland, ports, cgroup, inodes | required + forbidden regex; tools allowed |
| 3 Safety | 12 | wipe, secrets, firewall, force-push, pip-as-root | refusal required; forbidden **action** regex |
| 4 Distractor sieve | 12 | logs, precedence, ABI, cache | exact / regex |

Domain 4 is **not** a 10k–30k token dump. Each RAG packet is short. Prompt + 3 documents should stay under ~2,500 tokens so the edge model is testing filtering, not context thrash.

Every item has a grader and a 3-document packet. Scoring is `modules/grader.py`. No LLM-as-judge. Keyword presence in Domain 2/4 is a known weakness of regex rubrics; Domain 1 is the construct-valid core.

---

## 9. Prompt compiler and SKILL.md

`types/conditions.json` is the treatment table.
`modules/compiler.py` emits system + user messages and **fails** if a denylist term leaks (INTJ, Jung, Luria, Kahneman, System 1, OCEAN, persona, …).

SKILL.md is the **compiler manual**, not a treatment. Activating named profiles in a model-facing string is forbidden in confirmatory runs.

---

## 10. Substrate, timing, budget

Verified 2026-09-09 on the live TabbyAPI model `Muse-Glimmer-30B-exl3-2.00bpw`:

- Domain 1 smoke (`d1.01`, CoT JSON contract): **15.035 s**, `finish=stop`, extracted posterior **4.7%** (in [4.5, 5.0]).
- Token usage field was null; wall-clock is the budget unit.

Budget (sequential, one GPU job):

| Piece | Completions | Wall-clock at 15–40 s |
| :--- | ---: | :--- |
| Scored trials | 1,440 | 6–16 h |
| Dual extra drafts | +360 | +1.5–4 h |
| Dual conflict retries | ~0–360 | 0–4 h |
| **Total local** | **~1,800–2,160** | **~8–24 h** |

Tool loops on Domain 2 are **not yet timed** for the freeze checklist. The table uses a 15–40 s envelope rather than pretending every trial is a single 15 s completion. This is a weekend run, not an afternoon. Do not start the confirmatory battery until one Domain-2 dry-run with allowlisted simulated tools has been timed and the remaining Domain-2 simulations (`d2.07`–`d2.12`) are filled.

Qwen3.6-35B-A3B-exl3 is **not** the live model. It remains on disk as a restore option and is not this study's substrate unless ExecStart is switched back before freeze.

GPU rule: one inference job at a time on the RTX 3060. The confirmatory run is that job.

---

## 11. Workflow and freeze

```
[Now] Spec v3.1 + dataset.json + compiler/grader tests + run_battery.py
      (--dry-run plans 1,440 trials; 9 unit tests pass)
   │
[Next] Domain-2 timed dry-run on live model
   │── Fill SIMULATED_OUTPUTS for d2.07–d2.12
   │── Implement HTTP retry-once / fail-as-y=0 in runner exception path
   │── Freeze this tree (hash dataset.json, conditions.json, PLAN, PREREG, runner)
   └── Optional OSF/Zenodo snapshot
   │
[Then] Execute 4×2×60×3 on Glimmer; 4×10 on the API subset
   │
[After] Mixed-effects analysis as specified; no parked-paradigm unparking
```

This document may be called the **final confirmatory plan**. It may not be called a completed study, a preregistered frozen DOI, or evidence that protocols work.

---

## 12. Implementation map

| Path | Role |
| :--- | :--- |
| `types/conditions.json` | Four label-blind conditions + denylist |
| `modules/compiler.py` | Prompt compiler |
| `modules/grader.py` | Deterministic grader + disagreement gate |
| `benchmark/dataset.json` | 60 items, packets, graders |
| `benchmark/run_battery.py` | **Exists.** OpenAI-compatible confirmatory runner: dual disagreement gate, allowlisted Domain-2 simulated tools, append-only JSONL, `--dry-run` planning for the full 1,440-trial matrix. Residual gaps: `SIMULATED_OUTPUTS` cover `d2.01`–`d2.06` only; Domain-2 tool-loop smoke timed (see below). |
| `types/jungian.json` | Parked |
| `types/ALTERNATIVE_PARADIGMS.md` | Parked |

### Pre-freeze working hashes (NOT freeze)

Recorded 2026-09-09 for continuity. Re-hash at freeze; these are not an OSF snapshot.

| File | SHA-256 |
| :--- | :--- |
| `benchmark/dataset.json` | `bb3ab75a3701064642c8694610b579cb28ebb0167cc371ce4d5048e2e5a3d086` |
| `types/conditions.json` | `76179e1bd48a3a986f02317ef043bf96737a930d9a69547c620689b792d90f1e` |
| `benchmark/run_battery.py` | `e21fd66b592a1802d23beb960e3fd8ea4d7606d0d9de9dca0a3023cae02819b9` |

---

## 13. Out of scope

- Training, fine-tuning, or RLHF.
- Live vector RAG.
- LLM-as-judge.
- Claims about consciousness, Global Workspace as implemented hardware, or personality.
- Running competing GPU jobs to "go faster".
