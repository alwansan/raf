# 20261110T1607Z-T1-scheduled-kernel6-isolation-8c42
origin=scheduled
role=T1
issue=WATER-001 OPEN NOT_READY 0/3
experiment_key=T1-KERNEL-INDEX6-SOURCE-ISOLATION-20261108-164850-270
resource_key=none; read-only CL evidence, no shared Unity/CI
intended_files=prompt/coordination/T_TEAM/work/20261110T1607Z-T1-scheduled-kernel6-isolation-8c42.md; prompt/coordination/T_TEAM/clients/T1/sessions/20261110T1607Z-T1-scheduled-kernel6-isolation-8c42.md
hypothesis=All 11,165 invalid-kernel root messages in 8 Nov session identify index_6, but index_6 cannot be equated to one of 20 compiled FFT candidates or to a named Unity kernel without asset/dispatch correlation. Distinguish water pass failures by material first.
owner_priority=docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reentry succeeded from 42058825739 artifact; publish failed; do not regress to APK86.
new_evidence=CL main raft log/lf/LogRaft-20261108-164850-270/session-summary.json final_render_failure_breakdown: spectrum=29700; foam_global=44659; subsurface_blur=0; utility_noise=0; invalid_kernel_index_root_lines index_6=11165 other_index=0. Sum 29700+44659=74359, exactly final invalid-pass count. This partitions material-pass errors, not unique failed draws. Kernel index is Unity runtime lookup index, NOT verified compiled FFT slot.
method=For the SAME immutable APK/build and CL session, isolate first raw 'kernel index (6)' message with surrounding ComputeShader/asset identity and C# callsite, correlate timestamp to FFT Dispatch and shader GUID. Independently collect first Spectrum and Foam invalid-pass lines and material/Pass indices. Only after verified original .compute GUID + kernel-name/FindKernel mapping, stage private GPU readbacks and existing numeric-first-divergence gate. Never assume index6 maps to compiled slot6.
coordination=T2 owns Spectrum/Foam pass restoration; T4 physical mouse clicks; T5 Resolution/three controls and shared lab distribution. No edits to their source or touch layout.
provenance=20261110T1506Z-T1-scheduled-native-binding-evidence-c7d2; B48 compiled candidate inventory inherited without promoting runtime identity.
status=read_only_evidence_confirmed; private runtime identity unresolved; no build requested
next=Obtain exact kernel-index6 log callsite/compute GUID from immutable CL segment and compare with original ZIP2 verified owner digest before a targeted Unity runtime probe.
