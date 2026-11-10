# T3 scope 20261110T2230Z-T3-scheduled-guid-hash-e7q3
origin=scheduled
issue=RENDER-002
branch=feature/android-native-port
source=docs/DEVICE_FEEDBACK_42058825739_AR.md

Hypothesis: GUID audit only reports unresolved counts by extension, so a repeated unresolved shader/texture GUID cannot be correlated across material and prefab records without leaking raw proprietary identities. Add short SHA256 identifiers for unresolved GUIDs, with per-source-extension counts; preserve raw GUID privacy and existing aggregate counts.

Files: scripts/t3_unity_guid_link_audit.py; tests/test_t3_guid_audit_hashed_unresolved.py; this work file; independent T3 session file. No game resources, .meta, save, settings, mouse, resolution or other workers' files.

Experiment key: T3-GUID-HASH-UNRESOLVED-20261110; CPU-only source fixtures; no shared Unity/GPU resource; no CI duplicate requested. Prior same-export 41 material/227 TexEnv internal parity is not re-run. Existing oversized scan coverage remains explicit.

Latest verified prior session: 20261110T2133Z-T3-scheduled-guid-coverage-h6p2; prior source commits e7f55228 and a34035df; tests reported unexecuted. Owner device world/save/re-entry confirmed only for artifact 42058825739. No claim of visual fix.
