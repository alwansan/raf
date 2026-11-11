# T1 scheduled session 20261111T0110Z-T1-scheduled-marker-boundaries-6f42
origin=scheduled

## Evidence and baseline
Owner device feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358eda01785b65e4eb14f18723da426635628, CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Owner entered, saved, exited and re-entered world from artifact 42058825739; package publication failed. WATER-001 remains OPEN. 220911-559: 23884 water pass / 3850 kernel messages; 230108-327: 39132 / 6026. Counts are messages, not distinct faults; index 6 is not a proven Unity kernel identity.

## Scope and changes
Scope: work/T1-20261111T0110Z-T1-scheduled-marker-boundaries-6f42.md. Initial HEAD 143cbb5da365cd2762428536fd0e91ab3a62f0ce; observed HEAD at closure 99efa8451719c72817bb625dd753b57b258d97fd. Fixed regex false-positive on prefixed tokens such as subkernel #6; made FindKernel, Dispatch and water-pass diagnostic counts case-insensitive, consistent with context marker matching. Source commit db2ac1c0f42feca710226809101170232868910d. New synthetic regression commit 4671c8b6996e878440686c4a2c04838fc668f925; newline fixture correction 99efa8451719c72817bb625dd753b57b258d97fd.

## Validation and limitations
Source and test are committed; Python repository regression not executed in this environment because direct git/github.com DNS resolution fails. No CI was launched; no Unity/phone GPU test, no original FindKernel/Dispatch mapping or numerical Vulkan-vs-Unity parity claim. No T4 mouse or T5 Resolution files changed; no shared build resources reserved. Existing actions were read-only checked; no duplicate action triggered.

## Next
Run `python -m unittest scripts.test_t1_kernel6_marker_boundaries scripts.test_t1_kernel6_context_window scripts.test_t1_kernel6_real_line_proximity` on a checked-out branch or cheap isolated CI only after overlap review. Then execute tool on each CL session with --errors-only and compare first true kernel6 error context to original ComputeShader GUID/FindKernel/Dispatch mapping. Prioritize authentic FFT binding and first numeric mismatch, not further speculative regex tweaks.
