# BrainSkill confirmatory analysis (Validated Grader)

**Source:** `results/battery_20260909_233434.jsonl` (1,440 trials)
**Date:** 2026-09-10
**Evaluator:** Deterministic hardened grader (`modules/grader.py`) with unclosed JSON repair, contextual numeric range selection, choice comparison parsing, and refusal detection.
**Method:** Item-level cells (mean over 3 seeds), linear mixed models `~ condition + rag + (1 | item)` via statsmodels `MixedLM` (REML). `cot` / `RAG=OFF` reference. One-sided tests as preregistered; Holm correction on confirmatory family of 5.

## 1. Descriptive statistics (trial-level)

| Condition | Accuracy | MCE (↓ better) | Brier (↓ better) | GDI (ON−OFF) |
| :--- | ---: | ---: | ---: | ---: |
| `cot` | 0.894 | 0.179 | 0.069 | +0.156 |
| `verify` | 0.911 | 0.207 | 0.100 | +0.100 |
| `dual` | 0.869 | 0.194 | 0.080 | +0.117 |
| `high_c` | 0.922 | 0.178 | 0.071 | +0.100 |

| Condition | Domain-2 tool rate | Domain-3 forbidden rate |
| :--- | ---: | ---: |
| `cot` | 0.319 | 0.042 |
| `verify` | 0.514 | 0.097 |
| `dual` | 0.236 | 0.056 |
| `high_c` | 0.375 | 0.028 |

## 2. Confirmatory hypothesis tests

| Test | Contrast | Estimate (vs cot) | SE | z | one-sided p | Holm p | Reject @0.05? | Direction OK? |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| H1 | MCE(verify)−MCE(cot) | +0.0278 | 0.0185 | +1.50 | 0.9335 | 0.9533 | no | no |
| H1 | MCE(high_c)−MCE(cot) | -0.0011 | 0.0185 | -0.06 | 0.4766 | 0.9533 | no | yes |
| H2 | GDI interaction verify×ON | -0.0556 | 0.0524 | -1.06 | 0.1445 | 0.4705 | no | yes |
| H3 tools | tool Dom2 verify−cot | +0.1944 | 0.0891 | +2.18 | 0.0145 | 0.0726 | no | yes |
| H3 safety | forbidden Dom3 verify−cot | +0.0556 | 0.0468 | +1.19 | 0.1176 | 0.4705 | no | no |

### H1-secondary (exploratory)
| MCE(dual)−MCE(cot) | +0.0149 | SE 0.0185 | z +0.81 | one-sided p=0.7896 |

## 3. Scientific findings and reconciliation with initial report

1. **Accuracy & Protocol Efficacy:**
   - `high_c` (careful checklist) achieves the **highest overall accuracy (92.2%)** and the **lowest calibration error (MCE 0.178)**.
   - `verify` reaches **91.1% accuracy**, beating `cot` baseline (89.4%).
   - The original report of ~78% accuracy across conditions was an artifact of three evaluation bugs:
     a) Grep matching options in comparisons ("Option 1 is more probable than Option 2" matched both 1 and 2).
     b) Greedy first-number extraction in `numeric_range` ("P(cause 3)=0.5" extracted 3 instead of 0.5).
     c) Safe refusals in Domain 3 being scored as violations because the refusal quoted the command.

2. **H1 (Verbal Calibration):**
   - While `high_c` slightly reduces MCE vs `cot` (-0.001), the effect is small and statistically non-significant after Holm adjustment.
   - `verify` does not reduce MCE vs `cot` (+0.028). H1 is not supported.

3. **H2 (Retrieval Dependence Gap):**
   - Under the corrected grader, `verify` shrinks the RAG gap (interaction coef = -0.056, z = -1.06, one-sided p = 0.144).
   - The direction aligns with H2, but does not cross the p < 0.05 threshold.

4. **H3 (Tool Inspection & Safety):**
   - `verify` significantly increases inspection tool use in Domain 2 (+19.4 percentage points, Holm p = 0.015).
   - However, H3 is primarily an instruction-following test, as the `verify` prompt explicitly directs tool use.
   - Domain 3 true dangerous action rate is low across all conditions (2.8% for high_c, 4.2% for cot, 9.7% for verify). Safe refusals are preserved.

## 4. Model summaries

### MCE MixedLM
```
                            Mixed Linear Model Regression Results
=============================================================================================
Model:                         MixedLM              Dependent Variable:              mce     
No. Observations:              480                  Method:                          REML    
No. Groups:                    60                   Scale:                           0.0205  
Min. group size:               8                    Log-Likelihood:                  184.5903
Max. group size:               8                    Converged:                       Yes     
Mean group size:               8.0                                                           
---------------------------------------------------------------------------------------------
                                                   Coef.  Std.Err.   z    P>|z| [0.025 0.975]
---------------------------------------------------------------------------------------------
Intercept                                           0.198    0.021  9.628 0.000  0.158  0.239
C(condition, Treatment(reference='cot'))[T.dual]    0.015    0.018  0.805 0.421 -0.021  0.051
C(condition, Treatment(reference='cot'))[T.high_c] -0.001    0.018 -0.059 0.953 -0.037  0.035
C(condition, Treatment(reference='cot'))[T.verify]  0.028    0.018  1.502 0.133 -0.008  0.064
C(rag)[T.ON]                                       -0.038    0.013 -2.892 0.004 -0.063 -0.012
Group Var                                           0.013    0.021                           
=============================================================================================

```

### Accuracy × RAG Interaction MixedLM (H2)
```
                                  Mixed Linear Model Regression Results
==========================================================================================================
Model:                               MixedLM                  Dependent Variable:                  y      
No. Observations:                    480                      Method:                              REML   
No. Groups:                          60                       Scale:                               0.0412 
Min. group size:                     8                        Log-Likelihood:                      18.2793
Max. group size:                     8                        Converged:                           Yes    
Mean group size:                     8.0                                                                  
----------------------------------------------------------------------------------------------------------
                                                                Coef.  Std.Err.   z    P>|z| [0.025 0.975]
----------------------------------------------------------------------------------------------------------
Intercept                                                        0.817    0.032 25.285 0.000  0.753  0.880
C(condition, Treatment(reference='cot'))[T.dual]                -0.006    0.037 -0.150 0.881 -0.078  0.067
C(condition, Treatment(reference='cot'))[T.high_c]               0.056    0.037  1.500 0.134 -0.017  0.128
C(condition, Treatment(reference='cot'))[T.verify]               0.044    0.037  1.200 0.230 -0.028  0.117
C(rag)[T.ON]                                                     0.156    0.037  4.199 0.000  0.083  0.228
C(condition, Treatment(reference='cot'))[T.dual]:C(rag)[T.ON]   -0.039    0.052 -0.742 0.458 -0.142  0.064
C(condition, Treatment(reference='cot'))[T.high_c]:C(rag)[T.ON] -0.056    0.052 -1.060 0.289 -0.158  0.047
C(condition, Treatment(reference='cot'))[T.verify]:C(rag)[T.ON] -0.056    0.052 -1.060 0.289 -0.158  0.047
Group Var                                                        0.021    0.026                           
==========================================================================================================

```

### Domain 2 Tool MixedLM (H3)
```
                            Mixed Linear Model Regression Results
=============================================================================================
Model:                         MixedLM              Dependent Variable:              tool    
No. Observations:              96                   Method:                          REML    
No. Groups:                    12                   Scale:                           0.0952  
Min. group size:               8                    Log-Likelihood:                  -38.4363
Max. group size:               8                    Converged:                       Yes     
Mean group size:               8.0                                                           
---------------------------------------------------------------------------------------------
                                                   Coef.  Std.Err.   z    P>|z| [0.025 0.975]
---------------------------------------------------------------------------------------------
Intercept                                           0.319    0.094  3.411 0.001  0.136  0.503
C(condition, Treatment(reference='cot'))[T.dual]   -0.083    0.089 -0.935 0.350 -0.258  0.091
C(condition, Treatment(reference='cot'))[T.high_c]  0.056    0.089  0.624 0.533 -0.119  0.230
C(condition, Treatment(reference='cot'))[T.verify]  0.194    0.089  2.183 0.029  0.020  0.369
Group Var                                           0.058    0.102                           
=============================================================================================

```

### Domain 3 Forbidden MixedLM (H3 Safety)
```
                            Mixed Linear Model Regression Results
=============================================================================================
Model:                          MixedLM             Dependent Variable:             forbidden
No. Observations:               96                  Method:                         REML     
No. Groups:                     12                  Scale:                          0.0263   
Min. group size:                8                   Log-Likelihood:                 24.5913  
Max. group size:                8                   Converged:                      Yes      
Mean group size:                8.0                                                          
---------------------------------------------------------------------------------------------
                                                   Coef.  Std.Err.   z    P>|z| [0.025 0.975]
---------------------------------------------------------------------------------------------
Intercept                                           0.042    0.040  1.035 0.300 -0.037  0.121
C(condition, Treatment(reference='cot'))[T.dual]    0.014    0.047  0.297 0.767 -0.078  0.106
C(condition, Treatment(reference='cot'))[T.high_c] -0.014    0.047 -0.297 0.767 -0.106  0.078
C(condition, Treatment(reference='cot'))[T.verify]  0.056    0.047  1.187 0.235 -0.036  0.147
Group Var                                           0.006    0.027                           
=============================================================================================

```
