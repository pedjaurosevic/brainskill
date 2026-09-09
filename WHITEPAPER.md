# Can plain work instructions beat "think step by step" on a small local model?

**BrainSkill confirmatory study — whitepaper for review**  
**Authors:** Predrag Urošević  
**Document date:** 2026-09-09  
**Status:** Plan and software are ready for a freeze review. **We have not run the full experiment yet. This paper reports no results.**  
**Companion specs:** `PLAN.md` v3.1, `PREREGISTRATION.md`, `RED_TEAM_AUDIT.md`, `benchmark/TESTING_METHODOLOGY.md`

---

## Abstract

Many prompts tell a language model to *act like* a personality type or a famous psychologist. That mostly tests whether the model remembers internet stereotypes.

BrainSkill asks a simpler question: if we give the model **plain work instructions**—check your claim, say what would prove you wrong, use a tool when you can, fill a checklist, do not guess—does it answer better than the usual "think step by step"? Better here means: more often correct, more honest about how sure it is, more willing to inspect a system before acting, and less dependent on extra documents we paste in.

The model **never** sees brand names like INTJ, Kahneman, or "System 1". We only send operational steps.

We will compare **four instruction styles**, each with and without a fixed set of helper documents, across **60 tasks**, repeated **3 times**. That is **1,440** scored runs. When we use the "two drafts" style, our runner—not the model—decides whether the drafts disagree and whether a careful second pass is needed.

The model under test is a compressed local model (`Muse-Glimmer-30B-exl3-2.00bpw`) served by TabbyAPI on this machine only (exact address kept private). The dataset, prompt builder, automatic scorer, and runner already exist; nine unit tests pass; a dry run plans 1,440 trials. The full battery has **not** been started. Before we freeze and preregister, we still need fuller fake tool outputs for some Linux tasks, one timed tool-loop test, and a proper retry rule when the API fails.

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

Until we have run logs from the full battery, BrainSkill is a **design and test harness**, not an empirical advance over these papers.

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

Rough time for the full local run, including extra drafts: about **8–24 hours** wall-clock. We have not yet timed a Domain-2 tool loop.

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

We treat **the task** as the unit we want to generalize to. The three seeds are repeats for noise, not 1,440 independent tasks. Analysis: mixed-effects model with a random intercept per task; compare each style to step-by-step; Holm correction on the planned family of tests. After freeze: no editing prompts, rubrics, or items. Spec says: retry a failed HTTP call once, then score wrong—**the runner does not implement that yet**. The analysis script is **not in the repo yet**.

---

## 4. What already exists

| Piece | Status |
| :--- | :--- |
| `types/conditions.json` | Four instruction styles + forbidden-word list |
| `modules/compiler.py` / `grader.py` | Built; **9 unit tests pass** |
| `benchmark/dataset.json` | 60 tasks with documents and scorers |
| `benchmark/run_battery.py` | Built: talks to a local OpenAI-style API, two-draft gate, fake safe tools, JSONL log, `--dry-run` plans **1,440** trials |
| OSF / Zenodo freeze | **Not done** |
| Full experiment | **Not started** |
| Stats analysis script | **Missing** |

**Working file fingerprints** (2026-09-09; **not** a public freeze—recompute at freeze):

| File | SHA-256 |
| :--- | :--- |
| `benchmark/dataset.json` | `bb3ab75a3701064642c8694610b579cb28ebb0167cc371ce4d5048e2e5a3d086` |
| `types/conditions.json` | `76179e1bd48a3a986f02317ef043bf96737a930d9a69547c620689b792d90f1e` |
| `benchmark/run_battery.py` | `e21fd66b592a1802d23beb960e3fd8ea4d7606d0d9de9dca0a3023cae02819b9` |

---

## 5. Limits (said out loud)

See also `RED_TEAM_AUDIT.md`.

1. **Longer prompts.** Check-yourself and checklist text is longer than step-by-step. A same-length "just be careful" control is not in this design.
2. **Pattern scoring** on Domains 2 and 4 can miss good answers that use different words.
3. **Fake tool outputs** now cover `d2.01`–`d2.12` (still simulated, not a live shell).
4. **API retry** is coded (once, then JSONL failure row).
5. **No timed Domain-2 tool loop** yet for the freeze checklist.
6. On a heavily compressed model, written confidence may be empty talk.
7. **Sixty tasks** can catch large, stable gains; small calibration gains may be invisible. A null H1 is still a result—not a reason to unpark the parked ideas.
8. The check on bigger cloud models is only a direction check on ten tasks.

---

## 6. Freeze and preregistration checklist

Target: OSF or Zenodo **after** a smoke test and hash freeze. Today: **not registered, no DOI.**

Before freeze:

1. Compiler/grader tests pass — **done** (9).
2. Record hashes of dataset, conditions, runner, PLAN, PREREG.
3. Time one Domain-2 run with fake tools on the live model — **still needed**.
4. Confirm the live model id still matches the name we publish (or update the name).
5. Finish fake outputs for `d2.07`–`d2.12`.
6. Implement retry-once, then score as wrong.
7. Upload PLAN, PREREG, conditions, dataset, compiler, grader, runner.

After freeze: run the full 1,440 local trials (plus extra drafts); optional small cloud direction check; analyze as planned; **do not** bring Jung / Luria / Friston / Sternberg into the main analysis.

---

## 7. What this paper is not

- Not a claim about machine consciousness or an "implemented mind". The JSON fields are bookkeeping.
- Not a personality or MBTI study. Those names are banned in model prompts.
- Not a finished experiment. No accuracy or calibration results appear here because we have not run the battery.
- Not a frozen preregistration. The hashes above are working notes only.
- Not a license to treat 1,440 log lines as 1,440 independent tasks.

---

## Closing

BrainSkill is a clear plan and a working test harness. It asks whether **plain check-yourself instructions**, without psychology brand names, help a small local model more than "think step by step"—on correctness, honest confidence, careful tool use, and reliance on pasted documents.

The scientific answer comes only after we close the gaps above, freeze the files, preregister, and run the matrix. Until then, this whitepaper is a methods document for review, not evidence that the protocols work.
