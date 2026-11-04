# B19 — per-SubShader water pass structural gate, 2026-11-04

Session `20261104T2256Z-B19-hl7` / `WATER-001`. This is a source validation fix only; not restoration of original Spectrum, Foam, Blur, FFT or actual pixels.

## Demonstrated structural false positive

The previous `scripts/b49_shaderlab_pass_contract.py:pass_coverage` accumulated authored `Pass` bodies across every `SubShader` in one ShaderLab source. The water gate compared that **aggregate** to the log-derived minimum for water shaders (e.g. Spectrum6). A synthetic source having 2 passes in one alternative `SubShader` and 4 in another yielded aggregate6 and fully programmed=true, even though **neither individual SubShader has six passes**.

Unity documents that `Shader.passCount` is the pass count of the **active** SubShader, not a sum of alternatives: https://docs.unity.cn/2022.3/Documentation/ScriptReference/Shader-passCount.html ; for the project's Unity 2021.3 generation, https://docs.unity.cn/2021.3/Documentation/ScriptReference/ShaderData.Subshader.PassCount.html documents per-SubShader counts.

## Integrated changes

- [B19 parser commit 2c640cada](https://github.com/alwansan/raf/commit/2c640cada195c377962492e243352fe4f39b71f0): existing lexical Shader -> SubShader -> Pass brace scoping retained; now also counts/program-checks each completed direct-child SubShader independently. Adds `subshader_pass_counts`, `subshader_programmed_pass_counts`, `all_subshaders_programmed`, `active_subshader_runtime_verified:false`. The legacy aggregate `pass_count` is retained for diagnostics, no longer treated as runtime passCount.
- [B19 water gate b780d000](https://github.com/alwansan/raf/commit/b780d000dc5157c19078511927e681924907575a): `contract_satisfied` now requires every potentially active authored SubShader to have at least the required number of complete passes; conservative because the target Android device's selected SubShader cannot be inferred from static text. All preexisting SHA/GUID, no-placeholder and authenticity controls retained.
- [B19 synthetic tests 67aefcb6 and dff8de87](https://github.com/alwansan/raf/commit/dff8de87b651e30cc27719b1db239bbfe6528788), corrected HLSL fixture line breaks in [33ca3538](https://github.com/alwansan/raf/commit/33ca35381a2c88247dad928dcb5db0c4d1271ea6). Cases include 2+4 not counted as active six, 6+1 conservative rejection, correctly programmed alternatives, and an empty-program alternative.

## Validation and rejected mistake

[Final B49 source-only CI41930936302](https://github.com/alwansan/raf/actions/runs/41930936302) **SUCCESS at source SHA `33ca35381a2c88247dad928dcb5db0c4d1271ea6`**: 8/8 B49 tests plus 16/16 water source gate tests, with four added controls. Run command: `python3 -m unittest discover -s tests -p test_b49_shaderlab_pass_contract.py -v` and `python3 -m unittest discover -s tests -p test_verify_water_render_contract.py -v`.

Earlier [41930875672](https://github.com/alwansan/raf/actions/runs/41930875672) **FAILED one new assertion due to synthetic HLSL fixture containing literal escaped `\\n` rather than newline**. The fixture was corrected without relaxing any production guard; final test passed. Do not mislabel this as original game shader error.

## Boundaries

This is a **conservative** static minimum across all authored alternative SubShaders. Hardware selection, `UsePass` expansion, compiled GPU programs, draw state, material-to-shader GUID binding, original water pass order, FFT kernel execution and device pixels are **not** proved. This prevents one false structural readiness signal, not every possible false positive. No private original ShaderLab/DXBC, .meta/GUID bytes, game/audio/Settings/touch, Unity native request or APK changed. WATER-001/RENDER-002 and LOCAL-005 remain OPEN; NOT_READY 0/3 full independent immutable reviews. The latest real game remains APK86.

Next: compare original authenticated per-SubShader pass layout after actual restoration, identify active Android SubShader on a device build, and complete original FFT/shader resource bindings; do not substitute aggregate counts or dummy passes for original source.
