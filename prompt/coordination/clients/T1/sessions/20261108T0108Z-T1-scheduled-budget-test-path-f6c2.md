# T1 20261108T0108Z-T1-scheduled-budget-test-path-f6c2
origin: scheduled
issue_id: WATER-001
base_sha: work reservation commit fe9e752f83a6f6189dd9872e84600b202cc9f520
resumed_from_sessions: 20261107T2306Z-T1-scheduled-fft-budget-c8e2; prior T1 dispatch coverage handoff (chat)
owner_phone: docs/DEVICE_FEEDBACK_42058825739_AR.md, run42058825739 source e9c358eda01785b65e4eb14f18723da426635628; owner entered/saved/reentered world from Artifact, publication failed. CL pinned 520c4cf, 220911-559 23884 water pass /3850 kernel, 230108-327 39132 water pass /6026 kernel. This is not FFT kernel identity proof.
work: prompt/coordination/work/T1/20261108T0108Z-T1-scheduled-budget-test-path-f6c2.md
finding: scripts/test_t1_fft_capture_budget.py used Path(__file__).resolve().parents[1] / 't1_fft_first_divergence.py', which resolves to repo root; actual script is scripts/t1_fft_first_divergence.py. All three subprocess tests previously targeted a nonexistent file, preventing meaningful regression verification.
fix: replace parents[1] with parent in test-only SCRIPT constant; commit 7577eb37729c2fb286981ce1e24693599fc8a075. No production code, .meta, shader, Unity or runtime modified.
verification: static path reasoning and exact source review; no test run verified in this environment (container GitHub DNS unavailable). Do not claim green tests. Need run python3 -m unittest scripts.test_t1_fft_capture_budget on checked-out exact commit; run tests for dispatch coverage separately.
coordination: no Actions launched or cancelled; no native build, no T4 mouse or T5 buttons/Resolution changes. No numerical Vulkan/Unity parity or actual FindKernel/Dispatch binding proven.
next: execute corrected regression test, capture authentic kernel GUID/name/dispatch trace and paired original Vulkan/Unity inputs; find first divergent FFT pass. WATER-001 OPEN; NOT_READY 0/3.
