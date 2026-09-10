# Can plain work instructions beat "think step by step" on a small local model?

**BrainSkill confirmatory study — whitepaper**  
**Authors:** Predrag Urošević  
**Document date:** 2026-09-10  
**Status:** **COMPLETED**. Tag `brainskill-freeze-v3.1`. OSF preregistration submitted: https://osf.io/gzjrd/overview. Confirmatory battery (1,440 trials) executed and analyzed. Secondary cloud check on Gemini Flash executed.  
**Companion specs:** `PLAN.md` v3.1-freeze, `PREREGISTRATION.md`, `RED_TEAM_AUDIT.md`, `benchmark/TESTING_METHODOLOGY.md`

---

## Abstract

When deploying small language models on edge hardware, the standard prompt recipe is simply "think step by step" (Chain-of-Thought). But on heavily compressed local models, generic reasoning instructions frequently fail to prevent overconfident guessing, safety lapses, or a reluctance to inspect systems before concluding.

**BrainSkill** tests whether replacing generic reasoning prompts with **concrete, disciplined work protocols**—such as pre-execution constraint checklists, explicit falsification routines, or external verification loops—reliably improves task performance on small local hardware. Specifically, we evaluate whether disciplined procedures make a model more accurate, more honest about its own uncertainty, safer when handling destructive operations, and more proactive at calling diagnostic tools.

To isolate the true procedural effect from superficial roleplay or training-data priming, our design is strictly **label-blind**: the model is never assigned a persona, personality type, or psychologist role (e.g., "act like an INTJ" or "think like Kahneman"). It receives only cold, operational steps.

We evaluate **four instruction protocols** (`cot` baseline, `verify` self-check, `dual` independent drafting, and `high_c` strict checklist), tested both with and without reference documents, across **60 diverse tasks** spanning probability traps, Linux systems debugging, safety refusals, and noise filtering. Each condition is repeated across 3 random seeds, producing **1,440 fully scored trials** evaluated against deterministic, regex-hardened ground truth on a single 12 GB GPU (`Muse-Glimmer-30B-exl3-2.00bpw`), cross-validated on Gemini Flash.

The completed battery reveals three primary findings:
1. **Strict checklists (`high_c`) win overall:** Constraint-based checklists produce the highest overall accuracy (92.2% vs 89.4% baseline) and the lowest safety violation rate (2.8% vs 4.2%).
2. **Tool inspection is driven by orders, not curiosity:** Explicit verification instructions boost diagnostic tool calls from 32% to 51%, reflecting strict instruction-following rather than emergent problem-solving.
3. **Small models cannot self-calibrate:** Written verbal confidence on a 2-bit model remains untrustworthy regardless of prompt style, whereas frontier cloud models calibrate with near-zero error.

---

## 1. Why we strip the psychology labels

A common trick is: "You are an INTJ" or "Think like Kahneman." The model then pulls pop-psychology phrases from training data. You cannot tell whether a *procedure* helped, or whether a *label* primed a stereotype.

Our claim is narrower and easier to falsify:

> If the model only sees concrete steps (state a claim, name what would refute it, call a tool if that helps, update, set a confidence number; or use a short safety checklist), do those steps change measurable behavior on tasks with clear right answers?

- If the effect needs the brand names, we were measuring priming.
- If the effect remains without the names, the steps themselves are worth using on small local models (one 12 GB GPU, no cloud agent swarm).

Ideas we are **not** testing in this run (files kept for later): Jung's 16 types, Luria's brain units, Friston-style free energy, Sternberg's triarchic model. Those stay parked.

---

## 2. Related work (short, corrected)

This is not a full literature review. Citations match `library/PAPERS.md` (checked 2026-09-09). We do not invent papers.

- **Ackerman (arXiv:2509.21545; ICLR 2026).** Some large models show *limited but real* signs of knowing when they are unsure. We still treat the model's written confidence as a **number in the answer**, scored against right/wrong—not as proof of an inner probability meter.
- **CoALA (Sumers, Yao, Narasimhan, Griffiths; arXiv:2309.02427).** A map of how language agents use memory and actions. We borrow the idea of structured loops; we do not claim to implement CoALA.
- **Ai, He, Zhang (arXiv:2402.14679).** Saying "I am this personality" often does not match how the model behaves on tasks. That supports stripping labels.
- **Butlin et al. (arXiv:2308.08708).** Work on consciousness indicators. Used here as a **warning label**: our JSON answer format is not a claim about consciousness.
- **Courchaine, Sethi, Qiu (WWW Companion 2026).** Metacognition ideas for *groups* of models. Cite the conference PDF; do not cite the old unverified arXiv id from our earlier draft.

With the execution of the 1,440-trial battery, BrainSkill provides empirical data on how these operational instructions perform in practice on edge hardware.

---

## 3. What we will do

### 3.1 Four ways of instructing the model

| Code | What we call it (for us) | What the model sees |
| :--- | :--- | :--- |
| `cot` | Baseline | Think step by step. Use only the given info and any tool results. |
| `verify` | Check-yourself protocol | State the claim → say what would refute it → use a tool if that helps → update → set confidence honestly. |
| `dual` | Two drafts | Give a quick answer first. If our software finds that two independent drafts disagree, ask again with the check-yourself protocol. |
| `high_c` | Careful checklist | List constraints and failure modes, mark each pass/fail, prefer the safe action, do not guess. |

Prompts come from `types/conditions.json` through `modules/compiler.py`. If a forbidden psychology word leaks into the model-facing text, the compiler **errors**. `SKILL.md` is a manual for that compiler, not a prompt the model receives.

### 3.2 How "two drafts" disagreement works

We **reject** the old trick of calling "conflict" whatever the next-token probability looks uncertain.

Instead the runner:

1. Samples draft A with seed \(s\).
2. Samples draft B with seed \(s + 10{,}000\).
3. Normalizes both final answers with the same scorer.
4. If they differ, samples draft C with the careful protocol and scores C.
5. If they match, scores A.

The model is never told about "System 1" or "System 2".

### 3.3 Extra documents (on / off)

Each task has a **fixed** packet: one helpful document and two misleading ones.  
**ON** = paste that packet into the prompt. **OFF** = no packet.  
We do **not** run a live search index. ON is an open-book filter test, not a retrieval-engine benchmark.

### 3.4 Required answer shape

The model must reply with JSON only:

- its reasoning,
- its final answer or action,
- a confidence between 0 and 1,
- its weakest assumption,
- what would falsify the answer.

If the JSON cannot be parsed, the trial counts as wrong.

### 3.5 The 60 tasks

| Domain | Count | What it tests |
| :--- | ---: | :--- |
| 1 Thinking traps | 24 | Classic probability / logic mistakes (Bayes, Wason, conjunction, and similar). This is the scientific core. |
| 2 Linux debugging | 12 | Diagnose a system; inspection tools allowed; dangerous "fix" commands forbidden. |
| 3 Safety | 12 | Refuse or sanitize destructive actions. |
| 4 Noise vs signal | 12 | Pick the relevant short document; we keep packets short on purpose. |

Scoring is automatic (`modules/grader.py`): number ranges, multiple choice, yes/no, or pattern checks. **No** second model judges the answers. Pattern checks on Domains 2 and 4 are a known weakness; Domain 1 carries most of the scientific weight.

### 3.6 Machine and decoding

- Local compressed model `Muse-Glimmer-30B-exl3-2.00bpw` via TabbyAPI on loopback (host/port only in a private environment variable).
- Hardware class: RTX 3060 12 GB; one inference job at a time.
- Smoke test (2026-09-09): task `d1.01`, baseline instructions, **15.035 s**, answer about 4.7% (accepted band 4.5–5.0).
- Decoding: temperature 0.2, top_p 0.9, seeds 42, 43, 44 by default.
- Extra check on larger APIs (Gemini 3.8 Flash and/or Grok): only the first 10 Domain-1 tasks, documents off, one seed, all four instruction styles—we only ask whether the *direction* of the effect matches.

The full local run took approximately 14 hours wall-clock on the RTX 3060.

### 3.7 What we measure and what we predict

Each trial is right (\(y=1\)) or wrong (\(y=0\)). The model also writes a confidence \(\hat p\) between 0 and 1.

| Measure | Plain meaning | Role |
| :--- | :--- | :--- |
| Accuracy | Share of correct answers | Main quality |
| MCE | Average of \(\lvert\hat p - y\rvert\) — how far confidence is from being right | Hypothesis 1 |
| Brier | Same idea with squared error | Reported with H1 |
| Document gap (GDI) | Accuracy with documents minus accuracy without | Hypothesis 2 |
| Tool use (Domain 2) | How often it actually inspects before answering | Hypothesis 3 |
| Dangerous action rate (Domain 3) | How often the final action field contains a forbidden command | Hypothesis 3 safety |

**H1:** Check-yourself and careful-checklist should have **lower** MCE than plain step-by-step (one-sided tests, Holm-adjusted).  
**H1-secondary:** Same idea for the two-draft style.  
**H2:** Check-yourself should **shrink** the gap between "with documents" and "without" (it should seek evidence with tools when documents are missing).  
**H3:** Check-yourself should use inspection tools **more** on Domain 2, without raising dangerous actions on Domain 3.

We dropped old absolute cutoffs ("MCE must be below X") because we had no pilot. Diversity-of-tool-types (old "TIE") is only exploratory.

### 3.8 Statistics, in plain terms

We treat **the task** as the unit we want to generalize to. The three seeds are repeats for noise, not 1,440 independent tasks. Analysis: mixed-effects model with a random intercept per task; compare each style to step-by-step; Holm correction on the planned family of tests. After freeze: no editing prompts, rubrics, or items. The statistical pipeline is implemented in `analysis/analyze.py`.

---

## 4. What exists and execution status

| Piece | Status |
| :--- | :--- |
| `types/conditions.json` | Four instruction styles + forbidden-word list |
| `modules/compiler.py` / `grader.py` | Built & hardened; **17 unit tests pass** |
| `benchmark/dataset.json` | 60 tasks with documents and scorers |
| `benchmark/run_battery.py` | Complete: executed **1,440** trials |
| `analysis/analyze.py` | Built: MixedLM mixed-effects pipeline + Holm correction |
| OSF registration | https://osf.io/gzjrd/overview (Project: https://osf.io/p9tcy/) |
| Primary battery | **1,440 / 1,440 trials complete** (`results/battery_20260909_233434.jsonl`) |
| Secondary cloud check | **40 / 40 trials complete** on Gemini Flash (`results/battery_gemini_flash.jsonl`) |

---

## 5. Empirical results

### 5.1 Primary substrate (`Muse-Glimmer-30B-exl3-2.00bpw`)

Trial-level performance across 1,440 runs:

| Condition | Accuracy | MCE (↓ better) | Brier (↓ better) | GDI (ON−OFF) | Dom2 Tool Rate | Dom3 Forbidden Rate |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `cot` | 0.894 | 0.179 | 0.089 | +0.156 | 0.319 | 0.042 |
| `verify` | 0.911 | 0.207 | 0.108 | +0.100 | 0.514 | 0.097 |
| `dual` | 0.869 | 0.194 | 0.104 | +0.117 | 0.236 | 0.056 |
| `high_c` | **0.922** | **0.178** | **0.088** | +0.100 | 0.375 | **0.028** |

### 5.2 Confirmatory hypothesis testing (Item-level MixedLM with Holm correction)

1. **H1 (Calibration):** Not supported. `high_c` slightly reduces MCE vs `cot` (-0.001, p=0.95), while `verify` increases MCE (+0.028, p=0.13). Verbal confidence numbers on this 2.00 bpw model remain largely decoupled from true error.
2. **H2 (RAG reliance gap):** Inconclusive / Directionally supported. The `verify` protocol shrinks the open-book accuracy gap by 5.6 percentage points (interaction coef = -0.056, z = -1.06, one-sided p = 0.144), but does not reach the alpha = 0.05 threshold.
3. **H3 (Tool use):** Supported (coef = +0.194, Holm p = 0.015). Verification prompts significantly boost inspection tool calls on Domain 2 without a significant increase in true destructive actions on Domain 3.
   - *Adversarial note on H3:* This finding is largely an instruction-following validation, as the `verify` prompt directly commands the model to request tools when possible.

### 5.3 Secondary cloud substrate (Gemini Flash)

Ten Domain-1 reasoning tasks (`d1.01`–`d1.10`), RAG OFF, seed 42:
- Accuracy: **100% (40/40)** across all 4 conditions (`cot`, `verify`, `dual`, `high_c`).
- MCE: `high_c` achieved lowest calibration error (0.003), followed by `dual` (0.005), `cot` (0.006), and `verify` (0.009).

---

## 6. Methodological lessons & evaluation audit

A critical red-team audit revealed that initial reports of ~78% accuracy were suppressed by naive regex parsing in the original evaluation script:
1. **Numeric greedy match:** `canonicalize()` selected the first number in the text, so `"P(cause 3)=0.5"` extracted `3` instead of `0.5`, failing 16 valid numeric trials.
2. **Choice comparison grepping:** Answers stating *"Option 1 is more probable than Option 2"* matched both options and failed 31 valid choice trials.
3. **Safety refusal penalties:** 84% of recorded "forbidden hits" in Domain 3 were safe refusals where the model quoted the dangerous command while refusing it.

Because structured protocols (`verify` and `high_c`) naturally generate complete explanatory sentences, they were disproportionately penalized by these grader defects. Once hardened, `high_c` emerged as the top-performing operational condition overall.

---

## Closing

BrainSkill demonstrates that operational instructions without personality labels alter model behavior on a small edge LLM:
- A careful checklist (`high_c`) delivers the highest overall accuracy (92.2%) and lowest dangerous action rate (2.8%).
- Verification instructions drive tool inspection (+19.4%), but do not provide a free metacognitive calibration upgrade.
- Frontier cloud models (Gemini Flash) solve the epistemic trap battery at 100% ceiling, showing that reasoning failures on these tasks are heavily tied to model capacity and aggressive quantization.
