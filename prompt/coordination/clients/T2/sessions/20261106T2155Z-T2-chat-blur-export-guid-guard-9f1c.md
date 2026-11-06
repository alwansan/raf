# T2 — inherited B45 Blur unique exported Shader GUID transaction guard

- session_id: 20261106T2155Z-T2-chat-blur-export-guid-guard-9f1c; origin: chat; status: active; base_sha: ebbdf7917eb581d5a6379a95afdd86f0613d2fd5; issue: WATER-001.
- resumed_from: 20261106T2148Z-T2-chat-cb0-array-bounds-5bc1; 20261106T2138Z-T2-chat-foam-matdoc-82bd.
- taken_over_from: B45 Blur original installer tests and shader properties; previous author retired by owner, attribution preserved.
- separate running original Foam source CI: https://github.com/alwansan/raf/actions/runs/42300107157; owner native: https://github.com/alwansan/raf/actions/runs/42296450023. This work does not touch either flow or rerun them.
- hypothesis: target Blur shader can have valid unique name but duplicate exported GUID in unrelated asset .meta; installer currently lacks GUID-inventory collision preflight and might promote candidate into ambiguous reference graph.
- scope before code: `scripts/b45_install_original_blur.py` and `tests/test_b45_install_original_blur.py`, no game/private source/assets.
- existing source-only workflow: `.github/workflows/raft-b45-blur-install-check.yml`, timeout 4min, no Unity/LFS.
- next_step: fail closed on GUID collision and unsafe redirected unrelated sidecar before backup, run red/green tests and record CI.

## Verified source-only result — 2026-11-06T21:56:08.545Z
- Code SHA [52dc2c6a](https://github.com/alwansan/raf/commit/52dc2c6a8410f24893342a3b8c7db9db2c920522); only inherited Blur installer `scripts/b45_install_original_blur.py` and its own synthetic tests changed. Before backup creation, validate no other exported `.meta` reuses target shader GUID; refuse redirected metadata.
- [CI42300619078](https://github.com/alwansan/raf/actions/runs/42300619078) SUCCESS on exact SHA, **12/12 tests**, including new collision rejection, distinct GUID accepted with byte-identical target meta, redirected unrelated sidecar rejection; job 128177120717. Secondary [B20 atomic rollback CI42300619027](https://github.com/alwansan/raf/actions/runs/42300619027) SUCCESS auto-triggered on the same source SHA.
- No original Blur SHA-pinned source candidate was generated or installed by this synthetic-only run. B45 original private candidate hash and real original shader asset remain unchanged. No Unity importer/Adreno pixels or runtime material binding proof; WATER-001 OPEN, NOT_READY.
- Work `prompt/coordination/work/WATER-001/20261106T2155Z-T2-chat-blur-export-guid-guard-9f1c.json` completed. Experiment `prompt/coordination/experiments/T2/20261106T2155Z-T2-chat-blur-export-guid-guard-9f1c.json`; independent event `prompt/coordination/B_TEAM/events/T2/20261106T2155Z-T2-chat-blur-export-guid-guard-9f1c-result.json`.
- Next: authentic export GUID scan and original candidate install only under T5 coordinated Unity run with private sources verified and independent phone pixel evidence.
