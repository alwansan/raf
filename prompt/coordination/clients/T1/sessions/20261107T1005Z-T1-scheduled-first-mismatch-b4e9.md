# T1 checkpoint — 20261107T1005Z-T1-scheduled-first-mismatch-b4e9
origin: scheduled
base_sha: 958ab2c600ab122904c0a19c447c1184643a426b
resumed_from_sessions: 20261107T0821Z-T1-scheduled-trace-redaction-a6f2; 20261107T0710Z-T1-scheduled-schema-5e2a
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739; CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57
issue: WATER-001
scope: prompt/coordination/work/WATER-001/20261107T1005Z-T1-scheduled-first-mismatch-b4e9.md
result: Source audit confirmed comparator already scans coordinate and numeric mismatches together in trace-key order, so no redundant source patch was applied. Added two distinct regression cases in scripts/test_t1_fft_first_mismatch_order_b4e9.py at commit 0e94ac912c8c972dd8b78dbcb93fb58075c7b8ca. Tests cover numeric mismatch at invocation 0 followed by coordinate mismatch at invocation 1, and reverse case. Source sha blob 96f8e148223b78a591bad163b78f4f75514e9f75.
verification: tests committed but not executed on runner; no GPU/Unity/device validation. Git clone unavailable in local container (DNS). No CI requested; preserve running jobs. Existing comparison correctness is source-reviewed only.
phone: owner confirmed world enter/save/exit/reopen on artifact 42058825739; water errors 23884 passes/3850 kernels in 220911 and 39132 passes/6026 kernels in 230108. Physical mouse T4 and resolution/buttons T5 remain separate scopes.
next: execute the regression tests with repository Python environment, then prioritize genuine Vulkan/Unity captures with matched fixture and original FindKernel/Dispatch resource mapping. Check HEAD and T1 work overlap first. No build request; readiness NOT_READY 0/3.
