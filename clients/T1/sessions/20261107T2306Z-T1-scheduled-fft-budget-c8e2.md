# T1 session 20261107T2306Z-T1-scheduled-fft-budget-c8e2
origin: scheduled
baseline_sha: bbd2b39f96e42dd9e946e01a4d2463befc5a4e91
scope: WATER-001; FFT private comparison input budgeting
owner_phone_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; artifact 42058825739 world enter/save/reenter success, publish failed. CL 520c4cf: 220911-559 23884 water-pass/3850 kernel; 230108-327 39132 water-pass/6026 kernel. No inference kernel6 == FFT.
work: prompt/coordination/work/T1/20261107T2306Z-T1-scheduled-fft-budget-c8e2.md
implementation: scripts/t1_fft_first_divergence.py MAX_PASSES=32 and MAX_TOTAL_CAPTURE_BYTES=128MiB, preflight sum before capture reads. New scripts/test_t1_fft_capture_budget.py tests 33 passes, sparse 2x64MiB duplicated twice, and small valid match.
commits: plan bd7115e68f27d54aac3ac3b854d528c3553ffdbf; code 435d58ffb4cbb80df7077ed5839f22c22abda45e; tests f3c68d26752f8c4b49f8af64c3dec9ab7888b9e7.
verification: source changes published; regression tests not yet executed on branch. Not Unity, Vulkan, GPU or device evidence.
coordination: T4 physical mouse, T5 buttons/Resolution untouched; no native request, no duplicate Actions.
next: run python3 -m unittest scripts/test_t1_fft_capture_budget.py on exact SHA; investigate authentic FindKernel/Dispatch identity and paired Vulkan/Unity pass captures. WATER-001 OPEN; NOT_READY 0/3.
