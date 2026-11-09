# T5 CL evidence integrity gate
session_id: 20261109T0052Z-T5-scheduled-cl-gate-a6d2
origin: scheduled
base_sha: 4ec7751e071ffc9564805c586612df581c55b470
status: in_progress
files: scripts/t5_verify_shared_device_summary.py; scripts/test_t5_verify_shared_device_summary.py; work/T5/20261109T0052Z-T5-scheduled-cl-gate-a6d2.md; clients/T5/sessions/20261109T0052Z-T5-scheduled-cl-gate-a6d2.md
experiment_key: t5-cl-summary-fail-closed-20261109
resource_key: none (CPU-only)
hypothesis: shared Mini summary may report EVIDENCE_READY without enough provenance or verified image evidence; strict read-only validator must reject stale/duplicate/cross-pack records and never label game graphics or mouse as passed.
source: https://github.com/alwansan/CL/blob/main/test/shared-20261108-232759-468049775/summary-20261108-232759-468049775.json
coordination: no game source, T4 pointer, Unity, shared Mini Java or shared build request touched. Separate validation from T4 smoke.
next: implement and test fail-closed evidence validator, then record actual output.
