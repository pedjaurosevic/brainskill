# BrainSkill confirmatory analysis

**Source:** `results/battery_20260909_233434.jsonl` (1,440 trials)
**Date:** 2026-09-10
**Method:** Item-level cells (mean over 3 seeds), then linear mixed models `~ condition + rag + (1 | item)` via statsmodels `MixedLM` (REML). `cot` / `RAG=OFF` reference. One-sided tests as preregistered; Holm on the confirmatory family of 5.
**Note:** Linear mixed model on 0–1 outcomes is the Gaussian / LPM approximation named in PLAN (Bernoulli mixed GLM not required).

## 1. Descriptive (trial-level)

| Condition | Accuracy | MCE | Brier | GDI (ON−OFF) |
| :--- | ---: | ---: | ---: | ---: |
| `cot` | 0.797 | 0.229 | 0.128 | +0.050 |
| `verify` | 0.781 | 0.275 | 0.171 | +0.083 |
| `dual` | 0.775 | 0.247 | 0.144 | +0.039 |
| `high_c` | 0.800 | 0.257 | 0.153 | +0.056 |

| Condition | Domain-2 tool rate | Domain-3 forbidden rate |
| :--- | ---: | ---: |
| `cot` | 0.319 | 0.361 |
| `verify` | 0.514 | 0.375 |
| `dual` | 0.236 | 0.403 |
| `high_c` | 0.375 | 0.444 |

Parse failures / errors: parse_ok mean=0.9507; HTTP/error rows=1.

## 2. Confirmatory tests

| Test | Contrast | Estimate (vs cot) | SE | z | one-sided p | Holm p | Reject @0.05? | Direction OK? |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| H1 | MCE(verify)−MCE(cot) | +0.0281 | 0.0225 | +1.25 | 0.8944 | 1 | no | no |
| H1 | MCE(high_c)−MCE(cot) | +0.0109 | 0.0226 | +0.48 | 0.6848 | 1 | no | no |
| H2 | GDI interaction verify×ON | +0.0333 | 0.0620 | +0.54 | 0.7046 | 1 | no | no |
| H3 | tool Dom2 verify−cot | +0.1944 | 0.0709 | +2.74 | 0.003032 | 0.01516 | yes | yes |
| H3 safety | forbidden Dom3 verify−cot (higher=bad) | +0.0139 | 0.0850 | +0.16 | 0.4351 | 1 | no | yes |

### H1-secondary (exploratory, not in Holm family)
| MCE(dual)−MCE(cot) | -0.0034 | SE 0.0226 | z -0.15 | one-sided p=0.4396 | direction lower MCE: yes |

## 3. Interpretation (plain)

- **H1 verify (lower MCE):** not supported (coef=+0.0281, Holm p=1).
- **H1 high_c (lower MCE):** not supported (coef=+0.0109, Holm p=1).
- **H2 (smaller GDI for verify):** not supported (interaction=+0.0333, Holm p=1). Descriptive GDI cot=+0.050, verify=+0.083.
- **H3 tools (more Dom2 tools for verify):** supported (coef=+0.1944, Holm p=0.01516). Rates cot=0.319, verify=0.514.
- **H3 safety (verify not higher Dom3 forbidden):** OK (no significant increase) (coef=+0.0139, one-sided p[higher]=0.4351). Rates cot=0.361, verify=0.375.

Overall raw accuracy is similar across conditions (~78–80%). Domain 3 safety accuracy is low (~48%) for all conditions — a construct/grader issue as much as a protocol effect.

## 4. Model summaries (abbrev)

### MCE MixedLM
```
                            Mixed Linear Model Regression Results
=============================================================================================
Model:                          MixedLM              Dependent Variable:              mce    
No. Observations:               475                  Method:                          REML   
No. Groups:                     60                   Scale:                           0.0301 
Min. group size:                7                    Log-Likelihood:                  69.4187
Max. group size:                8                    Converged:                       Yes    
Mean group size:                7.9                                                          
---------------------------------------------------------------------------------------------
                                                   Coef.  Std.Err.   z    P>|z| [0.025 0.975]
---------------------------------------------------------------------------------------------
Intercept                                           0.249    0.033  7.661 0.000  0.186  0.313
C(condition, Treatment(reference='cot'))[T.verify]  0.028    0.023  1.250 0.211 -0.016  0.072
C(condition, Treatment(reference='cot'))[T.dual]   -0.003    0.023 -0.152 0.879 -0.048  0.041
C(condition, Treatment(reference='cot'))[T.high_c]  0.011    0.023  0.481 0.630 -0.033  0.055
C(rag)[T.ON]                                        0.002    0.016  0.099 0.921 -0.030  0.033
Group Var                                           0.044    0.055                           
=============================================================================================

```

### Accuracy × RAG interaction MixedLM (H2)
```
                                  Mixed Linear Model Regression Results
==========================================================================================================
Model:                              MixedLM                  Dependent Variable:                  y       
No. Observations:                   480                      Method:                              REML    
No. Groups:                         60                       Scale:                               0.0577  
Min. group size:                    8                        Log-Likelihood:                      -82.9720
Max. group size:                    8                        Converged:                           Yes     
Mean group size:                    8.0                                                                   
----------------------------------------------------------------------------------------------------------
                                                                Coef.  Std.Err.   z    P>|z| [0.025 0.975]
----------------------------------------------------------------------------------------------------------
Intercept                                                        0.772    0.046 16.701 0.000  0.682  0.863
C(condition, Treatment(reference='cot'))[T.verify]              -0.033    0.044 -0.760 0.447 -0.119  0.053
C(condition, Treatment(reference='cot'))[T.dual]                -0.017    0.044 -0.380 0.704 -0.103  0.069
C(condition, Treatment(reference='cot'))[T.high_c]              -0.000    0.044 -0.000 1.000 -0.086  0.086
C(rag)[T.ON]                                                     0.050    0.044  1.140 0.254 -0.036  0.136
C(condition, Treatment(reference='cot'))[T.verify]:C(rag)[T.ON]  0.033    0.062  0.538 0.591 -0.088  0.155
C(condition, Treatment(reference='cot'))[T.dual]:C(rag)[T.ON]   -0.011    0.062 -0.179 0.858 -0.133  0.110
C(condition, Treatment(reference='cot'))[T.high_c]:C(rag)[T.ON]  0.006    0.062  0.090 0.929 -0.116  0.127
Group Var                                                        0.071    0.064                           
==========================================================================================================

```