# T5 scoped work — 2026-11-06 09:46 UTC
origin: scheduled
base_sha: 8e67a3be6a49e0f28adc918210ffeec72cfa28aa
issue: INTEGRATION-001
experiment_key: T5-APK-ENCRYPTED-LOCAL-CENTRAL-SIGNATURE
status: active
files: tests/test_t5_verify_apk_obb_pair.py; own session file
hypothesis: APK encrypted-flag fixture uses literal backslash x sequences, not PK local/central ZIP signatures, causing CI42183679266 failure before verification. OBB equivalent uses correct bytes.
shared_resource: none; source-only unit tests, no Unity or Actions dispatch.
coordination: separate from T5 chat performance/native delivery and T4 mouse; preserve all source/game files. Check HEAD before modification, update existing test by blob SHA; no force.
resumed_from: 20261106T0751Z-T5-scheduled-apk-archive-coverage-c81.md; CI42183679266
