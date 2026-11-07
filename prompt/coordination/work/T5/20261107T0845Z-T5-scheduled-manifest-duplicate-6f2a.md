# T5 isolated scope — 2026-11-07 08:45 UTC

- session_id: `20261107T0845Z-T5-scheduled-6f2a`; origin=scheduled; owner=T5.
- baseline HEAD `ef4af2916d42ff8608a0eae4a729e61cd619636d`; source owner report `docs/DEVICE_FEEDBACK_42058825739_AR.md`.
- independent hypothesis: retained-delivery archive verifier silently accepts duplicate JSON object keys in `delivery.json`, allowing conflicting identity/part metadata to be shadowed. Fail closed on duplicates without changing binary data or Unity.
- files: `scripts/t5_verify_retained_delivery_archive.py` and new isolated test `tests/test_t5_retained_delivery_duplicate_json.py`; session `prompt/coordination/clients/T5/sessions/20261107T0845Z-T5-scheduled-6f2a.md`.
- experiment key: `T5-20261107T0845Z-retained-json-duplicate`; shared resource: none; no Unity/Actions dispatch, no game binaries.
- prior: `prompt/coordination/clients/T5/sessions/20261107T0751Z-T5-scheduled-a7c2.md` and `prompt/coordination/work/T5/20261107T0751Z-T5-scheduled-a7c2-artifact-retention-audit.md`.
- scope does not touch T4 physical mouse, T1–T3 shaders, or shared workflow. Recheck branch HEAD and verifier blob SHA before patch.
