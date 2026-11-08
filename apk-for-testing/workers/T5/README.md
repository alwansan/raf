# T5 — Android mini lab

**المسؤول: T5 | النطاق: Mini host / package / telemetry / distribution.**

- الحالة: SOURCE_READY — host مصدر فقط ولم يُبنَ APK.
- APK/versionCode/applicationId/SHA256: **لا ملف تنزيل موثق بعد**.
- المصدر SHA + CI: لا يوجد بناء مختبر Android فعلي مثبت حتى الآن.
- testpack: يحدد عند حاجة حقيقية؛ ليس إلزامياً الآن.
- مسار السجل: `/storage/emulated/0/Download/Games/cl/test/t5-<lab>-<session>/`.
- المطلوب قبل READY_TO_TEST: 2–10 حالات واضحة، baseline والمتوقع، وصف تجربة المالك، رابط APK/Artifact موجود وصالح، SHA256/size/package/version/source SHA، logs/screenshots المطلوبة.
- لا تمحُ نتائج أجهزة سابقة؛ أضف سجل الإصدار والنتيجة هنا. بعد التحقق حدّث [صفك وحده في مركز الاختبارات](../../TEST_CENTER.md) وفق [البروتوكول](../../LAB_PROTOCOL_AR.md).

## T5 SAF APK/OBB + telemetry pack — 8 November 2026

- [6 data-only cases](../../examples/t5-package-telemetry-testpack.json): T5-01 selected signed APK SHA, T5-02 selected original main OBB SHA, T5-03 main/patch warning classification, T5-04 frame time and resolution, T5-05 GPU/error interval, T5-06 landscape controls.
- Fixed host source: [StreamSha256.java](../../host/app/src/main/java/com/alwansan/raftlab/StreamSha256.java) + [MainActivity.java](../../host/app/src/main/java/com/alwansan/raftlab/MainActivity.java), with off-UI-thread streaming SHA-256 and 16 GiB file safety cap. Image preview remains <=64 MiB. Hashing selected file does **not** prove APK installation or the OBB mounted by Raft.
- Verified source regression [CI42496378895](https://github.com/alwansan/raf/actions/runs/42496378895) PASS: 14 JDK assertions, including streamed synthetic 2,301,256,312-byte input, + schema validator (6 cases). Source test is not Android APK compile/SAF/device proof.
- Device acceptance when a **T5** APK exists: select a known APK and a known main OBB through Android SAF, wait for final digest, record **file name + size + SHA-256** and any explicit file access failure. Compare with the immutable artifact and actual installed package evidence separately. For telemetry, note scene, timestamp, resolution, FPS source and GPU-counter source; SurfaceFlinger FPS/GPU busy are not Unity frame/GPU times.
- Logs: Export via MediaStore to `Download/Games/cl/test/t5-<lab>-<session>/`; provide exported JSONL and any permission/provider errors. Do not upload original APK/OBB or private game data for a digest check.
- **Delivery status at this checkpoint: SOURCE_READY only.** No T5 APK download link or signing digest has been established yet. Do not ask the owner to install or test a non-existent T5 artifact.
