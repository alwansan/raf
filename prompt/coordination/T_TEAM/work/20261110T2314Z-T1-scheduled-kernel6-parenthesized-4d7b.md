# 20261110T2314Z-T1-scheduled-kernel6-parenthesized-4d7b
origin=scheduled
role=T1
issue=WATER-001
baseline_head=475a748870d7af906445945e16667a3b2352764a
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; Artifact 42058825739 world/save/reentry succeeded, publishing failed.
experiment_key=T1-K6-PAREN-001
hypothesis=Kernel error lines containing 'kernel index (6)' or 'kernel #6' can escape existing strict index recognizer; test parser only, do not infer kernel identity.
files=scripts/t1_kernel6_log_context.py; tests/test_t1_kernel6_parenthesized.py; this work and matching session only.
shared_resource=none; no Unity/CI/APK dispatch; T4 mouse and T5 Resolution/buttons excluded.
taken_over_from=20261110T2210Z-T1-scheduled-kernel6-negative-context-c3e8.md
validation=isolated synthetic regex regression, no original runtime GPU evidence.
status=source_fixed; regex smoke PASS for 5 synthetic variants; full unittest NOT RUN (repository network unavailable locally)
source_commit=f048563edf22701684332bcb2e67e949d63f2af2
test_commit=cee85c0b190435261195456919ba5a27b5ef7736
next=run python -m unittest tests.test_t1_kernel6_parenthesized and pinned CL session extraction; then original GUID/FindKernel/Dispatch mapping
