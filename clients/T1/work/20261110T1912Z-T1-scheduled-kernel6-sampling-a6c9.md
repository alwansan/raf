# T1 work — 20261110T1912Z-T1-scheduled-kernel6-sampling-a6c9
origin=scheduled
baseline_sha=72027bb9e8fa80235332fa57c6140a0781ea812c
experiment_key=T1-KERNEL6-ERROR-FIRST-SAMPLING-20261110
scope=scripts/t1_kernel6_log_context.py; tests/test_t1_kernel6_log_context.py; clients/T1/sessions/20261110T1912Z-T1-scheduled-kernel6-sampling-a6c9.md
hypothesis=The bounded first-N sample currently admits non-error kernel mentions, hiding later actual errors. Introduce error-only sampling without altering legacy counters or raw-log privacy.
shared_resource=none; CI=none; full APK=none.
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md, run 42058825739: world save/reentry success from Artifact, publishing failed. Kernel index 6 identity unknown. T4 mouse and T5 resolution/buttons are separate scopes.
