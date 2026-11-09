# T5 scope 20261109T0855Z-T5-scheduled-png-order-r6c2
origin: scheduled
base_head: d7e7e3b84dbdbe61f4575cf7abecbd638968b7c8
issue: PNG-CHUNK-ORDER
experiment_key: t5-png-noncontiguous-idat-20261109
files: scripts/t5_verify_png_bytes.py; scripts/tests/test_t5_png_chunk_order.py; clients/T5/sessions/20261109T0855Z-T5-scheduled-png-order-r6c2.md
hypothesis: PNG verifier accepts noncontiguous IDAT chunks, violating PNG ordering and producing false PASS.
shared_resources: none; T4 owns mouse; no Unity/CI.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md; prior session 20261109T0758Z-T5-scheduled-png-adam7-b4e1.md
expected_sha: d7e7e3b84dbdbe61f4575cf7abecbd638968b7c8
limits: structural PNG only.
