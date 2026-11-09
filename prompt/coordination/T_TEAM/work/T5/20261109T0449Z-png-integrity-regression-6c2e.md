# T5 scheduled — PNG integrity regression
session_id: 20261109T0449Z-T5-scheduled-6c2e
origin: scheduled
baseline_sha: 166019dd17e7dde33c1942350c964fe3fddca3bb
scope: new isolated unittest file `scripts/tests/test_t5_verify_png_bytes.py`; no T4 mouse, Unity, shared manifest or game files.
hypothesis: the recently added PNG byte verifier lacks automated negative-case tests, so CRC, trailing bytes, duplicate IHDR and missing IDAT regressions could silently invalidate the T3 screenshot gate.
experiment_key: T5-PNG-BYTES-REGRESSION-20261109
shared_resource: none; no CI launch.
source: `scripts/t5_verify_png_bytes.py` at baseline; prior T5 session `clients/T5/sessions/T5-20261109T0353Z-scheduled-png-bytes-n7q4.md`.
next: add self-contained standard-library regression tests and run them; do not imply visual acceptance.
