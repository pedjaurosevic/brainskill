# BrainSkill freeze snapshot

**Status:** FROZEN for confirmatory preregistration
**Freeze time (Europe/Belgrade):** 2026-09-09 22:52 CEST
**Git tag:** `brainskill-freeze-v3.1`
**Git commit:** *(filled after freeze commit; see tag)*
**Public repo:** https://github.com/pedjaurosevic/brainskill
**Live model id at freeze check:** `Muse-Glimmer-30B-exl3-2.00bpw`
**Inference endpoint:** local OpenAI-compatible server on loopback (host/port via private env only; not published)

After this freeze: do **not** edit prompts, rubrics, graders, `dataset.json`, or `conditions.json` for confirmatory runs. Bugfixes that change scoring require a new freeze version.

## Artifact hashes (SHA-256)

| File | Bytes | SHA-256 |
| :--- | ---: | :--- |
| `PLAN.md` | 12035 | `a9fd9c93693c66715d0b50abce061edee7df70c5956533f0147a39c7188e4a6a` |
| `PREREGISTRATION.md` | 4333 | `ecc5b59bafe1da8692abb9a320e0629567ad8017037e3f367828ff4b63a8fc62` |
| `WHITEPAPER.md` | 13389 | `1fdd9e0a49912db31f0ecf19b5d24a681e03652881eb0e86cbe349a6aa736889` |
| `RED_TEAM_AUDIT.md` | 3912 | `90aaae979742100ea33f825cff8a6eb9b5018407ce7935bd9602c6de23d5636b` |
| `SKILL.md` | 2054 | `f807e7a100323612f9b9f0bd5245b9cd498cf09c8f1faf9709f9ef52a13894bf` |
| `NOTE.md` | 4620 | `7774b14cd69520da87ed7b94d6fc1aca5f768d6e61532aca71f917ed49a931e6` |
| `types/conditions.json` | 3600 | `76179e1bd48a3a986f02317ef043bf96737a930d9a69547c620689b792d90f1e` |
| `types/jungian.json` | 7549 | `1ad97c6aa439b6fc8f9a24bb7d968e6899fb38f3f042f1f79ac5f02de02c7ea6` |
| `types/ALTERNATIVE_PARADIGMS.md` | 5836 | `484f01104d1ac5dadb6b8fdf13c555c53af8054217fdaade7c71ca1e5e7379ac` |
| `modules/compiler.py` | 2546 | `59d37d9d1e7560f7cbf2659a7319913341e734fec826906ffc02058f8081d63d` |
| `modules/grader.py` | 4861 | `a9791418d86f03305a9beb5d6af8375164fff8a3a27bb5cebbd6d3e7dbccdd62` |
| `modules/test_compiler.py` | 7000 | `94f385a7df032cbb34356d7da885789291c1822440f36a3e960ee9cd35550d77` |
| `modules/test_runner_harness.py` | 3040 | `b1eb64c3d6bd16fbb455e56385138cb634c98a606a2cab58cb001d48d90df5dd` |
| `modules/__init__.py` | 256 | `47f7e1c178806f17dcfbc299d9e5938cfcc924dd26611776e549111b0916c323` |
| `benchmark/dataset.json` | 64400 | `bb3ab75a3701064642c8694610b579cb28ebb0167cc371ce4d5048e2e5a3d086` |
| `benchmark/build_dataset.py` | 49961 | `c4c67baf30193c8ef67c6a14a0ec16603011ed96e32b39c6aded84d53d19d23b` |
| `benchmark/run_battery.py` | 20057 | `e21fd66b592a1802d23beb960e3fd8ea4d7606d0d9de9dca0a3023cae02819b9` |
| `benchmark/BENCHMARK.md` | 3200 | `eb0793925726281cdf4f929fdbf14d18c198f6b2db606404d32ffca7ba6513fb` |
| `benchmark/TESTING_METHODOLOGY.md` | 3154 | `39ecb30a8de51ea17dce057ed62e8262690b7e75bf464bb1eefab40645b42ccc` |
| `library/PAPERS.md` | 2493 | `3ab86d6f1503525b773ab50f82626ab36f46ae7f0fa76a89b2b195f91d08a94d` |
| `.env.example` | 81 | `a94fdddedee970f0627e180fe9c9007f2a66d5d8fc2797b598a4dbf3072e5c6f` |
| `.gitignore` | 165 | `e5fdb1d1c30e76d737bec14d53eaa1e31022f3416d9de5462f9dcd24e0ca057c` |

## Freeze checklist

1. Compiler / grader / harness tests pass — **done** (13 tests).
2. Domain-2 tool-loop smoke recorded (`d2.01` cot RAG OFF ≈ 73.34 s) — **done**.
3. Live model id recorded above — **done**.
4. Hashes recorded in this file — **done**.
5. OSF / Zenodo upload of this tagged commit — **next**.

## How to verify

```bash
git checkout brainskill-freeze-v3.1
python3 -m unittest modules.test_compiler modules.test_runner_harness
sha256sum benchmark/dataset.json types/conditions.json benchmark/run_battery.py PLAN.md PREREGISTRATION.md WHITEPAPER.md
# compare digests to the table above
```
