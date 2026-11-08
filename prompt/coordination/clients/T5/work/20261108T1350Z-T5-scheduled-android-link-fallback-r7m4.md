# T5 work — Android-safe signed-pair extraction
session_id: 20261108T1350Z-T5-scheduled-android-link-fallback-r7m4
origin: scheduled
status: active
base_sha: 22961ed16cdc221c02866b55bde4463bb5c34b3f
issue_id: DELIVERY-013
intended_files: scripts/t5_extract_actual_signed_pair.py; tests/test_t5_extract_actual_signed_pair.py; this work file; independent session file
experiment_key: signed-pair-extract-os-link-unavailable-android-fallback-v1
resource_key: none (source-only, no Unity)
hypothesis: os.link is absent or unsupported on Android shared storage; a verified no-clobber exclusive copy fallback can publish prevalidated signed pair without weakening digest checks.
taken_over_from: prompt/coordination/clients/T5/sessions/20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2.md
constraints: no raw game assets; no CI duplicate; preserve T4 files; no claim of device verification. Original archive rescue remains blocked by 512MiB connector limit.
