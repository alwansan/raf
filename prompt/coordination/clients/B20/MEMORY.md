# B20 — working memory

- Identity: B20, session 20261104T2230Z-B20-6c9a; owner-authorized branch `feature/android-native-port` only.
- Startup HEAD: `5fc5c4838247c33669bba8b67e988893f22cd28e` (2026-11-04T22:20Z). Latest actual game release `android-early-test-41812889049-1` / APK versionCode86; no newer phone evidence verified. CL review 2026-11-04 has original water pass/FFT failures and SaveGame→Steam StoreStats exception; source logs and images cited in B_TEAM/REVIEW_2026-11-04.md. Audio and Settings owner-confirmed; touch deferred.
- Read: B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, SUMMARY.md, REVIEW_2026-11-04.md, TEMPLATES.md, issues/WATER-001.json, AGENTS.md, owner requirements, prompt README/continue/status and ZIP2 provider. No original shader bytes copied, no private asset published.
- Live Actions review: latest visible branch runs 41923703800 and 41923703812 SUCCESS, no running job in first 25 latest; original B18 FFT SPIR-V validation is source/translation evidence only.
- Assigned gap WATER-001: strengthen `scripts/b49_shaderlab_pass_contract.py` water **source-only** Pass scope verification, preventing fake authored Pass tokens in non-SubShader scopes or ShaderLab malformed braces from satisfying the prebuild diagnostic. B49 prior source guard supports syntax but not GPU or originality. Check upstream test contracts before changing. Distinct from B18 bindings, B24 Foam, B30 FFT selector, B45 original Blur.
- Hypothesis: global regex `Pass\s*{` can count token outside a `SubShader`; a staged fake candidate could fool structural counts despite being invalid ShaderLab. Reject synthetically and add CI before claiming SOURCE_FIXED.
- Active work record: `prompt/coordination/work/WATER-001/B20-20261104T2230Z-B20-6c9a-shaderlab-scope.json`.
- Do not change original assets/.meta/GUID, audio, Settings, touch, Unity request or any other agent's workflow.
- Next: add strict scope controls, run tests, commit and record result; WATER-001 stays OPEN, READY 0/3.


## Checkpoint — 2026-11-04T22:35Z

- Source guard merged: [a21d66b](https://github.com/alwansan/raf/commit/a21d66bc9122bba432c2c6d021e096b7f988abcc). `Shader -> SubShader -> Pass` lexical brace ancestry is now required before any water Pass is counted; old global Pass regex false positive rejected. No private source, .meta/GUID or original assets modified.
- Synthetic regression file [ed059c2](https://github.com/alwansan/raf/commit/ed059c2fa1ee25c5de3b6cf9a4fe645f08c61ed2) tests ten cases; own bounded workflow [2e4cabd](https://github.com/alwansan/raf/commit/2e4cabd5e8d801dc25f85b1b12e02cdb0a20b7e3).
- [B20 CI41926202371](https://github.com/alwansan/raf/actions/runs/41926202371) SUCCESS (B20, B49, water source regression test step), [B49 CI41926043987](https://github.com/alwansan/raf/actions/runs/41926043987) SUCCESS, [runner guard41926202314](https://github.com/alwansan/raf/actions/runs/41926202314) SUCCESS. CI does NOT verify original shader or Android water.
- [Evidence report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/B20_SHADERLAB_SCOPE_INTEGRATION_2026-11-04.md). Experiment B20-shaderlab-scope-20261104 completed stage SOURCE_FIXED; WATER-001 remains OPEN. Need pinned original Foam/Spectrum and FFT selectors actually integrated into transient Unity export with device comparison, reuse B18/B24/B45.
- Only latest Raft game release verified remains [APK86](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1). The CL 4 Nov screenshot and segment3 referenced in B_TEAM review are older installedVersionCode86: no post-fix water/device acceptance. Preserve current owner-working audio and Settings; do not touch input.
- Handoff limitation: no local clone/network in container; shell `git ls-remote` failed DNS. All source commit and Actions validation was through connected GitHub API and GitHub Actions, NOT local Unity/GPU. Summary generator requires repository runner; do not manually forge snapshot or claim it was regenerated.
- Next barrier: original water program and FFT binding authenticity, then live Unity import/device. Completed source-scope work is a narrow enabling fix, not an overall WATER-001 closure.
