# B20 WATER-001 — ShaderLab Pass scope guard (2026-11-04)

## Baseline / input

- Branch `feature/android-native-port`; initial HEAD `5fc5c4838247c33669bba8b67e988893f22cd28e`.
- Latest real game delivery reviewed from B-team owner review: [APK86 run 41812889049](https://github.com/alwansan/raf/actions/runs/41812889049), dated 2026-11-04. Owner CL device log records Spectrum/Foam/Blur pass failures and FFT kernelCount=0. No new Android APK/device evidence is part of this change.
- Existing B49 checker matched `Pass { ... }` globally; the B20 synthetically reproducible hypothesis is that such text outside a `Shader -> SubShader` can inflate the prebuild source-only coverage count.
- Actual original asset acquisition: **none**; original serialized identity, ShaderLab payload, private HLSL/DXBC, GUIDs and settings unchanged. Source pin for future original verification remains ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

## Integrated source change

- [a21d66b](https://github.com/alwansan/raf/commit/a21d66bc9122bba432c2c6d021e096b7f988abcc): `scripts/b49_shaderlab_pass_contract.py` now masks comments/quotes, checks a named Shader block followed by direct SubShader children, counts only Pass blocks immediately inside a proper SubShader, and detects unmatched enclosing braces. Matches complete CGPROGRAM/ENDCG or HLSLPROGRAM/ENDHLSL pairs inside each counted Pass.
- [ed059c2](https://github.com/alwansan/raf/commit/ed059c2fa1ee25c5de3b6cf9a4fe645f08c61ed2): 10 new B20 source-only synthetic cases for valid/multiple subshaders, orphan or Properties Pass, inline HLSL nested braces, comment and quote masks, malformed parent braces.
- [2e4cabd](https://github.com/alwansan/raf/commit/2e4cabd5e8d801dc25f85b1b12e02cdb0a20b7e3): separate B20 workflow, Ubuntu 24.04, 5-minute timeout, no original assets, Unity, native APK or device.

## Validation

- [B20 CI 41926202371](https://github.com/alwansan/raf/actions/runs/41926202371): **SUCCESS** on `2e4cabd5e8d801dc25f85b1b12e02cdb0a20b7e3`, including B20 controls plus B49 and `verify_water_render_contract` regression tests.
- [Preexisting B49 CI 41926043987](https://github.com/alwansan/raf/actions/runs/41926043987): **SUCCESS** on `a21d66bc9122bba432c2c6d021e096b7f988abcc`.
- [Runner compatibility 41926202314](https://github.com/alwansan/raf/actions/runs/41926202314): **SUCCESS** on B20 workflow SHA.
- Rejected hypothesis: a lone syntactically plausible `Pass` outside Shader/SubShader can be treated as an authored pass. It now has zero authored Pass count, with the negative cases passing.
- **Not established**: original shader bytecode authenticity, authored subprogram execution, original material bindings, Unity import, Adreno GPU pixels, FFT kernel routing, playable world, or any new device acceptance. `native_ready` authenticity flag is unchanged; WATER-001 and RENDER-002 remain OPEN, project NOT_READY (0/3 complete reviews).

## Follow-up

Next highest-value action is integration of a genuinely original water/FFT shader program and verified binding into the transient exported Unity project, with original GUID/pass/CB/texture/kernel identity preserved, then Unity/device pixels. Existing B24 Foam stage, B18 FFT resource roles and B45 Blur staging should be reused, not cloned. No changes to audio, Settings, deferred touch, other workflows or native requests.
