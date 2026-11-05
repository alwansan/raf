# T3 scheduled — native ShaderLab empty-program fail-closed guard

- session_id: 20261105T1831Z-T3-scheduled-profileguard-7b2e
- origin: scheduled
- resumed_from_sessions: 20261105T1815Z-T3-chat-native-source921-guid-6cb4; 20261105T1730Z-T3-scheduled-rawspv-gate-c8e1
- base_sha: e76f703de2d778425154a6f97d0cb64a8a462768
- issue: RENDER-002 OPEN / NOT_READY 0/3
- scope: prompt/coordination/work/RENDER-002/20261105T1831Z-T3-scheduled-profileguard-7b2e.json (registered dba45291fde380d76d051387cac96c2bde533aab)
- experiment_key: T3-native-921-source-profile-no-subprogram-failclosed-synthetic-v1; resource_key: none.

## Diagnosis and change

The existing original 921-use Shader48 → postrestorer native GUID join classified any profile with dummy=false as NON_DUMMY_NATIVE_PROGRAM_AUTHENTICITY_UNPROVEN, even when no_subprograms=true or programmed=0. This was a concrete false-positive path for shader recovery prioritization: absence of the Dummy marker does not imply an executable ShaderLab subprogram.

- d62e5a609e00fc59dd822a9db6de0f05388765f4: fail closed with non_dummy_native_shader_without_subprograms for contradictory marker-free/empty profiles. No game shader changed.
- 1f4e0d4b3ec4e0906a6203bfe923fde76c2fc0ef: add source-free negative controls for no_subprograms and zero programmed passes, plus a dummy-marker positive control. Existing non-Dummy with real programs remains allowed.
- This guard is scoped to private SHA-original top Shader48 join; no original source bytes/GUIDs are published.

## Verification and limitations

At session start HEAD e76f703de2d778425154a6f97d0cb64a8a462768; latest source-free original native identity CI42083469621 SUCCESS 45/45 on earlier commit 93c5ad45, not evidence of the new guard. New guard CI result **not yet verified**. The authentic private same-invocation top Shader48→full-native GUID experiment remains NOT RUN; source-free controls cannot establish whether top original Shader is actually Dummy in native export, Unity compiles it, or Android pixels match.

Earlier full-native T5 scanner observed 110/142 exported shaders marked Dummy and 770/1536 Material docs linked to Dummy; these aggregate counts cannot be attributed to top original 921 source slots without private join. No Unity/native dispatch, cancellation, assets, .meta, GUID, audio, Settings or touch edits.

## Next

Check CI for 1f4e0d4b3ec4e0906a6203bfe923fde76c2fc0ef or later; if failed, inspect failure without relaxing the fail-closed rule. When T5's full-native export private trace and SHA-pinned source are available together, run the exact native GUID join once with the newly guarded profiles. Only then prioritize real ShaderLab restoration and device visual validation. Keep RENDER-002 OPEN and NOT_READY 0/3.
