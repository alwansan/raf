# T2 scheduled session — 20261105T2225Z-T2-scheduled-cfg-malformed-6f2c

origin: scheduled
resumed_from_session: 20261105T0023Z-T2-foam-texture-identity (state.json historical; later T2 commits 1624818/220a329/24d490c/e156a1f considered)

Owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md: phone successfully entered/saved/re-entered world using run 42058825739 artifact; WATER-001 remains open with 23,884 water pass and 3,850 FFT errors in session 220911-559, 39,132 / 6,026 in 230108-327. Packaging publication failed. No renewed claim of APK86 world failure.

Scope: synthetic CIL return-provenance parser only; no ShaderLab, original private code, Unity, device, .meta, audio, Settings, touch, or other agent files.

Baseline parser blob: 81253e15ba1e10b52cce47bcd521c48325228a5f. Work registered at fdac0942a3e9d02225d47208f9e2e0d5c1b1dfa9.

Changes: ff38ff92b48efd8776a16e298250dbabc4970819 fail closed for malformed instruction records / invalid numeric analysis bounds; 2d59a4ca3690f25e7ac089aa8e667b712fd789fc adds isolated pytest regressions. No test execution or original-DLL/Unity/device proof; GitHub host DNS unavailable in local container, and connector has no Actions execution API. No new Action launched. Do not count as water restoration.

Next step: run `python -m pytest -q tests/test_t2_cfg_malformed_records.py` in reachable checkout/CI; continue original Foam RenderTexture caller provenance and actual Spectrum/Foam/Blur ShaderLab resource bindings with T1/T3 coordination, not another synthetic-only hardening cycle. Inspect live HEAD and Actions first. Status WATER-001 OPEN.
