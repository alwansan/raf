# T2 — unmocked original Foam report schema integration regression

- session_id: 20261108T0120Z-T2-scheduled-original-unmocked-fixture-n7q3
- origin: scheduled
- issue: WATER-001 OPEN; status: source_test_added_unexecuted
- baseline HEAD: 65005a4ef1cd662759d7c16b0590c590cda8b50f
- work: prompt/coordination/work/WATER-001/20261108T0120Z-T2-scheduled-original-unmocked-fixture-n7q3.json
- owner phone baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; native run 42058825739; original source e9c358eda01785b65e4eb14f18723da426635628. World enter/save/re-enter succeeded; water/FFT errors persist; delivery publish failed.
- taken_over_from: T2 sessions 20261108T0016Z (positive full-schema coverage gap), 20261108T0019Z (pass0 direct RenderTexture->RenderTexture; pass1 unknown->unknown). Original source proof run 42308583977, no redundant dispatch.
- latest observed branch before scope: 65005a4ef1cd662759d7c16b0590c590cda8b50f; latest sampled CI 42431115115 T5 parity SUCCESS, 42431115086 T4 mouse bridge SUCCESS. No native test or pixel proof from these.
- isolated code: tests/test_t2_foam_pass_crosscheck_original_integration.py, commits 610e4517c1260aea1bc6abd2722118e9bcbd4779 and 5e8636a7ea935899524e93ef3ae23d90be8a40f3. The fixture constructs all schema keys using the production validator constants; the real validate_original is **not mocked**. It tests pass0/pass1 reconciliation and fail-closed original authentication, pass counts, mismatched independent roles and extra private fields. Synthetic constants only; no original IL/names/assets.
- execution boundary: container git clone failed DNS github.com; connector could read/write source. Tests were **not run**; no success claim. Test import was made self-contained because tests/ is not guaranteed to be a package.
- no ShaderLab, original asset, .meta/GUID, Unity, FMOD, Settings, input, T3 or T4 file changed. No Actions dispatched, no package or trial-build request.
- next step: run `python -m unittest discover -s tests -p 'test_t2_foam_pass_crosscheck_original_integration.py' -v` on original checkout or existing source-only CI; if fixture fails, inspect real validator invariant and correct the synthetic fixture (never weaken original validator). Then privately trace pass1 unknown producer and compare CB0/ShaderLab. Coordinate T3 fire/smoke independently.
