# 20261107T2005Z-T1-scheduled-kernel6-identity-91af
origin=scheduled
issue_id=WATER-001
resumed_from_sessions=20261107T1919Z-T1-scheduled-auth-bridge-6f2c; 20261107T1806Z-T1-scheduled-boundary-a7c9
base_sha=6b442d3c4c5f6aea18c4290cfec08b47b55cf14e
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md
device_baseline=Owner entered world, saved, exited and reopened from 42058825739 artifact (source e9c358eda01785b65e4eb14f18723da426635628); publishing failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
work=prompt/coordination/T_TEAM/work/T1/20261107T2005Z-T1-scheduled-kernel6-identity-91af.md
change=0384786057bcaa32403c9a576d4ad8d1c0504097 scripts/t1_kernel_index_identity_gate.py
regression=15a40fc16dcb86283543ea525512a11401cff0dd tests/test_t1_kernel_index_identity_gate.py
result=Added independent structural gate that rejects identification of FFT from Kernel Index 6 alone, requiring pinned source SHA, Unity ComputeShader GUID, kernel name, matching FindKernel/Dispatch indices, dispatch dimensions, and original program/resource fingerprints. Tests cover incomplete evidence, mismatched indices, boolean index, and invalid group counts.
verification=Source and five regression fixtures published; not executed (container GitHub DNS resolution failed). STRUCTURAL_ONLY result is explicitly not numeric or GPU/device proof.
limits=No original matched Vulkan/Unity capture, no actual Unity kernel table or shader GUID attested. No Unity, native build, release, or device test. WATER-001 remains OPEN and readiness NOT_READY 0/3.
coordination=Only new T1 script/test/work/session paths; T4 physical mouse and T5 buttons/resolution unchanged.
next=Run python -m unittest discover -s tests -p test_t1_kernel_index_identity_gate.py -v in GitHub checkout. Then populate evidence from original FFT program SHA and Unity FindKernel/Dispatch runtime instrumentation, not from LogRaft integer alone; run numerical paired capture to first mismatch.
