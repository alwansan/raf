# T2 WATER-001 scoped work
session_id: 20261110T0620Z-T2-scheduled-rhs-opcode-normalization-k7p4
origin: scheduled
base_sha: 54fd9143eda9a10b6ac9f29879e98f8caa0985d9
issue_id: WATER-001
experiment_key: t2-foam-rhs-opcode-input-safety-v1-source-free-20261110
resource_key: none (Python source-only)
status: completed (source-only; no original/device proof)
intended_files: scripts/t2_foam_rhs_origin_guard.py; tests/test_t2_foam_rhs_classifier_synthetic.py; this work file; independent session file
hypothesis: unexpected opcode formatting may bypass the fail-closed producer classifier, and the existing tests must be executed against the current live source before further original-CIL integration.
constraints: no Unity/CI/ShaderLab/asset changes, no raw game data, preserve T3/T4/T5 scopes. This is not evidence of water rendering.
resumed_from: 20261110 earlier T2 scheduled guard commit 160c77efc6c41c7181ae2df63e395b3dec8c5ea1; test commit 4307592c7ff1c3946fe437b20d5f05155010075d.
owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md (world/save/reopen succeeds; water/FFT remains broken).

Result: short-form opcode classification merged in 804c61b963e49865c758066ace0e4356264d706f; regression cases in d3848e969918c82a8f1c30b340813ab3a447a4a9; session e75eb41d26bcceea1e977ebb92290b745b2adbe1. Next: full repo unittest on fixed SHA and original Mono.Cecil operand/CFG validation. WATER-001 remains OPEN NOT_READY 0/3.
