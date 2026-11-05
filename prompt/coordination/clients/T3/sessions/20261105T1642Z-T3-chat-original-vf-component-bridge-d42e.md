# T3 chat — SHA-original Shader48 vertex/fragment component bridge

- session_id: `20261105T1642Z-T3-chat-original-vf-component-bridge-d42e`
- owner: T3; origin: **chat**; branch: `feature/android-native-port`.
- resumed_from_sessions: `20261105T1633Z-T3-chat-vf-component-coverage-b71d` (17/17 source-free tests), `20261105T1625Z-T3-scheduled-dxbc-contract-8f2c` (separate DXBC signature component contract).
- base_sha: `ad1b1f0d753bcf7a01ebd942dcb048ec7f0c23f8`; work registered before edit in `prompt/coordination/work/RENDER-002/20261105T1642Z-T3-chat-original-vf-component-bridge-d42e.json` at `22e8bd2a7b8de3ba6fd61c49b5b4711ebbea5f77`.
- issue_id: **RENDER-002 OPEN**; readiness NOT_READY, 0/3 immutable complete reviews; Android phone colors and original ShaderLab unverified.
- experiment_key: `T3-ZIP2-15964ea8-6scenes-4owners-Sh48-921-4pass-VF-SPIRVCross-Location-Component-typed-source-v-roundtrip-v1`.
- resource_key: `T3-921-fourpass-original-vkd3d-CPU`, not Unity build resource.

## Original evidence to resume from

Genuine source CI [42062573338](https://github.com/alwansan/raf/actions/runs/42062573338) translated exactly four original Shader48 V/F pairs (8 stages) from six SHA-pinned ZIP2 scenes/four owners selected by 921 original Renderer Material uses. Original→HLSL→SPIR-V stages all valid but reflected generated names survived **0/34 inputs, 0/29 outputs**; matching multisets do not prove original semantic identity. T3 scheduled latest `20261105T1625Z-T3-scheduled-dxbc-contract-8f2c` handles DXBC ISGN/OSGN input contract in different files. No interference with its scripts/tests.

## Implemented and verified source-free

- [Private original selector, reflection sanitizer and V/F component summary](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t3_original_921_vf_component_bridge.py) commit `aa5982c4fc881c7a09e1f040fe6675ebad1d0db5` — reuses authentic original high-use selector and fourpass exact-pair sample, keeps DXBC/SPIR-V/HLSL in temporary files, reconciles old safe SPIRV reflection by `Counter(Location,type)`, strips generated names and IDs, allows only known scalar/component aggregates and false proof flags.
- [17 additional source-free negative controls](https://github.com/alwansan/raf/blob/feature/android-native-port/tests/test_t3_original_921_vf_component_bridge.py), commit `d4869125b9363effd0b6a257326207d95254c140`: malicious labels/hashes, arrays, Location/Component collisions, drift, unsupported matrices, invalid side or malformed source corpus.
- [Isolated workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t3-original-921-vf-component-bridge.yml), original `5081a37400dc9c6cd2364ba8af31da4e1650c9fb`, scoped 5-min source-free CI on own files and optional 28-min original private fourpass run.
- **[CI42067757782](https://github.com/alwansan/raf/actions/runs/42067757782) SUCCESS**: 17 new + 17 prior tests (34/34), Python compile valid. Also [CI42068641959](https://github.com/alwansan/raf/actions/runs/42068641959) SUCCESS on later gated workflow revision; original private job intentionally skipped on this non-request push.

## Explicit authentic original experiment status at checkpoint

Direct workflow_dispatch is not exposed in this chat's GitHub connector; a unique SHA-blobs-pinned JSON request marker was used to trigger exactly one original opt-in run via path-scoped push. `on.push.paths` includes `.github/t3-original-vf-requests/*.json`, and a strict commit-message + marker-only diff test avoids accidental heavy runs from ordinary pushes. Request stores original ZIP2 pin and three exact script/test Git blob SHA values, no private source.

- YAML parsing failure (colon embedded in unquoted `if`): [42068542470](https://github.com/alwansan/raf/actions/runs/42068542470) failed with **no jobs**. Fixed via folded scalar at `b6027ff6e7bb26897692d0d9b23b93c9afa7e303`. The valid workflow [42068641959](https://github.com/alwansan/raf/actions/runs/42068641959) passed 34/34 controls.
- First explicit marker run [42068710185](https://github.com/alwansan/raf/actions/runs/42068710185) source-free passed but native-original job failed **before reading any Raft source**: shallow checkout had no parent for `git diff-tree HEAD`. Fixed original job checkout `fetch-depth: 2` and a safe failure label in `b3e6caeffdb4cfc592cf05526f5c0ae9b6aedbc5`.
- New marker-only push attempt 3 at `df1d56d385e6961d8d3442caf8d9a1cc43f190da`. **Run id/result not yet checked at this checkpoint**. Check Actions for workflow `T3 RENDER-002 original Shader48 VS-FS Location Component coverage` at commit `df1d56d`, then inspect jobs, safe aggregate artifact and original source validation. Do not launch duplicate while active.

## Important proof boundaries and team coordination

The new component test is narrower than DXBC source semantics: valid numeric SPIR-V Location+Component and scalar-family coverage is **not** evidence of interpolation, original DXBC register/semantic mask, all33 authentic source pairs, original authored ShaderLab, Unity pixels or corrected Adreno white materials. Unsupported array/matrix/64-bit layouts are declared inconclusive. Never print raw original names/code/SPV/HLSL/hashes in public logs/artifacts; only per-source-vs-roundtrip safe totals. Never force shared branch or edit others' active files.

At session start T5 complete native [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) was in progress; T1 FFT Vulkan [42066983894](https://github.com/alwansan/raf/actions/runs/42066983894) independent. Neither cancelled or restarted. Audio/Settings maintained; touch/layout deferred.

**Next:** check attempt 3 CI, inspect exact private original V/F source-versus-roundtrip numerical aggregate (4 original Passes) if SUCCESS, or diagnose new failure stage conservatively. Save final outcome in this session, experiment, event and work. Keep RENDER-002 OPEN until real shader integration/visual validation.

## Final genuine original confirmation — 2026-11-05 16:53 UTC

- The original marker-only push at `df1d56d385e6961d8d3442caf8d9a1cc43f190da` triggered [CI42068915602](https://github.com/alwansan/raf/actions/runs/42068915602), **COMPLETED SUCCESS**. Source-free 34 tests passed, explicit marker-only diff+three SHA public source blobs passed, genuine original six scene and four owner SHA verified (269007288 bytes), no LFS or duplicate Unity build. Full original private script produced source and HLSL roundtrip V/F component summaries.
- Exact genuine result: 4/4 sampled original Passes and 4/4 derived roundtrip Passes classified `STRUCTURAL_CANDIDATE_ONLY`; 0 structural deficits, 0 inconclusive. Original and roundtrip both **22 vertex output records (75 scalar components), 14 fragment input records (44 scalar components), 31 extra unused vertex components, 0 missing fragment lanes, 0 mismatched type lanes, 0 unsupported type records**. Eight original source/roundtrip stage reflection pairs completed.
- Public-safe artifact id `13435221320`, name `t3-921-original-VF-component-counts-42068915602`, size 939 bytes, retention 7 days. No original SPV, HLSL, shader names, private offsets, DXBC or asset bytes uploaded.
- Authenticated real result supports only **sampled SPIR-V typed Location+Component V/F structural coverage**, **not authored/original DXBC semantic mapping**, interpolation, pixel parity, Unity ShaderLab/Adreno visuals, shader installation or all 33 source variants. RENDER-002 **OPEN** and game **NOT_READY**.
- Permanent proof/constraints: [docs/T3_ORIGINAL_921_VF_COMPONENT_COVERAGE_2026-11-05.md](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_ORIGINAL_921_VF_COMPONENT_COVERAGE_2026-11-05.md), experiment `prompt/coordination/experiments/T3/20261105T1642Z-T3-chat-original-vf-component-bridge-d42e.json`, event `prompt/coordination/B_TEAM/events/T3/20261105T1642Z-T3-chat-original-vf-component-bridge-d42e.json`. Canonical RENDER-002 issue evidence merged while retaining status OPEN at commit `edd349232b2f53a945025049d7cdff55b9dfd943`.
- Distinct next step: scheduled T3's DXBC signature structure must be joined privately to the **same eight original Shader48 stages** by source signature register/mask/system-value; generated reflected name matches were 0/34 inputs and 0/29 outputs (CI42062573338), so do not invent semantics. Need independent interpolation/ShaderLab Pass state and material/sRGB/GPU evidence.
- No active T1/T2/T4/T5 file or workflow touched. Native/T5 [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) still in progress at last status inspection; T1 FFT [42066983894](https://github.com/alwansan/raf/actions/runs/42066983894) independent. Leave their jobs running.
- Scope status: completed for this source-authentic V/F **structural question** only, not restoration or game readiness.
