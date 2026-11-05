# T4 LOCAL-005 — source-authentic original RGD-derived local/field write sites (2026-11-05)

## Authenticated original baseline

Original ZIP2 immutable commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, `Raft/Raft_Data/Managed/Assembly-CSharp.dll` **3,211,776 bytes SHA256** `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`, checked again before Mono.Cecil metadata read. The experiment does **not** run original game methods, deserialize a user RGD, modify any source/asset/.meta, or emit original CLR identifiers, raw IL, RGD bytes or proprietary game payloads.

[T4 prior CI42058900699](https://github.com/alwansan/raf/actions/runs/42058900699) **SUCCESS 22/22** established structural immediate `Save(string,RGD)` arguments in exact original IL: `SaveWorld` pushes `LOCAL_DERIVED_RGD`, `SaveUser` pushes `FIELD_DERIVED_RGD`. The original seed `StreamingAssets/Data.rgd` root differs from `RGD` required by private `Save`, per [CI42047540260](https://github.com/alwansan/raf/actions/runs/42047540260), and must not be used as synthetic world-save input.

## Distinct question and actual result

The new probe determines where the exact **local slot** loaded just before `SaveWorld`'s genuine private Save call has direct lexical `stloc` sites, classifies the immediately preceding instruction of the *nearest lexical assignment*, and counts the **direct `stfld/stsfld` write sites** within the exact original managed assembly to the same field read just before `SaveUser`'s private Save call. It also bounds the field owner's declaring scope. It checks the original compiled method shape and SHA and never prints field names or IL.

[**FINAL CI42062124798**](https://github.com/alwansan/raf/actions/runs/42062124798) **COMPLETED SUCCESS** at source commit `cff6351d68c1941610dfabdc3b18ee0f77e7c8d4`:

- **36/36** source-free Python/adversarial schema and false-device-claim controls passed.
- .NET 8 / Mono.Cecil 0.11.5 C# source tool compiled, inspected exact authenticated original DLL; deliberate one-byte source SHA mutation was refused before inspection.
- `world_precall_class=LOCAL_DERIVED_RGD`; `world_local_lexical_store_sites=1`; `world_nearest_store_source_class=CALL_RETURN_DERIVED_RGD`: the exact local variable has one lexical original IL assignment before Save, with immediately preceding original IL returning a value of a type derived from `RGD`.
- `user_precall_class=FIELD_DERIVED_RGD`; `user_field_declaring_scope=SAVEANDLOAD_CLASS`; `user_field_direct_store_sites=3`: original SaveUser reads a field owned by SaveAndLoad with three direct stores across the authenticated original DLL (including nested original types where present).
- Explicit negatives: `argument_value_origin_proven=false`, `original_local_store_reached_save_at_runtime=false`, `original_user_field_initialized_at_runtime=false`, `gameplay_save_rgd_written_or_reopened=false`, `unity_android_il2cpp_or_phone_executed=false`. These are **lexical sites and type relations only**, NOT path-sensitive IL/SSA tracing. Actual branch execution, object data/identity, field init timing and serialization remain unknown.

The experiment does not prove the original method which returns the derived-RGD value, any full transitive call stack, executed world initialization, successful save or Android runtime correctness. Neither does it prove missing initialization. The additional finding reduces the next debugging scope: a specific **typed-return method feeding a local** for world save, versus the **SaveAndLoad-owned field with three direct store sites** for user save.

## Changes, regression and boundaries

- Source-only C# instrument: `android-port/Experiments/T4/OriginalRgdPrecallSlice/Program.cs`, commit [0e25b282](https://github.com/alwansan/raf/commit/0e25b282bd96d876a31a19b43300041d362cf72d).
- Bounded report/negative controls: `scripts/t4_validate_original_rgd_precall_slice.py` commit [189decf0](https://github.com/alwansan/raf/commit/189decf071208fa9e044361d3813f7520d0abdcb); `tests/test_t4_validate_original_rgd_precall_slice.py` commit [cff6351d](https://github.com/alwansan/raf/commit/cff6351d68c1941610dfabdc3b18ee0f77e7c8d4). Tests increased from 22 to **36** (14 new adversarial cases).
- Reused existing isolated path-triggered read-only workflow `.github/workflows/raft-t4-original-rgd-precall-slice.yml` without altering its shared resource behavior; `cancel-in-progress:false`, no artifacts or private payload published, no game Unity/IL2CPP/native build triggered. Intermediate runs [42061895812](https://github.com/alwansan/raf/actions/runs/42061895812) and [42062052526](https://github.com/alwansan/raf/actions/runs/42062052526) failed before all schema/tool/test updates were committed. Final matched-source success is CI42062124798; intermediate tool/test contract mismatches are **not** game runtime save failures.

## Integration handoff and unresolved acceptance

T4 scheduled session `20261105T1548Z-T4-scheduled-m7q4` independently owns JSONL UTC monotonic verifier source and remains outside this file scope; no edits or CI cancellation. T1/T2 own water/FFT, T5 native integration. Latest authored game native [run42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) failed at the **strict water gate** during reconstruct *before* an installable diagnostic build; no updated signed APK/OBB/XAPK was produced by that run.

Next original-source discrimination: identify the immediate call-return method's declaring scope and whether all SaveAndLoad field-write sites are initializer/in-world/nonexecuting, ideally under bounded privacy-preserving evidence, then coordinate one native candidate with T5 for real phone test. **Actual acceptance remains:** offline world playable -> genuine `.rgd` written/durable -> full exit -> same installation same-world playable reopen, with per-session markers. Preserve original save schema, GUID/.meta and real local host, never fake ready flags; audio and Settings regression-only, touch deferred.

**LOCAL-005 OPEN; overall NOT_READY 0/3.**
