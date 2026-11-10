# T4 INPUT-005 scope 20261110T0643Z-T4-scheduled-eligibility-contract-m8q5
origin: scheduled
session_id: 20261110T0643Z-T4-scheduled-eligibility-contract-m8q5
base_sha: de94af945c2ef98be68e4816c7c7bc1a87bfabb1
issue_id: INPUT-005
status: active
intended_files: tests/test_t4_capture_eligibility_contract.py; prompt/coordination/clients/T4/sessions/20261110T0643Z-T4-scheduled-eligibility-contract-m8q5.md
experiment_key: t4-eligibility-transition-source-contract-be31b553-20261110
resource_key: none (source-only, no Unity build)
hypothesis: the new pointer-capture eligibility telemetry must preserve all four gate bits, emit only transitions, and never change native request/keyboard behavior.
coordination: T5 owns Resolution and shared mini APK; T4 owns only physical mouse capture. Existing owner-confirmed world save/reopen on artifact 42058825739 preserved; no .rgd changes.
next: add source-contract tests; run locally; no duplicate Actions.
