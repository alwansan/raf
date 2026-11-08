# T1 scheduled — 20261108T1410Z-T1-scheduled-trace-mutation-c9e4

- origin: scheduled; owner: T1; issue_id: WATER-001; experiment_key: T1-TRACE-SAME-SIZE-MUTATION-20261108-0da4625f.
- resumed_from_session: 20261108T1312Z-T1-scheduled-trace-shortread-q8m3; baseline_sha: 0da4625f2f21892c062dbd895e12c6ddeb48690f.
- Owner evidence read first: docs/DEVICE_FEEDBACK_42058825739_AR.md and its CL snapshot links. Run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628; phone world/save/reopen succeeded from artifact, packaging publication failed, water/kernel errors remain. Historical APK86 does not supersede.
- Read team instructions, owner requirements and previous T1 checkpoint; latest GitHub Actions listed run 42485092438 success, unrelated T3 run 42485049910 failed; no duplicate Unity build dispatched.
- Work plan commit: 9f94696d6de9c6826b517ac1e438b60e20d91011; source commit: ed3eb83589ef0774c670d3bcd79a2a08da0258b6; regression commit: 535a459f3d99269f8768a883d6fc02f9c5dd4884.
- Finding: the prior reader checked exact length and growth, but not an in-place same-size rewrite during read. Added descriptor fstat before/after consistency check of size, mtime_ns, ctime_ns. Added three regression tests (unchanged file, changed mtime, changed ctime). This is best-effort detection, not an atomic snapshot against adversarial races or same-timestamp rewrites.
- Verification: GitHub commits confirmed; regression tests **not executed in this session**. Do not treat source-only controls as original kernel identity or device proof.
- Latest observed branch HEAD before checkpoint: 535a459f3d99269f8768a883d6fc02f9c5dd4884; no Unity/GPU resource, APK build, cancellation, raw assets, or other T role modifications.
- Next: run `python -m unittest tests.test_t1_fft_trace_mutation tests.test_t1_fft_trace_short_read` on a full checkout or CI; check test failures. More important: capture authentic GUID/name/FindKernel/Dispatch/SetTexture evidence and paired Vulkan/Unity first divergent FFT pass. WATER-001 OPEN, NOT_READY 0/3.
