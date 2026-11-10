# T2 checkpoint — 20261110T0121Z-T2-scheduled-foam-rhs-failclosed-k6p9

- origin: scheduled
- issue: WATER-001; status: SOURCE_FIXED / synthetic verification pending
- start: 2026-11-10 01:21 UTC
- resumed_from: 20261109T2323Z-T2-scheduled-writer-rhs-scope-m7q2; latest preceding T2 published guard 86a19cab and tests df11e0e3; T2 state.json remains an older chat index.
- phone baseline: [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source e9c358eda01785b65e4eb14f18723da426635628; owner confirmed enter/save/reenter from artifact, delivery gate failed; CL source snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- issue baseline: WATER-001 OPEN. Phone session 220911-559 reported 23,884 water pass errors and 3,850 FFT kernel errors; 230108-327 reported 39,132 and 6,026 respectively. Do not infer GPU timing from HUD FPS.
- scope record: [work/20261110T0121Z-T2-scheduled-foam-rhs-failclosed-k6p9.json](../../work/WATER-001/20261110T0121Z-T2-scheduled-foam-rhs-failclosed-k6p9.json), commit c29f8caaef2cdae00eff452abdc7667480274df9.
- implementation: `scripts/t2_foam_rhs_origin_guard.py` at dc969d1695bec11e1e582fb971c72fe6c8e8d6e1; synthetic adversarial tests `tests/test_t2_foam_rhs_classifier_synthetic.py` at e52639eef70d0ed03add6c7bcb7741ae97577232.
- test command: `python -m unittest tests.test_t2_foam_rhs_classifier_synthetic` (or `python -m unittest discover -s tests -p 'test_t2_foam_rhs_classifier_synthetic.py'`). **Not executed on checked-out branch in this run**: local git network DNS unavailable; no new CI dispatched.
- technical boundary: only classifies *single producer* normalized CIL slices with conservative fail-closed handling of branches, unknown operations and multiple producers. It does not parse raw CIL, model the evaluation stack, establish cross-pass RenderTexture instance identity, infer alias from equal SSA signatures, or prove source/authentic ShaderLab/Adreno pixels. Source-only helper is not a water shader patch.
- overlap: no T3/T4/T5 files, game assets, native build request or workflow edited. T4 owns physical mouse capture, T5 Resolution and three-button placement; general touch layout deferred.
- next: run the synthetic tests on exact e52639e SHA, then use Mono.Cecil on SHA-pinned original managed DLL to extract *complete stack-correct producer slices* and reject all unresolved call/branch merges before using the helper. Coordinate actual pass1 RHS with concurrent T2 chat, and only then compare source-to-ShaderLab bindings. No READY claim.
