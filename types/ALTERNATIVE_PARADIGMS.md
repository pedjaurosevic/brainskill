# Parked alternative architectures

**Status: PARKED.** Not confirmatory treatments. PLAN.md v3.0 tests four label-blind conditions (`cot`, `verify`, `dual`, `high_c`). Do not unpark these paradigms until that matrix has been run and analyzed as specified.

The dual-process conflict score \(C_s = 1 - \max P(\text{tokens})\) below is **rejected** for the confirmatory gate. The runner uses disagreement of two canonicalized answers instead.

---

# Alternative Cognitive Architectures Beyond Jung's 16 Types

While Jung's 16 cognitive stacks provide an intuitive, widely recognized categorical taxonomy, BrainSkill's modular architecture could later support several alternative computational paradigms. They are not in the v3 matrix.

---

## Paradigm 1: Luria's Three Functional Brain Units (Neuropsychological Model)

Proposed by Alexander Luria (founding father of neuropsychology). Rather than "personality types," this structures the agent into the three fundamental biological units of cognitive regulation:

```
┌────────────────────────────────────────────────────────────┐
│ UNIT 1: Arousal, Vigilance & Attention (Brainstem/Reticular)│
│ - Regulates token compute allocation and noise filtering.   │
│ - Gates input based on signal-to-noise ratio.              │
├────────────────────────────────────────────────────────────┤
│ UNIT 2: Information Reception, Coding & Storage (Sensory)  │
│ - Primary: Raw parsing of file diffs and tool logs.       │
│ - Secondary: Cross-modal feature extraction.               │
│ - Tertiary: Semantic integration and working memory buffer.│
├────────────────────────────────────────────────────────────┤
│ UNIT 3: Programming, Regulation & Verification (Frontal)   │
│ - Goal decomposition and plan formulation.                 │
│ - Executive inhibition of premature output.                │
│ - Post-execution comparator: verifies outcome vs. intent.  │
└────────────────────────────────────────────────────────────┘
```

**Why this is compelling:**  
It mirrors true functional neurology. It eliminates personality drama and optimizes for pure task execution fidelity.

---

## Paradigm 2: Dynamic Dual-Process Arbitration (Kahneman System 1 / System 2)

Instead of a static profile, this model acts as a **Dynamic Cognitive Gearbox**:

- **System 1 (Fast / Heuristic Engine):**
  - High-temperature, low-latency, parametric forward pass. Generates an immediate draft hypothesis.
- **Surprise / Conflict Detector (ACC Analog):**
  - Evaluates internal entropy and confidence:
    $$\text{Conflict Score } C_s = 1 - \max(P(\text{tokens}))$$
  - If $C_s < \theta_{\text{low}}$: Emit fast answer directly (saves compute, mimics human intuition).
  - If $C_s \ge \theta_{\text{high}}$: Intercept and force gear-shift to System 2.
- **System 2 (Slow / Deliberative Auditor):**
  - Low-temperature, formal step-by-step verification, tool execution (`bash`, `read`), and falsification checking.

**Why this is compelling:**  
Solves the fundamental compute-efficiency problem of LLMs. Simple queries are answered instantly; complex, ambiguous dilemmas trigger deliberate analytical depth.

---

## Paradigm 3: Active Inference & Predictive Processing (Friston's FEP)

Based on Karl Friston's Free Energy Principle. The agent is parameterized as a generative model minimizing variational free energy (surprise):

1. **Epistemic Value (Curiosity / Exploration):**
   - The agent chooses actions (reading files, listing directories) specifically to maximize Information Gain:
     $$\mathcal{G}_{\text{epistemic}} = \mathbb{E}[D_{KL}(Q(\theta | a) \parallel Q(\theta))]$$
2. **Pragmatic Value (Goal Pursuit / Exploitation):**
   - Actions aimed strictly at satisfying user requirements:
     $$\mathcal{G}_{\text{pragmatic}} = \mathbb{E}[\ln P(o^*)]$$
3. **Precision Weighting ($\gamma$):**
   - A single tuning knob: High $\gamma$ means sensory evidence (actual tool output) strictly overrides the model's internal priors (eliminating hallucinations). Low $\gamma$ relies on internal intuition.

---

## Paradigm 4: The Continuous Big Five (OCEAN) Vector Space

Replaces discrete 16 boxes with a continuous 5-dimensional vector $\vec{P} = \langle O, C, E, A, N \rangle \in [0.0, 1.0]^5$:

- **$O$ (Openness):** Controls divergent exploration rate (branching factor for hypotheses).
- **$C$ (Conscientiousness):** Strictness of validation checks, zero-tolerance for untested code, exhaustive edge-case coverage.
- **$E$ (Extraversion):** Verbosity and proactive user collaboration vs. terse silent autonomous execution.
- **$A$ (Agreeableness):** Susceptibility to user suggestion. Low $A$ actively challenges flawed user premises; high $A$ seeks cooperative harmony.
- **$N$ (Neuroticism / Threat-Sensitivity):** Depth of defensive coding, automated rollback preparation, and worst-case scenario paranoia.

---

## Paradigm 5: Sternberg's Triarchic Theory of Intelligence

Divides cognitive processing into three distinct cognitive lenses:
1. **Analytical Sub-Mind:** Algorithmic decomposition, formal mathematical correctness, critique.
2. **Creative Sub-Mind:** Lateral problem re-framing, synthetic connections across domains.
3. **Practical Sub-Mind:** Feasibility under hard hardware constraints (workstation RTX 3060, Btrfs limits, execution time).
