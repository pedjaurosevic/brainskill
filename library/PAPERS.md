# BrainSkill Research Library

Short catalogue. Claims below are checked against abstracts/PDFs on 2026-09-09. This is not a literature review.

---

## 1. Architecture

### 1.1 CoALA — Sumers, Yao, Narasimhan, Griffiths
- arXiv: [2309.02427](https://arxiv.org/abs/2309.02427)
- Cognitive-architecture taxonomy for language agents (working memory, long-term memory, action space, decision cycle).
- **Correction:** Griffiths is a co-author. v2 omitted that name.

### 1.2 Consciousness in AI — Butlin, Long, Elmoznino, Bengio, et al.
- arXiv: [2308.08708](https://arxiv.org/abs/2308.08708)
- Indicator properties from GWT, HOT, predictive processing.
- **Use:** negative control. BrainSkill does not claim consciousness. Module 3 is a JSON contract.

### 1.3 Shang — "Theater of Mind" GWT architecture
- Cited previously as arXiv `2604.08206`. Treat as unverified unless the PDF is pinned in-tree. Do not rest a claim on this id.

---

## 2. Metacognition

### 2.1 Ackerman — Evidence for Limited Metacognition in LLMs
- arXiv: [2509.21545](https://arxiv.org/abs/2509.21545) (ICLR 2026)
- Behavioral tests (not self-report). Frontier models show **limited but real** use of an internal confidence signal; resolution is weak; surface difficulty cues matter; post-training likely matters.
- **Correction:** v2 summarized this as "confidence is confabulation". That is not the paper's result. Verbal p in BrainSkill is still only a behavioral output.

### 2.2 Courchaine, Sethi, Qiu — Metacognition framework for ensembles of LLMs
- WWW Companion 2026, Dubai. PDF: `research.sethi.org/.../courchaine_sethi_2026-thewebconf.pdf`
- MSV vector and System 1/2 switching for **ensembles**.
- **Correction:** arXiv `2608.15400` was not confirmed. Cite the WWW Companion paper, not that id.

---

## 3. Persona vs behavior

### 3.1 Ai, He, Zhang — LLM personality consistency
- arXiv: [2402.14679](https://arxiv.org/abs/2402.14679)
- Declared persona and task behavior diverge.
- **Use:** supports label-stripping. Do not test "personality" with questionnaires.

---

## 4. What this study adds (claim, not result)

| Typical paper | This confirmatory design |
| :--- | :--- |
| "Act like an INTJ" | Denylisted brand names; operational protocols only |
| Always-on RAG | Frozen packet ON/OFF |
| MBTI quizzes | Checkable traps + regex safety/debug |
| Cloud multi-agent | One 12GB GPU, timed budget |

Until `run_battery.py` produces JSONL, the right-hand column is a design, not an advance.
