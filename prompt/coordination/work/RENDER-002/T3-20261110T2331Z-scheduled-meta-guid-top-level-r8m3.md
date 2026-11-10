# T3 scope — 20261110T2331Z-scheduled-meta-guid-top-level-r8m3

origin=scheduled; owner=T3; track=RENDER-002; experiment=T3-META-GUID-TOPLEVEL-001.

Baseline observed `scripts/t3_unity_guid_link_audit.py` blob `e67c83e451c0aeac8c192f65670a456e40284b0f`.

Hypothesis: `.meta` GUID indexing uses an unanchored `GUID.findall` and takes the first occurrence, potentially indexing an incidental nested/comment GUID rather than the top-level Unity asset identity. This can falsely classify a material/shader/texture reference as resolved. A narrow top-level-only parser with synthetic negative controls prevents false resolution without touching original game data.

Files reserved: `scripts/t3_unity_guid_link_audit.py`; new `tests/test_t3_meta_guid_top_level.py`; this work record and own session file. No shared resources, no Unity build, no ZIP2 acquisition, no raw proprietary assets. No overlap with T1/T2 water, T4 input, T5 resolution/build.

Acceptance: only top-level `guid:` from `.meta` establishes an indexed identity; nested/comment GUIDs cannot establish identity; mixed case canonicalized; duplicate identity count unaffected. Run isolated Python unit test locally if executable; otherwise record unverified and rely on CI. Re-read blob before update and fail closed on changed SHA. Preserve previous export parity evidence and phone limitations.
