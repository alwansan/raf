# T3 chat — source-only ParticleSystemRenderer negative PPtr CI

- session_id: `20261108T1556Z-T3-chat-particle-ci-c83f`; origin: **chat**
- created_at: 2026-11-08T15:52:00Z
- issue: RENDER-002 (OPEN)
- resumed_from: `20261108T1529Z-T3-scheduled-neg-fileid-q7m2` (scheduled code + fixture); `20261108T1540Z-T3-chat-gles-material-lab-6b2a` (separate completed mini lab).
- base_sha: `7800e28583679d5e23825818b0ea5120b9d8b33f`
- work record: `prompt/coordination/work/RENDER-002/20261108T1556Z-T3-chat-particle-ci-c83f.json`
- intended files: `.github/workflows/raft-t3-native-material-shader-quality.yml`; unique own work/session/event documents.
- experiment_key: `t3-particle-renderer-negative-material-fileid-postpatch-python-regression-ci`
- concurrent check: 0 queued and 0 in-progress Actions before scope; T4/T5 other files were not modified.

## Measured result

The previous T3 scheduled negative material `fileID` classification patch `b4f7d645` and fixture `3825975d` were not covered by prior [40/40 CI42485092438](https://github.com/alwansan/raf/actions/runs/42485092438), which predates the patch. Registered new independent source-only CI scope before editing existing lightweight T3 workflow.

Commit `8e92718a2855c65b00a17a661504f5149c229170` added script/test path filters and runs `tests/test_t3_particle_renderer_yaml_audit.py` plus Python syntax compile without touching parser logic, game resources or the T3 GLES lab.

[CI 42496973989](https://github.com/alwansan/raf/actions/runs/42496973989): **SUCCESS** on exact commit. 16/16 postrestore shader quality + 8/8 Material Shader links + **3/3 ParticleSystemRenderer tests** (including negative Material fileID) + 8/8 W1 shader export + 8/8 B49 pass contract = **43/43** source-only Python tests; py_compile success. This is positive verification of *the actual previously untested T3 source patch*, not game or original asset pixels.

## Bounded next step

Authenticated original→export ParticleSystemRenderer material list → Shader/Texture keywords/blend/alpha triage (private source as allowed) and actual Android GLES lab owner comparison. Do not classify synthetic PASS as correct fire/dark smoke textures, full scene materials, Unity, phone or READY. No new full XAPK, no source asset/decompiled shader publication, no changes to T4/T5 or other branches.
