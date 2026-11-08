<!-- OWNER_SHARED_MINI_LAB_20261108 -->
> **المختبر الموحد هو المرجع الحالي:** لا تطلب من المالك تثبيت APK هذا العامل بشكل منفصل. التجربة الجديدة داخل [تطبيق T1–T5 الواحد](../../TEST_CENTER.md)، [الحزمة الواحدة](../../unified/pack/team-testpack.json)، [سياسة التعاون](../../UNIFIED_LAB_POLICY_AR.md)، [صف جاهزية بناء Mini المشترك](../../SHARED_BUILD_READINESS.md). احتفظ بروابط APK القديمة وأدلّتها أدناه للأرشفة فقط. يمكن أن يحتاج العامل تغيير Java/renderer تحت unified، ولا يبدأ بناء مستقل؛ T5 ينسّق واحداً عند حاجة عامل واحد مثبتة.

# T2 — Android mini lab

**المسؤول: T2 | النطاق: Spectrum / Foam / Blur / CB0.**

- الحالة الحالية: **READY_TO_TEST** (real debug APK verified, device test pending).
- APK bytes **38,113**; package `com.alwansan.raft.lab.t2`; versionCode **1** / versionName `0.1.0-source-prototype`; SHA256 `8254743c8514d4a808135f931d1fc560af54c40a7dd03bac3670c81ce4f5b4c1`.
- source SHA `1eb3e880e65a6f239be9b3cfbe1ff761851091eb`, [CI 42496746941 SUCCESS](https://github.com/alwansan/raf/actions/runs/42496746941), [Artifact 13624290449](https://github.com/alwansan/raf/actions/runs/42496746941/artifacts/13624290449) expires 2026-11-15T15:50:42Z.
- testpack: يحدد عند حاجة حقيقية؛ ليس إلزامياً الآن.
- مسار السجل: `/storage/emulated/0/Download/Games/cl/test/t2-<lab>-<session>/`.
- المطلوب قبل READY_TO_TEST: 2–10 حالات واضحة، baseline والمتوقع، وصف تجربة المالك، رابط APK/Artifact موجود وصالح، SHA256/size/package/version/source SHA، logs/screenshots المطلوبة.
- لا تمحُ نتائج أجهزة سابقة؛ أضف سجل الإصدار والنتيجة هنا. بعد التحقق حدّث [صفك وحده في مركز الاختبارات](../../TEST_CENTER.md) وفق [البروتوكول](../../LAB_PROTOCOL_AR.md).

## 2026-11-08 — bounded diagnostic protocol (not a GPU test)

- [Six-case T2 water testpack](../../examples/t2-water-render-testpack.json) defines baseline, positive/negative render-pass controls, original binding check, FFT controls with T1, and artifact provenance.
- All six cases are `note` because the generic host has **no Spectrum/Foam/Blur GPU renderer**. The pack is a non-executable test plan; importing it cannot test original shaders, GPU passes, CB0, FFT or Raft pixels. Do **not** mark READY_TO_TEST or ask the owner to run it as a graphics benchmark.
- Next: coordinate with T1/T3/T5 on a minimal compiled GLES/Vulkan renderer, prove a positive-control offscreen roundtrip and explicit invalid-pass failure, then integrate only authenticated original shader bindings. No proprietary shader bytes in public testpacks.
- Owner's 8 Nov CL session reports 74,359 invalid water passes and 11,165 invalid FFT kernels; counts are session-specific and not GPU output validation. Mouse button/scroll ownership remains T4; Resolution remains T5.

## 2026-11-08 — real GLES3 T2 mini-lab source (build/device pending)

- Real GLES3 driver experiments in `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T2GpuActivity.java`; T2-only button in host, package `com.alwansan.raft.lab.t2`.
- CASE01: device GPU name, GLES version and MAX_TEXTURE_SIZE.
- CASE02: two-pass RGBA8 FBO draw/sample/readback of [32,96,159,255] +/-2 on real GPU.
- CASE03: incomplete no-attachment FBO fails with GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT.
- CASE04: intentionally invalid fragment GLSL is rejected by driver.
- Four numbered cases with observed and expected, manual PASS/FAIL/UNEXPECTED notes, timestamped append-only private JSONL and MediaStore export under `Download/Games/cl/test/t2-gles-pass-<session>/`.
- No original game shader or proprietary assets. Positive result proves only a generic GLES3 two-pass diagnostic, **not** original Foam/Spectrum/Blur ABI, ShaderLab, FFT or final Raft rendering.
- At initial source checkpoint: SOURCE_READY. Superseded by verified build below.

## Actual verified T2 GLES3 lab APK — CI42496746941

- **Authentic build:** [GitHub Actions 42496746941](https://github.com/alwansan/raf/actions/runs/42496746941) SUCCESS, pinned source `1eb3e880e65a6f239be9b3cfbe1ff761851091eb`, debug package `com.alwansan.raft.lab.t2` vCode=1, vName=`0.1.0-source-prototype`. Actual 38,113-byte APK SHA256 `8254743c8514d4a808135f931d1fc560af54c40a7dd03bac3670c81ce4f5b4c1`, independently extracted/checked vs CI. [Artifact 13624290449](https://github.com/alwansan/raf/actions/runs/42496746941/artifacts/13624290449) (35,402-byte ZIP), expires **2026-11-15 15:50:42 UTC**.
- **Install:** install only T2 lab, leave full Raft APK and original worlds untouched. Tap **OPEN T2 REAL GLES3 WATER PASS LAB**; select each numbered CASE, read Expected/Observed, mark PASS/FAIL/UNEXPECTED and add observed notes.
- **CASE01** real GPU renderer/GLES version/MAX_TEXTURE_SIZE. **CASE02** genuine two-pass RGBA8 offscreen framebuffer/sample/readback checks pixel **[32,96,159,255] ±2**. **CASE03** empty FBO must report missing attachment incomplete status. **CASE04** invalid GLSL must fail compilation. Failures are useful diagnostics; do not mark PASS without observation.
- **Return**: screenshots of all four Expected/Observed case displays, especially failures; tap **EXPORT LOGS** and share `/storage/emulated/0/Download/Games/cl/test/t2-gles-pass-<session>/t2-gles-<session>.jsonl`. App-private JSONL preserves logs. New debug signature could require uninstalling **only an older T2 lab**, not Raft.
- **Evidence boundary:** compiled CI APK does **not** establish phone GPU PASS; built-in shaders are test patterns, **not original Foam, Spectrum, Blur, ShaderLab/CB0, FFT**, or Raft pixels. WATER-001 OPEN; Raft NOT_READY 0/3, full XAPK vote unchanged.
