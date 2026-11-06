# T3 chat — Particle108 authored Shader48 default-value parity

- **session_id:** `20261106T1835Z-T3-chat-property-defaults-c42d`
- **origin:** `chat`; owner: `T3`; issue: **RENDER-002 OPEN / NOT_READY**
- **resumed_from_sessions:** `20261106T1818Z-T3-chat-shaderlab-prop-contract-37bd` (prior name/type only), `20261106T1828Z-T3-scheduled-contract-fixture-b6e1` (independent DXBC/SPIR-V explicit provenance work), `20261106T1756Z-T3-chat-cb-uniqueness-4f1a`
- **base_sha:** `f86e1ac9d651440bbb2aa98736dd01477ac65be9`
- **scope reserved first:** [work/20261106T1835Z-T3-chat-property-defaults-c42d.json](../../../work/RENDER-002/20261106T1835Z-T3-chat-property-defaults-c42d.json), commit [36f23730](https://github.com/alwansan/raf/commit/36f23730cdc85d029b3c5c72ee477634f4e6e9e5)
- **origin and experiment key:** `T3-PARTICLE108-SAMEEXPORT-SHADER48-PROPERTY-DEFAULT-SEMANTICS-c42d`; source-only, no native build or shared Unity resource.
- **trial vote:** T3 **لا يحتاج** in `trial-20261106-r1`; T4 alone had `يحتاج` in last table. No 5/5 consensus, no native request.

## Evidence and new code

Prior [CI42270269076](https://github.com/alwansan/raf/actions/runs/42270269076) proved 15/15 synthetic Shader48 authored property *name/type* gates, but a changed default RGB color, float, Range lower/upper bounds or texture fallback was invisible if name and type matched. The exact original author property text is already privately reconstructed by `t3_particle108_source_propstate.serialize_properties` and only compared in the same GUID-verified W1/B02 AssetRipper export by `t3_particle108_shaderlab_export_quality.classify`.

Changed these **public-safe validators**:

- `scripts/t3_particle108_shaderlab_property_parity.py`: strict finite numeric tuple parsing for 4-component Color/Vector, Float/Int, Range current value + both limits, texture quoted fallback + empty modifier block. Numeric spellings (`1`, `1.0`, `1e0`) decode to the same numeric value, **without approximate tolerance** that could hide source-default drift. Reject NaN/non-finite, malformed vector, unexpected texture block or unsupported value. Output remains aggregate counters and booleans only: `matched_name_type_different_default`, `original_authored_property_defaults_semantically_equal`. Source names/values are not serialized or printed.
- `scripts/t3_particle108_shaderlab_export_quality.py`: if private original properties are supplied and same-export shader is non-dummy, a default mismatch now returns **`AUTHORED_PROPERTY_DEFAULT_MISMATCH`** before source-only structural pass acceptance. Existing dummy/no-subprogram failure precedence remains; no false executable shader claim. `source_to_export_authored_property_defaults_match` is an independent flag.
- `tests/test_t3_particle108_shaderlab_property_parity.py`: five regressions for changed Color default, Range bounds/scalar, Texture fallback, equivalent numeric spellings, malformed/non-finite values.
- `tests/test_t3_particle108_shaderlab_export_quality.py`: source-only same-export synthetic positive-identity/mismatched Color default must reject structurally complete shader. No original property default bytes in fixtures.

Commits: initial [207e1287](https://github.com/alwansan/raf/commit/207e1287674a750fb6c364510b57971f41cf1e8e) accidentally produced malformed replacement due JS `$'` string-replacement token; [CI42272416082 failed](https://github.com/alwansan/raf/actions/runs/42272416082). Corrected file atomically from baseline + intended patch in [59b9e9f4](https://github.com/alwansan/raf/commit/59b9e9f4c0e1c6f0cd68f7658612141dd63b6bf6), then integration [70b45cf4](https://github.com/alwansan/raf/commit/70b45cf448724c50a93f216bf421223abe758d6f), regressions [2653e5f6](https://github.com/alwansan/raf/commit/2653e5f6c836ce13d1d3ed31a6c348ced506dfd2) / [9aeebcd4](https://github.com/alwansan/raf/commit/9aeebcd42d427080257a348e38ab6d249692c743).

**Terminal validation:**
- [CI42272706523 SUCCESS](https://github.com/alwansan/raf/actions/runs/42272706523), job `128081101924`: **19/19** property-parity synthetic unittest assertions, Python compile.
- [CI42272760367 SUCCESS](https://github.com/alwansan/raf/actions/runs/42272760367), job `128081291316`: **16/16** same-export shader-quality synthetic unittest assertions, Python compile.
- No CI was cancelled; no native Unity/APK/OBB/XAPK build requested; no external game assets changed.

## Limits, integration and next step

This closes a **validator-fidelity blind spot only**. It does **not** show that an original non-dummy Shader48/HLSL pass has been reconstructed, or that exact default values from a real original → AssetRipper export have been compared in this run. No actual project ShaderLab/Material/Texture was changed; no graphics, Android GPU pixels, water/fire/smoke or save tests conducted. `original_property_default_or_material_value_equivalence_proven` remains false as no Material instance-value comparison was made. Read game owner phone report [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) as world/save/reentry only, not current color success.

Scheduled T3 `20261106T1828Z-T3-scheduled-contract-fixture-b6e1` owns `scripts/t3_dxbc_spirv_contract_join.py` and test; its next action is to run its untested fixture. **Do not overwrite/duplicate its files.** If it has completed an original per-stage DXBC/SPIR-V semantic join, the next T3 renderer step is to integrate a *real source-authenticated non-dummy Shader48 program* for the original four VS/FS keyword variants, then rerun the same W1/B02 exact original→export flow with both property default + stage resource mapping gates. Only then run Unity shader compilation and owner Adreno pixel checks. Do not trigger a trial APK for diagnostic-only scripts. Preserve original .meta/GUID/.rgd, FMOD and Settings, leave touch deferred; maintain **RENDER-002 OPEN/NOT_READY** and trial vote **لا يحتاج** until major game render integration is real.

- **work:** `prompt/coordination/work/RENDER-002/20261106T1835Z-T3-chat-property-defaults-c42d.json`
- **experiment:** `prompt/coordination/experiments/T3/20261106T1835Z-T3-chat-property-defaults-c42d.json`
- **event:** `prompt/coordination/B_TEAM/events/T3/20261106T1835Z-T3-chat-property-defaults-c42d.json`
