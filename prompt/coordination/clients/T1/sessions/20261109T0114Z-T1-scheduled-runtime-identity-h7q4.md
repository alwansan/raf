# T1 — WATER-001 runtime identity gate

- session_id: 20261109T0114Z-T1-scheduled-runtime-identity-h7q4
- origin: scheduled
- baseline: script blob 63d2004f7b96057a19430932c5f96ec71265a64e
- resumed_from: 20261109T0011Z-T1-scheduled-binding-duplicates-6a8d; 20261108T2022Z-T1-chat-fft-source-gate-d8b4
- scope: prompt/coordination/work/WATER-001/20261109T0114Z-T1-scheduled-runtime-identity-h7q4-runtime-identity.json
- owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md
- observation: owner successfully entered/saved/reloaded world from 42058825739 artifact; newer 2026-11-08 CL still reports 74,359 invalid water passes and 11,165 FFT invalid kernel errors. Numeric source argument 6 is NOT a Unity kernel ID.
- change: reject whitespace-only, padded, and ASCII control-containing device_session/kernel_name before treating runtime evidence as attributable. Existing GUID, FindKernel/Dispatch equality, and binding name checks retained.
- source commit: a989615ca843039a284851b2352bec3ff24a22db
- seven regression controls: 8269cd96c2d1bc3c89d09cda5812093029264639
- test status: NOT EXECUTED (this connector environment cannot run the repository test suite; no new CI dispatched). No GPU, Unity, Vulkan pixel, or Android evidence from this change.
- limits: validates evidence structure only; does not prove original FFT shader/kernel mapping, shader authenticity, resource binding, water rendering, or device acceptance.
- next: run `python3 -m unittest discover -s tests -p 'test_t1_fft_runtime_identity_h7q4.py'` on checkout/CI; capture same-build named ComputeShader GUID, kernel index from FindKernel, dispatch, bound resources, FFT size/bank, then first Vulkan-vs-Unity pass comparison. Preserve T4 physical mouse and T5 Resolution ownership.
- WATER-001: OPEN; NOT_READY 0/3.
