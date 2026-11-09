# T2 WATER-001 stage key strictness
session_id: 20261109T1616Z-T2-scheduled-stage-key-guard-v7q2
origin: scheduled
scope: scripts/t2_foam_resource_abi.py; tests/test_t2_foam_resource_abi.py; own session only.
Baseline: previous evidence guard commits 359774d and b4be53d, latest session 1cd9524. Owner device report 42058825739 read first; world/save/reentry confirmed, water FFT open, package publication failed.
Hypothesis: Python bool is int subclass; (False,0) can alias pass0/stage0 in dictionary membership, and (0,False) can alias stage0. A forged report could pass numeric tuple key checks without genuine typed stage identifiers. Test fail-closed strict integer stage key validation; avoid shader, T3, shared files, Unity and Actions duplication.
Experiment: synthetic report tampering of pass/stage_code with booleans and floats; reject before original stage mapping. No claim of original resource identity or device pixels. Coordination: isolated own Python script/test, no shared GPU/Unity resource.
Next: execute targeted source-free tests in CI when no equivalent run active, then continue original Foam texture provenance.
