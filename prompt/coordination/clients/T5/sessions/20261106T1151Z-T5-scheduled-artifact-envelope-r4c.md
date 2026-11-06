# T5 scheduled — signed artifact envelope metadata verified
session_id: 20261106T1151Z-T5-scheduled-artifact-envelope-r4c
origin: scheduled
status: completed_metadata_provenance_only
baseline_sha: c2863950848a470aae5d6795a13740c586f554ff
scope_commit: 502761864cb4108f016ba53cb446dc41bd6c7c7d
resumed_from_sessions: 20261106T1046Z-T5-scheduled-pair-success-q6f8.md; 20261106T1130Z-T5-chat-applycallers-c6e1.md

## New verified result (GitHub Actions artifact API, 2026-11-06 11:51 UTC)
- Original phone-tested source: e9c358eda01785b65e4eb14f18723da426635628; run https://github.com/alwansan/raf/actions/runs/42058825739 . Owner confirmed world/save/exit/re-entry only on this build.
- Delivery artifact ID **13441227298**, name **raft-android-test-delivery**, size **5,948,243,524 bytes**, `expired=false`, GitHub artifact archive digest **sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6**.
- Signed checkpoint artifact ID **13441766832**, name **raft-android-signed-output-checkpoint**, size **2,974,110,506 bytes**, `expired=false`, GitHub artifact archive digest **sha256:0e99e82c44af0fa21f613515ca0cb8eee2c04aa7911e9a001aabd1abdcde16bd**.
- **Crucial boundary:** these SHA256 values describe GitHub Actions artifact ZIP envelopes, NOT signed APK or main OBB inner-file SHA256. The two sizes likewise are compressed archive sizes, not OBB bytes. Cannot infer versionCode, APK signature, OBB basename, internal size, GUID, or actual phone installation provenance from them. No raw game assets downloaded or redistributed.
- Existing synthetic pairing validation: https://github.com/alwansan/raf/actions/runs/42197510807 succeeded; synthetic only. Current team CI T5 original Settings Apply caller audit https://github.com/alwansan/raf/actions/runs/42210936332 succeeded; chat owns follow-up, no overlap. Latest T1 Vulkan run https://github.com/alwansan/raf/actions/runs/42212055131 succeeded; source-only.

## Next step / acceptance
Download the two still-unexpired archives only to authorized isolated environment, validate artifact archive digests, locate `delivery.json` and signed APK/OBB, compute per-inner-file size/SHA256, inspect APK versionCode/signing cert, compare main OBB expected name/versionCode and inspect actual main-vs-optional-patch GUID warnings; avoid raw asset publication. Run existing `scripts/t5_verify_apk_obb_pair.py` and report redacted evidence. Then correlate LogRaft sessions with exact installed version and resolution before performance comparisons. No device test or new runtime repair in this session. WATER/FFT/RENDER and device acceptance unresolved; NOT_READY 0/3.
