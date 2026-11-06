# T5 scheduled — original signed APK live attestation failure isolated

- session_id: `20261106T1346Z-T5-scheduled-apk-live-failure-m7q2`; origin: `scheduled`; issue: `INTEGRATION-001`; branch: `feature/android-native-port` only.
- Base HEAD at scope registration: `7e5d69ce00e5c22183915205f164b67101694d8c`; work scope: `prompt/coordination/work/INTEGRATION-001/20261106T1346Z-T5-scheduled-apk-live-failure-m7q2.json`. Independent evidence review; no source, Unity, original asset, or other client files edited.
- Resumed from latest T5 chat `20261106T1330Z-T5-chat-signed-apk-auth-f7b2.md`, earlier T5 chat nested ZIP `20261106T1316Z-T5-chat-nested-zip-c53a.md`, and scheduled envelope `20261106T1151Z-T5-scheduled-artifact-envelope-r4c.md`. Owner report `docs/DEVICE_FEEDBACK_42058825739_AR.md` read before prioritization.

## New observed evidence, 2026-11-06 13:46 UTC

- [Original full signed APK attestation CI42227170402](https://github.com/alwansan/raf/actions/runs/42227170402) on immutable source `c23b26efd1112cf1cd828e2190bd378f6f0b08d4` is **completed FAILURE**, not still running as the earlier chat checkpoint stated.
- Actual [job 127923480529](https://github.com/alwansan/raf/actions/runs/42227170402/job/127923480529) step conclusions: synthetic signed APK SHA/Android identity tests **success**; Android SDK signer tools and disk preflight **success**; **stream actual original signed 673MB APK only from ZIP_STORED remote member FAILED**; secret-safe cleanup **success**.
- This is a discriminating failure-stage localization. No verified complete signed APK SHA256, actual AndroidManifest versionCode, or cryptographic apksigner result exists from this run. Do not misclassify as bad signature, corrupted OBB or manifest mismatch. Script `scripts/t5_verify_real_signed_apk.py` fail-closed reasons include `remote_range_request_failed`, `remote_range_incomplete`, `downloaded_apk_digest_mismatch`, `artifact_metadata_changed` and others; the job-step summary alone cannot choose one.
- Prior [CI42224062207](https://github.com/alwansan/raf/actions/runs/42224062207) proved **70/70 nested local headers** by bounded range reads, not full payload SHA or phone mount. Owner world/save/reentry remains confirmed only for [artifact run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739).

## Next evidence-gated action

Retrieve **redacted** failed-step output (look for `T5_REAL_SIGNED_APK status=BLOCKED reason=...`) from existing CI job logs. Identify whether remote range, artifact expiry, disk, digest or other step failed; only then make a minimal tested fix. Avoid duplicate ~673MB download or heavy Unity CI until this cause is known. Continue separate Resolution and three-right-button scope without overwriting concurrent chat T5 work. No device/LogRaft measurement was made here; water/FFT/colors remain open; NOT_READY 0/3.
