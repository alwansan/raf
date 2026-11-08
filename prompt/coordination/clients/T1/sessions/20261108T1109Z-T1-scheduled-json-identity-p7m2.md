# T1 scheduled — 20261108T1109Z-T1-scheduled-json-identity-p7m2

- origin: scheduled
- identity: T1; branch: feature/android-native-port
- Scope: WATER-001 / T1-FFT-TRACE-JSON-DUPLICATE-IDENTITY.
- Owner source of truth: docs/DEVICE_FEEDBACK_42058825739_AR.md, owner phone run 42058825739 at e9c358eda01785b65e4eb14f18723da426635628; world entry/save/re-entry confirmed by owner from Artifact, not proof of new source or graphics. Water pass/kernel errors remain; delivery publishing failed.
- Prior checkpoint: T1 20261108T0811Z kernel trace plan; later T1 consistency checker commits 988ccbfd and 70cf9dd, tests cd2bfef6/a3e019d. Current code was read from branch before change.
- Trial policy: trial-20261106-r1, no T1 substantial water fix; no new native request, no Actions cancellation.
- Hypothesis: json.loads silently overwrites duplicate keys in recorded FindKernel/Dispatch manifests. An attacker or faulty logger could record both indices/names and checker would inspect only the last.
- Change: scripts/t1_fft_trace_consistency.py rejects duplicate keys at every object nesting level via object_pairs_hook before check(); regression tests tests/test_t1_fft_trace_duplicate_keys.py (5 controls). No original shader, GUID, meta, scene, world, input, audio, Settings, or raw asset changed.
- Work scope commit: 940adfcbcb1c7355a857a353b6b075b4674347d2.
- Code commit: a9e58e04fe350d05af5afb0b668fb1d331489da2; tests commit: b803973b1ace5639f581f5ba5fbf46f511022212.
- Verification: GitHub commits confirmed. Local git checkout unavailable (DNS github.com failure), and new tests have not been run on full repository; status SOURCE_FIXED / CI_UNVERIFIED, not device confirmed.
- Remaining: link authentic Unity .compute GUID and kernel names with recorded FindKernel/Dispatch; collect matching original RGBA32F Vulkan and Unity capture, compare first divergent FFT pass. Existing owner CL water counts are diagnostic, not proof of exact failing kernel.
- Readiness: WATER-001 OPEN, NOT_READY 0/3. Do not claim this guard restores water. T4 owns physical mouse, T5 owns three buttons/Resolution.
