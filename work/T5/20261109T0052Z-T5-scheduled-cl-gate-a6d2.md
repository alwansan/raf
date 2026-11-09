# T5 CL evidence integrity gate
session_id: 20261109T0052Z-T5-scheduled-cl-gate-a6d2
origin: scheduled
base_sha: 4ec7751e071ffc9564805c586612df581c55b470
status: source_implemented_validation_pending
files: scripts/t5_verify_shared_device_summary.py; scripts/test_t5_verify_shared_device_summary.py; work/T5/20261109T0052Z-T5-scheduled-cl-gate-a6d2.md; clients/T5/sessions/20261109T0052Z-T5-scheduled-cl-gate-a6d2.md
experiment_key: t5-cl-summary-fail-closed-20261109
resource_key: none (CPU-only)
hypothesis: shared Mini summary may report EVIDENCE_READY without enough provenance or verified image evidence; strict read-only validator must reject stale/duplicate/cross-pack records and never label game graphics or mouse as passed.
source: https://github.com/alwansan/CL/blob/main/test/shared-20261108-232759-468049775/summary-20261108-232759-468049775.json
coordination: no game source, T4 pointer, Unity, shared Mini Java or shared build request touched. Separate validation from T4 smoke.
result: added read-only validator and seven regression controls at commits d1ac0d7 and 069abc5. Independently parsed CL JSON via GitHub connector: 29 results, T3 six EVIDENCE_READY with nonzero PNG metadata and verified_surface_pixels=true, T4 nine NEEDS_INPUT. Python tests not executed: container network DNS unavailable and no checkout mounted; do not claim CI or device PASS.
next: execute python -m unittest scripts.test_t5_verify_shared_device_summary and run validator on CL JSON after obtaining it; inspect PNG visually, then prioritize game Resolution/right controls with nonoverlap. No Mini/Unity build requested.
