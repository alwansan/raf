# T1 WATER-001 — scheduled checkpoint
session_id: 20261108T2106Z-T1-scheduled-firstpass-name-preflight-5c21
origin: scheduled
resumed_from_sessions: clients/T1/sessions/20261108T2006Z-T1-scheduled-firstpass-json-4a7d.md; prompt/coordination/clients/T1/sessions/20261108T2022Z-T1-chat-fft-source-gate-d8b4.md
base_sha: ce5859d7ee7aff1911b43064727f7ea02bb0af9f
issue: WATER-001 OPEN; readiness NOT_READY 0/3
owner_source: docs/DEVICE_FEEDBACK_42058825739_AR.md, run 42058825739 (e9c358eda01785b65e4eb14f18723da426635628); successful phone world/save/reentry from Artifact; Actions publish failure. CL 220911-559 water23884/kernel3850 and 230108-327 water39132/kernel6026, different sessions and not a normalized regression.
work: clients/T1/work/20261108T2106Z-T1-scheduled-firstpass-name-preflight-5c21.md
fix: https://github.com/alwansan/raf/commit/9ac294ff37bb5f34f7190058d45189f15d91c093
regression: https://github.com/alwansan/raf/commit/8eebe992e6d6802a064f83e19b07f85b6f6694a2
scope: reject blank/duplicate FFT pass labels in manifest preflight before reading private pixel captures; two unittest cases use mock read_private_capture to assert zero reads on invalid labels.
validation: source inspection only. Local container could not resolve raw.githubusercontent.com to execute tests. Existing CI 42523525581 was running for earlier source SHA 9ac294ff, does not include new test SHA; no duplicate CI launched.
limits: does not establish original Unity FFT shader resource, FindKernel, runtime numeric kernel ID, Dispatch success, Vulkan/Unity numeric match, or phone water success. T4 mouse/T5 Resolution untouched; unified mini policy retained.
next: run tests/test_t1_fft_pass_label_preflight.py and inspect 42523525581; request same-build original FFT first failure capture (shader GUID, index, dimensions, bindings and Dispatch) via coordinated T5 full game build, then numeric first-pass comparison. Do not re-run unchanged source-only original kernel6 test (42519853981 success 30/30).
