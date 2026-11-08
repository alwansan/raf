# T2 isolated scope — 2026-11-08T05:25Z
origin=scheduled; session=20261108T0525Z-T2-scheduled-underflow-4f8c

Base HEAD: 1292c024c71f3bec83c68ee950b675da3480a11f.
Issue: WATER-001 evidence-ingress integrity only; not water rendering.
Files: scripts/t2_foam_pass_crosscheck.py, tests/test_t2_foam_pass_crosscheck_finite_json.py, this work file, new T2 session file.
Hypothesis: JSON parse_float currently converts nonzero subnormal exponent e.g. 1e-9999 to zero silently, losing numerical evidence; reject nonzero underflow while preserving zero and finite representable values. Experiment key: T2-foam-json-underflow-4f8c. Shared resource: none; no CI/Unity/build.
Ownership: independent T2 evidence parser; T3 shaders/FX, T1 FFT, T4 mouse, T5 resolution/delivery untouched. Source is original safe report only; no proprietary payload.
Preconditions: owner device feedback 42058825739 read; trial vote T2 remains no-build; recent finite overflow test exists and should not be duplicated.
