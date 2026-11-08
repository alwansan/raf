# T1 scheduled — 20261108T1910Z-T1-scheduled-axis-identity-f4c8

origin: scheduled
issue: WATER-001 (OPEN)
resumed_from: 20261108T1836Z-T1-chat-water-startup-order-c5e7; 20261108T1714Z-T1-scheduled-fft-shared-lab-b6d2
base_sha: efe39f647208dbe1d8f62d5f47a3d8922481187f
work: prompt/coordination/work/WATER-001/T1-20261108T1910Z-T1-scheduled-axis-identity-f4c8-axis-identity.json
experiment_key: fft-axis-identity-v1-synthetic-invocation-traces
resource_key: none
status: waiting_ci

## Owner evidence and newest context
- Device run 42058825739: owner entered, saved and reopened world from Artifact; package publish failed. Its CL sessions report water invalid-pass 23,884/39,132 and FFT kernel 3,850/6,026; not historical APK86.
- Newer pinned CL 61f71ceb session 20261108-164850-270: 74,359 water and 11,165 invalid-kernel root messages. T1 chronology source CI 42513165405 SUCCESS: first water and FFT messages precede world-loaded milestone by 64,486 and 64,484 ms. These counts do not establish the original Unity kernel name or water pixels.
- Shared Mini APK first run 42509945996 SUCCESS as ZIP; T1 device cases pending; r2 T1 NO_BUILD. No extra native build or Actions cancellation.

## Engineering
- Detected a false positive in synthetic paired FFT invocation diagnostic: axis_mapping([(1,1),(2,2),(3,3)]) previously marked uniform_translation true, even though addresses are identical. That could misleadingly implicate an address translation before inspecting actual Vulkan/Unity divergence.
- Fix commit [a120761](https://github.com/alwansan/raf/commit/a12076184214b348eaa8d1435730cde0f46a33da): require at least one changed coordinate before classifying uniform translation or reflection.
- Regression commit [fd55804](https://github.com/alwansan/raf/commit/fd558046592baba6af9c40bcb92bac80a45a31c8): direct identity axis and same-input paired invocation controls.
- Automatic existing T1 diagnostic CI [42513642491](https://github.com/alwansan/raf/actions/runs/42513642491) queued at checkpoint. An earlier automatic run 42513635469 was in_progress at previous source commit; do not cancel or duplicate.
- Scope isolated to scripts/t1_fft_trace_compare.py and tests/test_t1_fft_trace_compare.py; T2/T3/T4/T5 code untouched. No raw shader assets or device data published.

## Limits and next
This is a diagnostic false-positive fix, not original FFT shader restoration or actual FindKernel/Dispatch/numeric parity. Await exact CI verdict and correct any failure; then return to authenticated original Unity compute program mapping, same-build runtime binding and first-stage numeric comparison. WATER-001 OPEN; full Raft NOT_READY 0/3. Physical mouse buttons/scroll T4 and three buttons/Resolution T5 remain active per newer owner directions; general touch layout deferred.
