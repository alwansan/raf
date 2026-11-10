# 20261110T1506Z-T1-scheduled-native-binding-evidence-c7d2
origin=scheduled
role=T1
issue=WATER-001 OPEN NOT_READY 0/3
baseline_sha=0e8ff0111d214b53d20da55e5f14814a6535d8b5
experiment_key=T1-FFT-NATIVE-BINDING-DEVICE42058825739-SOURCE-e9c358eda01785b65e4eb14f18723da426635628
resource_key=none (read-only evidence inventory; no Unity/CI)
intended_files=prompt/coordination/T_TEAM/work/20261110T1506Z-T1-scheduled-native-binding-evidence-c7d2.md; prompt/coordination/T_TEAM/clients/T1/sessions/20261110T1506Z-T1-scheduled-native-binding-evidence-c7d2.md
hypothesis=Existing metadata integrity gates cannot establish original FFT GUID/FindKernel/Dispatch binding; device log errors must be matched to immutable source and stage before numerical attribution.
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
observations=220911-559 water pass errors 23884 and kernel errors 3850; 230108-327 water pass errors 39132 and kernel errors 6026. These are message counts in separate sessions, not unique kernels or causal proof. 42058825739 reconstructed and phone world/save/reentry succeeded from artifact; package publishing failed.
independence=T4 physical mouse and T5 Resolution/three buttons untouched; no touch layout change.
status=active
next=Obtain original FFT .compute GUID and kernel name/order from verified ZIP2 source, map actual Unity FindKernel calls and resource binding, capture same-build Vulkan/Unity GPU readbacks; run existing integrity tests before claiming first numeric mismatch.
