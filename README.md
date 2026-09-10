# BrainSkill

**Label-blind operational protocols vs chain-of-thought on an edge LLM**  
Confirmatory study by Predrag Urošević (2026).

> Public results poster: **https://pedjaurosevic.github.io/brainskill/**

## One-sentence result

On `Muse-Glimmer-30B-exl3-2.00bpw`, a careful checklist protocol (`high_c`) achieved the **highest overall accuracy (92.2%)** and lowest safety violation rate (2.8%), while verification instructions **boosted inspection tool use (+19.4%)** without significantly improving verbal calibration error (MCE) versus chain-of-thought. On Gemini Flash, all protocols achieved 100% accuracy on Domain 1.

## Status

| Piece | Status |
| --- | --- |
| Spec / freeze | Tag `brainskill-freeze-v3.1` |
| OSF project | https://osf.io/p9tcy/ |
| OSF preregistration | https://osf.io/gzjrd/ |
| Confirmatory battery | **1,440 / 1,440** complete (`results/battery_20260909_233434.jsonl`) |
| Secondary cloud check | **40 / 40** complete on Gemini Flash (`results/battery_gemini_flash.jsonl`) |
| Analysis script | [`analysis/analyze.py`](analysis/analyze.py) (MixedLM + Holm pipeline) |
| Report | [`analysis/ANALYSIS.md`](analysis/ANALYSIS.md) |
| Trial JSONL | [Release `results-v3.1`](https://github.com/pedjaurosevic/brainskill/releases/tag/results-v3.1) |

## Repo map

| Path | Role |
| --- | --- |
| `WHITEPAPER.md` | Full methods write-up & empirical report |
| `PLAN.md` / `PREREGISTRATION.md` | Confirmatory specification |
| `FREEZE.md` | SHA-256 freeze snapshot |
| `types/conditions.json` | Four label-blind conditions + denylist |
| `modules/` | Compiler, hardened deterministic grader, 17 unit tests |
| `benchmark/` | Dataset builder, local runner, and Gemini check runner |
| `analysis/` | Reproducible MixedLM analysis script & H1–H3 report |
| `docs/` | GitHub Pages results poster |

## Reproduce (high level)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-analysis.txt
python3 -m unittest modules.test_compiler modules.test_runner_harness
python3 analysis/analyze.py
```

Do **not** commit real inference host/port. Use `.env` locally (see `.env.example`).

## License note

Code and docs in this repository: see repository license settings / OSF project license (CC0 on OSF registration metadata).
