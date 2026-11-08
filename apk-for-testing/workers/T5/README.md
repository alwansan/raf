<!-- OWNER_SHARED_MINI_LAB_20261108 -->
> **المختبر الموحد هو المرجع الحالي:** لا تطلب من المالك تثبيت APK هذا العامل بشكل منفصل. التجربة الجديدة داخل [تطبيق T1–T5 الواحد](../../TEST_CENTER.md)، [الحزمة الواحدة](../../unified/pack/team-testpack.json)، [سياسة التعاون](../../UNIFIED_LAB_POLICY_AR.md)، [صف جاهزية بناء Mini المشترك](../../SHARED_BUILD_READINESS.md). احتفظ بروابط APK القديمة وأدلّتها أدناه للأرشفة فقط. يمكن أن يحتاج العامل تغيير Java/renderer تحت unified، ولا يبدأ بناء مستقل؛ T5 ينسّق واحداً عند حاجة عامل واحد مثبتة.

# T5 — Android mini lab

**المسؤول: T5 | النطاق: Mini host / package / telemetry / distribution.**

## READY_TO_TEST — T5 SAF APK/OBB / Telemetry v0.1.0 (8 November 2026)

- **Android APK:** [download real artifact ZIP (GitHub Actions 42496945089, artifact 13624380481)](https://github.com/alwansan/raf/actions/runs/42496945089/artifacts/13624380481). Open the Actions artifact, extract `app-debug.apk` and install that APK only, NOT the ZIP. Requires GitHub sign-in/appropriate repository access. File actually passed Android Gradle `:app:assembleDebug`.
- **Immutable build source SHA:** `7800e28583679d5e23825818b0ea5120b9d8b33f`; **package/applicationId:** `com.alwansan.raft.lab.t5`; **versionCode:** `1`; **versionName:** `0.1.0-source-prototype`; debug-signed, independent from installed Raft.
- **APK SHA-256 from actual build log:** `494f52199d215fd25c6b29283bc3b1733746a1180bb409c83491c055a5fe112d`. **Artifact ZIP**: id `13624380481`, size `35,397 bytes`, SHA-256 `b61e55b129321d2614781b196d97546c9f035886c18a941b960022b37254684f` (**ZIP digest is not APK digest**); expires `2026-11-15T15:53:09Z` (7-day retention). Actual `app-debug.apk` extracted and verified byte-for-byte against CI: **38,113 bytes**, SHA-256 `494f52199d215fd25c6b29283bc3b1733746a1180bb409c83491c055a5fe112d`, APK ZIP internal CRC checks passed; do not confuse this size with the 35,397-byte Actions artifact ZIP.
- **Result:** CI [42496945089](https://github.com/alwansan/raf/actions/runs/42496945089) **SUCCESS**, real Android Gradle compile and upload; prior T5 JDK streamed-digest [42496378895](https://github.com/alwansan/raf/actions/runs/42496378895) **SUCCESS 14 checks**, including synthetic >2 GiB stream. **Android device SAF and real OBB readback remain UNTESTED**; current lab status is READY_TO_TEST, not DEVICE_PASS.
- **Testpack to obtain separately:** [T5 six-case testpack JSON](../../examples/t5-package-telemetry-testpack.json), pack_id `t5-signed-package-telemetry-v1`, 6 data-only tests. Save JSON to user-visible Downloads; in the T5 APK tap **Pick testpack**, select that JSON and verify **T5-01** through **T5-06** appear. Android SAF import cannot execute code from JSON.

### Owner test: sequence and expected evidence

1. **CASE T5-01 — APK:** select an authorized downloaded *actual* signed APK via **Pick image or file / SHA256**, ideally the T5 APK itself for the baseline (expected digest is the APK SHA above). Wait for completion, record elapsed time, actual size/hash, PASS only if this file matches expected bytes. A user-selected file does not prove it is the separately installed Raft binary.
2. **CASE T5-02 — main OBB:** if an authorized copy of `main.<versionCode>.<package>.obb` is available in a folder allowed by the Android picker, select it, including an OBB larger than 64 MiB (ideally original >2 GiB). Expected: progress continues, UI remains usable, final full SHA-256 and byte count are logged, no false 64 MiB rejection; **FAIL** for crash/frozen UI/wrong hash, **UNEXPECTED** or explicit access denial if Android 15 SAF does not grant it. **Do not move, overwrite, or delete Raft's installed OBB or saves.** A selected copy is not proof that Unity mounted that OBB.
3. **CASE T5-03 — OBB warning:** write exact `obb_guid_load_failed` log path/time and whether it refers to optional patch or main; expected UNKNOWN when path is absent, not a guessed failure.
4. **CASE T5-04 — FPS/resolution:** note scene, landscape dimensions, selected resolution/render scale, refresh Hz, per-source FPS/p50/p95 times, timestamps. Expected device display estimates remain separate from Unity HUD FPS.
5. **CASE T5-05 — GPU/errors:** write session ID, GPU counter source/time interval, PSS/RSS if available, and WATER/FFT error deltas over same interval. Expected no fabricated per-game GPU utilization.
6. **CASE T5-06 — side controls & Settings:** check safe-area positioning of Show Xbox/Xbox layout/Test report and whether Resolution changes actual render scale while preserving landscape/aspect; note exact mismatch or PASS based on observation.

For each case, select it, reproduce the steps, enter your observation, then tap **PASS**, **FAIL**, or **UNEXPECTED**. Tap **Export logs**, which writes JSONL via MediaStore to `/storage/emulated/0/Download/Games/cl/test/t5-t5-signed-package-telemetry-v1-<session>/` when this pack is loaded. Please return the exported JSONL plus screenshots of SHA completion/errors, SAF access permission failures, and display/resolution before and after. Avoid sending raw proprietary APK/OBB data; hashes, size, paths with privacy redaction, and logs suffice.

**Acceptance criteria:** APK launches Android 15; 6 testpack cases load; large-file SHA completes accurately with progress and no UI freeze; MediaStore export succeeds; no claim of game-fixed or installed APK/OBB mount until verified by independent evidence. If only small-file testing is possible, report partial results rather than DEVICE_PASS.

### Version history

| Version | Source / CI | Result | Remaining proof |
|---|---|---|---|
| 0.1.0-source-prototype (T5) | `7800e28583679d5e23825818b0ea5120b9d8b33f`, [CI 42496945089](https://github.com/alwansan/raf/actions/runs/42496945089) | Android build success, artifact 13624380481 | Real Android 15 SAF >2 GiB read/digest, MediaStore logs, owner acceptance |
| Earlier shared host source | [CI 42496378895](https://github.com/alwansan/raf/actions/runs/42496378895) | Source/JDK regression 14 checks | No APK or Android result from this source-only CI |


[Historical note] Earlier source-only status was superseded by successful Android CI 42496945089. Do not conflate source-only and device evidence.

## T5 SAF APK/OBB + telemetry pack — 8 November 2026

- [6 data-only cases](../../examples/t5-package-telemetry-testpack.json): T5-01 selected signed APK SHA, T5-02 selected original main OBB SHA, T5-03 main/patch warning classification, T5-04 frame time and resolution, T5-05 GPU/error interval, T5-06 landscape controls.
- Fixed host source: [StreamSha256.java](../../host/app/src/main/java/com/alwansan/raftlab/StreamSha256.java) + [MainActivity.java](../../host/app/src/main/java/com/alwansan/raftlab/MainActivity.java), with off-UI-thread streaming SHA-256 and 16 GiB file safety cap. Image preview remains <=64 MiB. Hashing selected file does **not** prove APK installation or the OBB mounted by Raft.
- Verified source regression [CI42496378895](https://github.com/alwansan/raf/actions/runs/42496378895) PASS: 14 JDK assertions, including streamed synthetic 2,301,256,312-byte input, + schema validator (6 cases). Source test is not Android APK compile/SAF/device proof.
- Device acceptance with the verified **T5** APK: select a known APK and a known main OBB through Android SAF, wait for final digest, record **file name + size + SHA-256** and any explicit file access failure. Compare with the immutable artifact and actual installed package evidence separately. For telemetry, note scene, timestamp, resolution, FPS source and GPU-counter source; SurfaceFlinger FPS/GPU busy are not Unity frame/GPU times.
- Logs: Export via MediaStore to `Download/Games/cl/test/t5-<lab>-<session>/`; provide exported JSONL and any permission/provider errors. Do not upload original APK/OBB or private game data for a digest check.
- **Updated delivery status:** READY_TO_TEST from CI 42496945089 artifact 13624380481; previous source-only note above is historical, no Android 15 owner test yet.
