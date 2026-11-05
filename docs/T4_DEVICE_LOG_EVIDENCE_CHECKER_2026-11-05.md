# T4 LOCAL-005: machine-checkable phone JSONL evidence contract

Source `android-port/Runtime/Platform/PersistentDiagnosticLog.cs` writes JSONL records with session, sequence, UTC, area, operation and detail. It copies early lines into both startup and rotating segment files, and a session sequence may be missing after retention/queue loss. Raw paths, world names and exception messages are sensitive and must not be echoed into public Actions.

`scripts/t4_verify_device_world_save_log.py --input <local path>` accepts one JSONL or local directory; it bounds input (80 MiB, 500k lines, 128 files) and rejects malformed records, file symlinks, conflicting duplicate sequences. Byte-identical startup/segment copies deduplicate. Reports **only** numeric session ordinals, marker counts, file existence size categories, completeness flags, and explicit unverified claims. It never publishes session IDs, private file names, or stack text.

Cross-session nonzero Save and nonzero Load events are hypotheses only: they do NOT establish an application process restart, same world, valid RGD, original de/serialization, a controllable player, or candidate source SHA. The owner must still verify offline new-world playability, true save after full process exit, and reopen of the exact same world on a signed candidate. Even a complete log is not an acceptance result.

Scope is complementary to active independent `T4-20261105T1405Z-chat-original-rgd-runtime-k6n8` (authentic seed CLR deserialization). No original binary/assets or .rgd are read by the CI tests. Last actual phone game APK86 predates new source event markers. LOCAL-005 OPEN and NOT_READY 0/3.

Test script `tests/test_t4_verify_device_world_save_log.py` uses eleven source-free negative controls and the bounded workflow `.github/workflows/raft-t4-world-save-log-evidence.yml`. No Unity/native run is requested.

## Verification

At initial publication, CI status pending; append immutable run ID and actual result when known.
