# T1 scheduled — 20261108T1312Z-T1-scheduled-trace-shortread-q8m3

- origin: scheduled; owner: T1; issue: WATER-001; experiment: T1-FFT-TRACE-SHORT-READ-20261108.
- Owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358eda01785b65e4eb14f18723da426635628; actual owner phone world entry/save/reopen succeeded from Artifact; water pass/kernel errors remain and package publishing failed. Do not substitute historical APK86.
- Read live AGENTS.md, CURRENT_OWNER_REQUIREMENTS, STATUS, T_TEAM operating instructions and trial policy; T1 prior session 20261108T1109Z and legacy state/MEMORY. Other T roles retain physical mouse, three buttons and Resolution; no touch layout development.
- Initial branch HEAD ac6208be78505fdee102dd5445056fe0e185da6d. Work plan commit ef7cca9d066a3301db51acf8a110e84e92bd97f6; no shared GPU/Unity resource.
- Finding: a single os.read(fd, MAX_MANIFEST+1) is not guaranteed to return all bytes even on a regular file. This can truncate a valid trace and obscure the actual kernel evidence. Fix uses bounded exact-length loop, rejects early EOF and growth beyond fstat size; no original asset or runtime changes.
- Source commit 7d473b344784761da71fd7bc1f92c2193866a5e9; regression test commit cca91cc8b7e892dc71c2da8c95ab036f97bc0e3e; fixture correction 857c7d83e9c3b6b2bf059a33b5c097adf97edf04.
- Controls added: short reads (3-byte chunks), truncation after fstat, growth after fstat. **Not executed in CI or local full checkout during this session**. Source-level change only, not proven Unity kernel binding.
- Current HEAD observed before session checkpoint: 857c7d83e9c3b6b2bf059a33b5c097adf97edf04. No new Unity build, APK/OBB/XAPK, cancellations, raw game binaries, or team file edits.
- Trial r1 T1 remains «لا يحتاج»: no integrated authentic FFT water repair. Readiness WATER-001 OPEN, NOT_READY 0/3.
- Next: execute python -m unittest tests.test_t1_fft_trace_short_read (or unittest discover -s tests -p test_t1_fft_trace_short_read.py); fix any failures; collect authentic Unity FindKernel/Dispatch GUID/name and matching Vulkan/Unity RGBA32F captures, identify first divergent FFT pass. Do not mistake synthetic controls for device proof.
