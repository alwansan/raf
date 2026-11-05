# T3 chat — non-null Shader48 built-in transport guard, end-to-end synthetic CI

- **identity:** T3
- **origin:** chat
- **session_id:** `20261105T2102Z-T3-chat-builtin-null-pointer-0d3e`
- **resumed_from_sessions:** `20261105T204947Z-T3-chat-program-coverage-b6f2`, `20261105T2034Z-T3-scheduled-7c91`.
- **base_sha:** `fe9a9ae5264821304923d6bac04d21089f3a3df8`; scope registered under `prompt/coordination/work/RENDER-002/20261105T2102Z-T3-chat-builtin-null-pointer-0d3e.json` **before edits**, commit `ee2460c907ffa084b94a50d450618b3a7229f6a1`.
- **issue_id:** RENDER-002 (still OPEN, NOT_READY). **status:** completed (strict source-free guard only).
- **experiment_key:** `t3-source21-shader48-native-top921-builtin-null-zero-fileid-and-guid-contract-v1`.
- **resource_key:** null (small source-free checks, no Unity/ZIP2 original download).

## Last verified evidence and non-overlap

The previous T3 source-free ShaderLab pass guard passed CI [42107128075](https://github.com/alwansan/raf/actions/runs/42107128075) (52/52) and left original 921-use Shader48 -> private full-native export GUID match unrun. Latest owner phone report [DEVICE_FEEDBACK_42058825739_AR](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md) confirms actual new-world entry/save/reentry for a particular newer APK artifact, but water/white materials remain unresolved. Historic full native exporter aggregate: 110/142 ShaderLab Dummy, 770/1536 Material docs target Dummy, without definitive original high-use shader attribution. T1's exact Unity FFT sampled input CI [42108071145](https://github.com/alwansan/raf/actions/runs/42108071145) was in progress at last action check and was not modified, duplicated or cancelled.

## New concrete defect and correction

`scripts/t3_source_renderer_shader_to_postvendor_export.py` previously categorized any `(guid in BUILTIN, type=0)` as engine shader without checking `fileID > 0` or excluding all-zero GUID; `BUILTIN` includes `000..000` for generic null use. The private source→native authoritative join could falsely credit a nonzero-fileID all-zero GUID as a valid Unity built-in for one of 21 genuine source Shader48 objects. The top-921 wrapper had the same broad predicate. An actual `fileID=0` is already rejected earlier by `scripts/verify_export_lineage.pointer`; the new guard is defense-in-depth for file ID and closes the remaining all-zero GUID / negative-ID path. Do not imply zero fileID was previously accepted.

Implemented `VALID_BUILTIN_GUIDS = BUILTIN - {all-zero GUID}` with required positive `fileID` in both source→export and high-use top classification, retaining valid nonzero Unity builtin `fileID=46` and custom Shader48 handling. Commits: [source predicate](https://github.com/alwansan/raf/commit/dc3f3ea04347ae98ce8e8ff05517d9fadb795c1c), [top predicate](https://github.com/alwansan/raf/commit/c52603ff0fd48f747764f908ce957e03335c5522), [source boundary tests](https://github.com/alwansan/raf/commit/adb44e55ffefce4dce549b67df9b9e5f1784a812), [native top boundary tests](https://github.com/alwansan/raf/commit/0cd715181fbf9b86caac88527d78940d8b3f5f91), [test assertion correction](https://github.com/alwansan/raf/commit/96c04389c4f636712a2d896e0e9662f21bd90f5a).

Separate CI maintenance change [8ff409fe](https://github.com/alwansan/raf/commit/8ff409feafc56188ab7f462b814d13849d576d04) adds both previously omitted source→export join file and its existing test file to the isolated T3 workflow's push path filters; it already ran those tests but source-only edits were not sufficient to trigger the workflow.

## Actual tests and prior failures

Stale intermediate [42108313304](https://github.com/alwansan/raf/actions/runs/42108313304) and [42108337297](https://github.com/alwansan/raf/actions/runs/42108337297) FAILED source-free because new negative regression expected `unresolved_or_wrong_actual` for `fileID=0`, while the earlier shared `pointer` guard correctly raises `Null or malformed trace export pointer`. Fixed only assertion routing to preserve both strict guards. **This is a test expectation error, not observed shader restoration regression or original-resource defect.**

Final exact workflow SHA `8ff409feafc56188ab7f462b814d13849d576d04`, [CI 42108532173](https://github.com/alwansan/raf/actions/runs/42108532173), job `127529698524`, **COMPLETED SUCCESS**. Python compile passed. Three source-free unittest suites PASSED **24 native 921 + 14 source→same-export + 16 material/ShaderLab = 54/54**. Original source, private W1 trace and actual Unity export NOT exercised here. No genuine program equivalence, material color recovery, original top-921 status after full restorers, Vulkan rendering or Adreno pixel proof.

No original game binaries/shaders, .meta, GUID, Unity scenes, APK/OBB, build request JSON, sound, Settings, touch or saves modified. No heavyweight CI launched. Existing T1/T2/T4/T5 jobs remain independent.

## Handoff / next

When a future authentic same-process T5 native export runs, execute scripts/t3_native_original_921_shader_target_audit.py with independently SHA-verified ZIP2 six scenes/four owners and W1 private trace plus postrestorer exported project. Only publish allowlisted aggregate source→target result. Then recover missing genuine ShaderLab Pass/subprogram/variant links and verify Unity+phone pixels. No duplicate full build.

Save this unique session for the scheduled T3 cycle and do not overwrite its file. Work completed, no resource lock and no CI waiting. `RENDER-002` remains OPEN and release READY cannot be inferred.
