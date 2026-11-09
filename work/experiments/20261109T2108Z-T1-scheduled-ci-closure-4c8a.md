# T1 CI evidence closure — 20261109T2108Z-T1-scheduled-ci-closure-4c8a
origin: scheduled
baseline_sha: e983fbb5f7dad184a67bd90e790b4e9563591867
question: Did the pending 2026-11-09 T1 evidence-order tests actually pass?
method: read-only GitHub Actions run and job-step API; no re-run.
source_change: bdf57d929b39b96b3c3cfea24f3f4ab74babb950
tests_change: 0e63f88ed00e5e6ae4fbb16d14b4bf6c6309097a
result: run 42691010634 completed success (2026-11-09T20:14:28Z); run 42691034311 completed success (2026-11-09T20:14:36Z). In 42691034311 pinned-phone-evidence job success, Synthetic adversarial provenance tests success, Pinned public owner CL/test result success.
limits: this proves CI checks for synthetic evidence order/provenance, not authentic FFT resource binding, FindKernel/Dispatch, GPU readback, Vulkan-vs-Unity parity, or phone water. No CI rerun.
separate_other_issue: T2 evidence-refresh run 42697151936 failed at 20:53 UTC, unrelated and not attributed to T1. A full native delivery run 42696228231 remains in_progress at inspection; do not cancel or duplicate.
owner_evidence: run 42058825739 successful world enter/save/reenter from Artifact; 5 Nov 220911-559 water pass 23884 FFT kernel 3850; 230108-327 water pass 39132 FFT kernel 6026. 8 Nov CL LogRaft-20261108-164850-270 water pass 74359 FFT kernel 11165; never sum across sessions.
next: obtain authenticated original FFT kernel/program/resource table and compare first mismatching Vulkan/Unity pass with GPU readback; avoid additional audit-only changes without new evidence.
