# T2 scheduled — CL evidence parser strict schema and JSON constants

- session_id: `20261106T0226Z-T2-scheduled-schema-6f31`; origin: `scheduled`; issue: WATER-001.
- baseline SHA: `9fb807f6cf45743c1bffd9d61b7aa9a42e3f7d0e`; scope commit `c2c077a33ec54ee8c7c14972d15ebeb366d7723e`.
- resumed_from_sessions: `20261106T0120Z-T2-scheduled-json-evidence-7c91`, `20261106T021504Z-T2-chat-foam-descriptor-collision-c7e8`; kept active chat Foam descriptor scope untouched.
- phone source: docs/DEVICE_FEEDBACK_42058825739_AR.md, run 42058825739, pinned CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Owner entered, saved, exited and reentered world from Artifact. Package publication failed. WATER-001 still OPEN; no pixel/ShaderLab validation.
- hypothesis verified by Python semantics: `True == 1` would accept boolean schema in prior `classify`; Python JSON decoder permits nonstandard NaN/Infinity constants unless parse_constant is supplied, including irrelevant fields.
- changes: `scripts/t2_device_water_summary.py` commit `9508f0c573a4bfb4f4f8a074ecc1944a0c5fcacf`: require exact int schema and reject nonfinite JSON constants. `tests/test_t2_device_water_summary.py` commit `58e118f0fec0b3813924381f9328378c24faacdd`: add boolean/float/string/null schema and NaN/Infinity/-Infinity nested/extra regression cases.
- validation: isolated Python guard smoke **9/9 PASS** on Python runtime; repository unittest suite **NOT executed**, no authentic CL summary run, no Unity/GPU/device build. Source fetch reviewed; expected-sha file updates succeeded. Latest platform CI 42149963530 SUCCESS on older 9fb807f, unrelated to changes. No equivalent active build dispatched/cancelled.
- scope: only evidence parser/tests plus own work/session files; no ShaderLab/game/audio/Settings/input changes. No claim Foam rendering fixed.
- next: run `python -m unittest tests.test_t2_device_water_summary` on actual checkout and apply to pinned CL summaries, then continue original Foam two-pass descriptor experiment from chat after checking its latest evidence. Keep source private, coordinate with T3 fire/smoke and T1 FFT.
