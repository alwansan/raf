# T5 — Android-safe signed-pair extraction
session_id: 20261108T1350Z-T5-scheduled-android-link-fallback-r7m4
origin: scheduled
resumed_from_session: 20261108T1255Z-T5-scheduled-artifact-download-limit-q9r2
base_sha: 22961ed16cdc221c02866b55bde4463bb5c34b3f
scope_commit: 6e5727d32c4980177d2e886439703ecd7a9d6a1c
code_commit: 34435e51475c5e2843891424418b184673a94530
test_commit: 2f5a9cbba3e0e69322efa98ac38a96682b24ca86
issue: DELIVERY-013
origin_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md
## Result
Original phone success remains run42058825739 source e9c358eda01785b65e4eb14f18723da426635628; APK/OBB installed hashes unknown. The pinned rescue artifact 13454900880 is 5,948,243,834 bytes and the prior connector download failed at 512MiB cap. No binary was downloaded in this cycle.
Fixed scripts/t5_extract_actual_signed_pair.py so os.link unavailable (AttributeError/NotImplementedError) or unsupported (EXDEV, EPERM, EOPNOTSUPP, ENOSYS, EACCES) uses exclusive destination open('xb') + streamed copy + flush/fsync, preserving no-clobber behavior. Unexpected errors still fail closed and clean staging. Added three regression tests to tests/test_t5_extract_actual_signed_pair.py for missing os.link, EOPNOTSUPP, EIO cleanup. No game data or secrets published.
## Validation and limits
Static code and tests committed. Test execution not verified: this runner's container could not resolve raw.githubusercontent.com to fetch repo source; GitHub Actions result for these commits not yet established. Do not claim device, signature, OBB GUID, or Unity validation. No Unity build dispatched, no T4 files touched.
## Next
Run python -m unittest discover -s tests -p test_t5_extract_actual_signed_pair.py -v on a checkout or existing cheap CI. Rescue pinned artifact before 2026-11-08T21:12:40Z via authorized private runner/gh client with >6GB storage; verify outer SHA 41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef and extract exact signed pair with this tool. Then compare actual APK/OBB manifest, SHA and device install. Right-side buttons and Resolution still require real device validation and render-scale integration. NOT_READY.
