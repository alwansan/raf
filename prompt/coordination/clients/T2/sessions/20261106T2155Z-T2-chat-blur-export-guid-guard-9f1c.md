# T2 — inherited B45 Blur unique exported Shader GUID transaction guard

- session_id: 20261106T2155Z-T2-chat-blur-export-guid-guard-9f1c; origin: chat; status: active; base_sha: ebbdf7917eb581d5a6379a95afdd86f0613d2fd5; issue: WATER-001.
- resumed_from: 20261106T2148Z-T2-chat-cb0-array-bounds-5bc1; 20261106T2138Z-T2-chat-foam-matdoc-82bd.
- taken_over_from: B45 Blur original installer tests and shader properties; previous author retired by owner, attribution preserved.
- separate running original Foam source CI: https://github.com/alwansan/raf/actions/runs/42300107157; owner native: https://github.com/alwansan/raf/actions/runs/42296450023. This work does not touch either flow or rerun them.
- hypothesis: target Blur shader can have valid unique name but duplicate exported GUID in unrelated asset .meta; installer currently lacks GUID-inventory collision preflight and might promote candidate into ambiguous reference graph.
- scope before code: `scripts/b45_install_original_blur.py` and `tests/test_b45_install_original_blur.py`, no game/private source/assets.
- existing source-only workflow: `.github/workflows/raft-b45-blur-install-check.yml`, timeout 4min, no Unity/LFS.
- next_step: fail closed on GUID collision and unsafe redirected unrelated sidecar before backup, run red/green tests and record CI.
