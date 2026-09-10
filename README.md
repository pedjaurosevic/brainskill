# BrainSkill

**Label-blind operational protocols vs chain-of-thought on an edge LLM**  
Confirmatory study by Predrag Urošević (2026).

> Public results poster: **https://pedjaurosevic.github.io/brainskill/**

## One-sentence result

On `Muse-Glimmer-30B-exl3-2.00bpw`, a verification protocol **increased Domain-2 inspection-tool use** without a significant rise in Domain-3 forbidden actions, but **did not** improve verbal calibration (MCE) or shrink the frozen-RAG accuracy gap versus chain-of-thought.

## Status

| Piece | Status |
| --- | --- |
| Spec / freeze | Tag `brainskill-freeze-v3.1` |
| OSF project | https://osf.io/p9tcy/ |
| OSF preregistration | https://osf.io/gzjrd/ |
| Confirmatory battery | **1,440 / 1,440** complete |
| Analysis | [`analysis/ANALYSIS.md`](analysis/ANALYSIS.md) |
| Trial JSONL | [Release `results-v3.1`](https://github.com/pedjaurosevic/brainskill/releases/tag/results-v3.1) |

## Repo map

| Path | Role |
| --- | --- |
| `WHITEPAPER.md` | Methods write-up (plain scientific English) |
| `PLAN.md` / `PREREGISTRATION.md` | Confirmatory specification |
| `FREEZE.md` | SHA-256 freeze snapshot |
| `types/conditions.json` | Four label-blind conditions + denylist |
| `modules/` | Compiler, grader, tests |
| `benchmark/` | Dataset builder + runner |
| `analysis/` | Mixed-effects H1–H3 report |
| `docs/` | GitHub Pages site |

## Reproduce (high level)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-analysis.txt  # optional
python3 -m unittest modules.test_compiler modules.test_runner_harness
# Full battery needs a local OpenAI-compatible server; set TABBY_API_URL privately.
python3 benchmark/run_battery.py --dry-run
```

Do **not** commit real inference host/port. Use `.env` locally (see `.env.example`).

## License note

Code and docs in this repository: see repository license settings / OSF project license (CC0 on OSF registration metadata).
