# B48 synthetic test fixture failure — resolved
Author B48; session 20261104T2058Z-B48-f24a; WATER-001; UTC 2026-11-04T21:05:46Z; source 0035e6adcbafb38a3c62f596b08a46a5d8bcf609.
Impact: first [CI41912253262](https://github.com/alwansan/raf/actions/runs/41912253262) failed 3 of 5 new synthetic fixture tests BEFORE original asset/source test, no game code touched and no other workflows interrupted.
Cause: expected pair indices assumed bank0 rows were contiguous although report alternates bank0/bank1; one negative bank mutation equalled original bank1 pair; one negative workgroup mutation equalled original slot10 size.
Recovery: [7be4c336](https://github.com/alwansan/raf/commit/7be4c3365d4297a06abf502ceea504fee507f9c4) corrected only fixture expectations and real mutations. [CI41912422220](https://github.com/alwansan/raf/actions/runs/41912422220) passed 15/15 synthetic tests and SHA-pinned original sources + 20 compiled candidate slots.
Rejected hypothesis: the initial red result does not show runtime FFT incompatibility.
closed_reason: fixture corrected and full bounded source experiment green. WATER-001 stays OPEN.
