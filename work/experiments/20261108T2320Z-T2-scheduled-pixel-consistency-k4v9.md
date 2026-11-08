# T2 scope — 20261108T2320Z-T2-scheduled-pixel-consistency-k4v9
origin: scheduled
issue_id: WATER-001
base_sha: 724d80cda6a249fedfa4096eebad0c6c8c68a96c
resumed_from: clients/T2/sessions/20261108T2120Z-T2-scheduled-gles-evidence-q6m2.md; clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md
intended_files: scripts/t2_gles_device_jsonl_gate.py; tests/test_t2_gles_device_jsonl_gate.py; own work/session
experiment_key: T2-CASE02-RGBA-NUMERIC-RELATION-20261109
resource_key: none
hypothesis: CASE02 currently accepts arbitrary RGBA arrays whenever marker tokens are present; reject inconsistent source/final pixels and no-contrast output.
scope: independent synthetic evidence gate, not original water/ShaderLab and not T3/T5 UI.
status: completed_source_change_tests_pending
updated_at: 2026-11-08T23:20:00Z

result: Added strict numeric CASE02 RGBA arrays (4 channels 0..255), source/final <=2 tolerance, nontrivial contrast; two regression tests with four invalid variants and one valid tolerance-2 case.
commits: bb29d1af2b2d603a6bcee2ab1b8414eca4572be3; 65dddd277c19f9e31eed1f79ea369c82dafc3efc; aa7b4f70c117a387fa489101948f56ae6d539def
verification: Read back published regex and smoke-checked same expressions against known synthetic CASE02 detail locally; full Python unittest NOT EXECUTED (container cannot resolve github.com); no CI dispatch.
limits: validates only reported text, not authenticated pixels or Raft shaders; source-original pass1 CFG and CB0 remain open.
next: execute python -m unittest tests.test_t2_gles_device_jsonl_gate and run gate on four CL original JSONL exports; coordinate with T3 on effects; avoid duplicate Mini build.
