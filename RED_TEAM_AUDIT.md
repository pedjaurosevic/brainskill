# BrainSkill Red-Team Audit

**Document version:** 2.1 (v1 findings kept; v3 closures added; v3.1 runner status)
**Date:** 2026-09-09

---

## 1. Original five vulnerabilities (still the right attacks)

### V1 Stereotype priming
If the prompt says INTJ / Luria / Kahneman, the model retrieves pop-psychology, not an algorithm.

### V2 Power
N = 20 items with 5 seeds is not N = 100. Repeats measure run variance.

### V3 LLM-as-judge
Open debugging/safety text cannot be graded by another LLM without circular bias.

### V4 Quantization
A 2.00–2.08 bpw edge model can fail a protocol because the weights are crushed, not because the protocol is empty.

### V5 Retriever variance
Live FAISS/Chroma would confound reasoning with retrieval luck.

---

## 2. Extra v2 failures the first audit missed

6. Four documents, four matrices (6×2 vs 7 conditions vs 16 stacks vs 20×5).
7. Absolute MCE cutoffs with no pilot, and H1 numbers that disagreed across files.
8. TIE (entropy over tool types) used as H3 while H3 was an invocation-rate claim.
9. Dual-process "conflict" defined as `1 - max P(token)`.
10. SKILL.md was itself a named-profile treatment.
11. Empty `modules/`, truncated PLAN, live model already not Qwen3.6.
12. Literature: Ackerman was flattened to "confidence is confabulation"; Courchaine's arXiv id `2608.15400` was not the paper (WWW Companion 2026 PDF, no such arXiv).

---

## 3. v3 / v3.1 closures

| Attack | Closure | Residual |
| :--- | :--- | :--- |
| V1 priming | Denylist compiler; conditions.json has no type names | Residual: protocol wording may still look like "be careful" and help via generic instruction-following |
| V2 power | 60 items; mixed-effects; seeds are repeats | 60 is modest; small calibration effects may be undetectable |
| V3 judge | `modules/grader.py` only | Domain 2/4 regexes still keyword-ish |
| V4 quant | Dual substrate: 10 Domain-1 items on Gemini/Grok | Direction-only; not a full replication |
| V5 retriever | Frozen 1+2 packets | Packets can still *contain* the answer; RAG ON is an open-book sieve, not a search test |
| Multiple matrices | One 4×2×60×3 matrix | Parked paradigms must stay parked |
| Absolute cutoffs | Directional tests | No promised MCE number |
| TIE as H3 | Tool *rate* + destructive rate | TIE exploratory |
| Fake conflict | Two-draft canonical disagreement | Extra cost; gate may rarely fire |
| SKILL.md contamination | Compiler manual, not treatment | Product-mode named profiles would be a different study |
| Empty harness / `run_battery` missing | **Runner exists** (`benchmark/run_battery.py`): OpenAI-compatible client, dual gate, allowlisted simulated tools, JSONL, `--dry-run` plans 1,440 | Residual: Domain-2 sims only `d2.01`–`d2.06`; no HTTP retry-once / fail-as-y=0 on exception path; no OSF freeze yet; Domain-2 tool-loop not timed |
| Stale model | Live id Glimmer, timed 15.035 s | Must re-check `/v1/models` at freeze |
| Literature | PAPERS.md corrected | Library is still thin |

---

## 4. Attacks that remain open

- **Instruction length confound.** `verify` and `high_c` prompts are longer than `cot`. A longer "be careful" baseline would be a better control and is not in this matrix. Flag as a limitation; do not add it post-freeze.
- **Regex construct validity** on Domain 2/4. Domain 1 carries the scientific load.
- **Incomplete Domain-2 tool simulation & timing.** Runner is present, but half the Domain-2 sims and a timed tool-loop dry-run are still missing before freeze.
- **HTTP retry policy gap.** Prereg specifies retry-once then y=0; current runner exception path does not yet implement it.
- **Verbal p.** Emitted confidence may not track any internal signal on this 2.00 bpw model.
- **No freeze / no analysis script.** Spec completeness + harness ≠ executed, analyzed study.

Do not declare the study reviewer-proof. Declare the matrix coherent and the remaining attacks named.
