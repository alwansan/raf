# T5 ZIP method compatibility audit
session_id: 20261110T1250Z-T5-scheduled-j6q2
origin: scheduled
baseline_sha: 681581182b322497ac8fb7946d9735b0f76d1d09
issue_id: APK-OBB-DELIVERY
intended_files: scripts/t5_verify_apk_obb_pair.py; tests/test_t5_verify_apk_obb_pair.py; this work file; prompt/coordination/T_TEAM/clients/T5/sessions/20261110T1250Z-T5-scheduled-j6q2.md
experiment_key: T5-APK-OBB-UNSUPPORTED-ZIP-METHOD-68158118
resource_key: none (CPU-only synthetic fixtures)
hypothesis: currently a matching delivery SHA can mask unsupported BZIP2/LZMA members in an OBB; Android asset readers cannot be assumed to support these methods. Reject unsupported methods before claiming usable assets.
coordination: T4 owns physical mouse; this run changes only standalone T5 pairing checker/tests, not Unity or shared mini APK. No Unity CI or native build.
status: active
