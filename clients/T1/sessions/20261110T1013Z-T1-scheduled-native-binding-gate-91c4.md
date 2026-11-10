# T1 scheduled session — 20261110T1013Z-T1-scheduled-native-binding-gate-91c4

origin: scheduled
baseline_sha: 028957e91ec1624bdfd121e45b698d113ea3de50
work_registration_commit: 352d9010239f40eea61df29a71ae9eb28b302efd

## Verified this cycle
Read owner phone report `docs/DEVICE_FEEDBACK_42058825739_AR.md` first, then current owner requirements, T_TEAM instructions and current FFT audit/tests. Source branch head was 028957e91ec1624bdfd121e45b698d113ea3de50 at read. Inspected GitHub Actions recent runs: 42788071163 successful, head f7da4de0a024cc8ea5fc3ec411f481c7e65642a6; later regression tests at 70e8cbd are NOT covered by that run. No duplicate CI launched.

The current source logger explicitly emits `original_findkernel_callsite_present=false`, `original_runtime_mapping=unverified`, `gpu_result=unverified`. Therefore neither passing pairs nor synthetic FFT GPU tests establish the original Unity FFT resource/kernel binding. This is an evidence gap, not a reason to alter authenticity flags. Need original .compute GUID/kernel mapping and same-build readback to compare Vulkan/Unity first divergent pass. Do not use the two device sessions' aggregated error counts as a causal timeline.

Owner 2026-11-05 phone result 42058825739: world entered, saved and reentered from artifact; publish/delivery failed. T4 physical mouse and T5 three buttons/Resolution are separate live scopes; do not overwrite their work. 2026-11-08 shared lab instruction supersedes individual APK experiments.

## Work performed
Created independent T1 work scope at `clients/T1/work/20261110T1013Z-T1-scheduled-native-binding-gate-91c4.md` with exact experiment key and proof requirements. No code changed, no Unity build, no GPU proof and no phone test. Status WATER-001 OPEN / NOT_READY 0/3. The decisive source asset mapping and paired GPU readback are not present in reviewed material, so a source-only claim of repair would be false.

## Next step
Find verified original FFT compute asset GUID and original callsite in ZIP2/Unity graph, then instrument real FindKernel + Dispatch with session/build provenance, binding metadata and readback. Compare each pass numerically and identify the first mismatch. Run new tests on a SHA that contains them, or reuse equivalent existing CI if available. Recheck branch HEAD and active team scopes before any change.
