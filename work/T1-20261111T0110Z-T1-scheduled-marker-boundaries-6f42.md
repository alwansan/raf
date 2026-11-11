# T1 scope — 20261111T0110Z-T1-scheduled-marker-boundaries-6f42
origin=scheduled
Issue WATER-001. Baseline HEAD 143cbb5da365cd2762428536fd0e91ab3a62f0ce (recheck before edits).
Source: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
Files: scripts/t1_kernel6_log_context.py and isolated scripts/test_t1_kernel6_marker_boundaries.py; clients/T1/sessions/20261111T0110Z-T1-scheduled-marker-boundaries-6f42.md.
Hypothesis: kernel6 token matching lacks a left word boundary, so unrelated prefixes (e.g. 'subkernel #6') inflate counters. Counters for water passes and FindKernel/Dispatch use inconsistent case-sensitive checks despite case-insensitive marker detection. Test bounded redaction and avoid claiming original kernel identity.
Experiment key: T1-KERNEL6-MARKER-BOUNDARY-20261111; shared resources: none; no CI launch, no APK. T4 mouse and T5 Resolution untouched.
