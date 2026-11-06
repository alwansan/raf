# T5 — Actual original signed APK/OBB Unity marker identity (HTTP Range)

**Issue:** INTEGRATION-001. **Worker:** T5. **Session:** `20261106T1520Z-T5-chat-real-unity-guid-2b61`; `origin=chat`; write branch `feature/android-native-port` only.

## Why this probe is new and warranted

The old owner-tested Raft Android build [run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), exact source SHA `e9c358eda01785b65e4eb14f18723da426635628`, was independently verified via full SHA-256 stream for the original **signed APK** ([CI42228262902](https://github.com/alwansan/raf/actions/runs/42228262902)) and **main OBB** ([CI42230326050](https://github.com/alwansan/raf/actions/runs/42230326050)); the latter's whole OBB CRC32 also matched its original signed ZIP central directory. However, integrity of delivered bytes does not prove Unity resource GUID mapping or a matching installed-device OBB mount.

An **already-completed earlier** T5 read-only study [CI42119428667](https://github.com/alwansan/raf/actions/runs/42119428667), six Git-hash-pinned original CL owner LogRaft segments, showed **3 warnings explicitly for optional `patch.89.com.alwansan.raft.androidtest.obb`**, **0 observed main OBB GUID warnings**; original delivery contains only `main.89`, no patch OBB. Do not reclassify warnings, invent a patch file, suppress Unity errors, or assume the main installed OBB was definitely mounted.

The production `scripts/audit_android_expansion.py` explicitly allows `assets/unity_obb_guid` identity comparison only if that marker is present on **both** sides; otherwise reports `expansionIdentityCheck=unavailable`. The exact real owner-signed APK/OBB marker presence had not been proven by an authenticated range read.

## New genuine original artifact measurement

[CI42243852483](https://github.com/alwansan/raf/actions/runs/42243852483), job `127980808269`, exact final code commit `f128787aa536cf6db076e13634aba1c49034925d`: **COMPLETED SUCCESS**, **13/13** synthetic positive/negative tests and read-only actual original signed checkpoint ZIP (artifact `13441766832`, full outer ZIP `2,974,110,506` bytes). The tool authenticated GitHub artifact source metadata, used strict HTTP 206 only, validated all inner ZIP local headers versus central entries and checked only the exact marker `assets/unity_obb_guid`.

| Actual original signed member | `assets/unity_obb_guid` present |
|---|---|
| Signed APK, `672,853,870` bytes, 31 inner ZIP members | **YES** |
| Main OBB, `2,301,256,312` bytes, 39 inner ZIP members | **NO** |

- **Result category:** `apk_only_identity_unavailable`.
- **Byte-for-byte APK↔OBB marker equality:** **NOT AVAILABLE**. The OBB has no matching exact marker entry to compare, so the tool reports **zero marker bytes compared**, not a positive match.
- **Security:** no original marker/engine GUID value, auth token, Azure download URL or private game resources printed or uploaded. Total original archive bytes fetched: **11,447** via **156** strict HTTP 206 range requests, below the **16 MiB** cap.
- **No false runtime claim:** `unity_internal_engine_guid_verified=false`, `actual_installed_phone_obb_mount_verified=false`, and `game_ready_or_GPU_pixels_verified=false`. All **70** original nested APK+OBB local headers were checked. Signed APK and OBB whole SHA were proved separately in prior source CIs; this experiment was metadata only.

### Fail-closed history and exact test controls

- [CI42242913633](https://github.com/alwansan/raf/actions/runs/42242913633) **FAILED after 13/13 tests** because the *real* signed package had an unexpected one-sided marker; the first reporter rejected it with `unity_guid_marker_one_sided`. This demonstrates the finding was real, not merely guessed from packaging conventions.
- The follow-up reporter was revised to explicitly distinguish `apk_only_identity_unavailable`, `obb_only_identity_unavailable`, `both_absent_identity_unavailable`, and `both_present_byte_identical`; mismatch when both contain values still raises an error, and the source never invents a GUID. [CI42243221625](https://github.com/alwansan/raf/actions/runs/42243221625) failed old synthetic one-sided expectations while the tests were being updated; not an OBB data failure.
- Initial full pass [CI42243273146](https://github.com/alwansan/raf/actions/runs/42243273146) **SUCCESS**; final semantically precise proof [CI42243852483](https://github.com/alwansan/raf/actions/runs/42243852483) **SUCCESS** with 13 synthetic controls covering actual marker parity, one-sided asymmetry, both missing, equal-size mismatch, zero/overbound marker, path aliases, duplicates, ZIP local name/CRC corruption, signed checkpoint strict STORED fixture, wrong sizes, compressed outer members and range budget.

Files: `scripts/t5_probe_real_unity_obb_guid.py`, `tests/test_t5_probe_real_unity_obb_guid.py`, `.github/workflows/raft-t5-real-unity-obb-guid.yml`. They reuse the prior T5 original signed ZIP range/authenticity source modules, do not change real Unity runtime or the game's original assets.

## Interpretation and next action

An APK-only marker is an **observed archive layout**, **not by itself evidence of a wrong GUID or failing Unity OBB mount**. It is not safe to copy the APK marker into the OBB or create fake `patch.89` bytes without a verified Unity runtime contract. The prior three original phone warnings still refer specifically to the **optional unshipped patch**, not to a main expansion GUID check.

The next useful differential test is the original owner device's **installed** `/Android/obb/com.alwansan.raft.androidtest/main.89...obb` **file path and full SHA**, together with an actual Unity file-read success/error path and whether Unity reports `assets/bin/Data/*` from main OBB or APK. Only with that correlation can the on-device missing graphics/texture issue be attributed to packaging versus water/FFT shader binding. Do not guess from a harmless marker mismatch or hide warnings. If device evidence unavailable, focus on T1/T2 WATER-001 and T3 RENDER-002 source integration rather than repeating package census.

**Readiness:** WATER-001, RENDER-002 and full device acceptance still **OPEN**, game **NOT_READY 0/3**. Owner world/save/reentry applied only to older run42058825739, not a new current-branch build.

## خلاصة بالعربية

العلامة `assets/unity_obb_guid` موجودة فعلياً داخل APK القديم ولا تظهر كمدخل مماثل داخل OBB الرئيسي؛ لذلك لا توجد مقارنة GUID ثنائية يمكن اعتمادها. هذه الحقيقة لا تثبت فساد OBB ولا تفسر وحدها مشكلة الشيدرات والماء، والتحذيرات الثلاثة القديمة تشير إلى `patch.89` الاختياري. لا تعدل ملفات Unity الأصلية بناء على وجود العلامة في جهة واحدة.
