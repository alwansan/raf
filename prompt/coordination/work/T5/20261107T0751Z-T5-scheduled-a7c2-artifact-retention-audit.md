# T5 artifact-retention and provenance audit — scope

- session_id: `20261107T0751Z-T5-scheduled-a7c2`
- origin: `scheduled`
- issue_id: `DELIVERY-APK-OBB` / owner feedback 42058825739
- status: `active`
- experiment_key: `artifact-retention-api-42058825739-42110297871-42296450023-20261107`
- resource_key: `none` (GitHub metadata read-only; no Unity or shared CI)
- intended_files: this work file and `prompt/coordination/clients/T5/sessions/20261107T0751Z-T5-scheduled-a7c2.md` only
- hypothesis: GitHub artifact ZIP SHA256/expiry is not an APK or OBB content match; expiring original checkpoint can be distinguished from retained delivery and newer build by immutable run/source/artifact IDs.
- baseline: original source `e9c358eda01785b65e4eb14f18723da426635628`; later rebuild source `a1737bd736e276d53df808442cfae3b1eea0d488`.
- safety: no asset downloads, no Unity, no release or build dispatch, no writes to CL or other worker files; no READY claim.
- next: verify retention and provenance from Actions API, record exact timestamps, distinguish archive digest from internal APK/OBB SHA; coordinate independent binary inspection if artifact is available.
