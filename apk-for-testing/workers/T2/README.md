# T2 — Android mini lab

**المسؤول: T2 | النطاق: Spectrum / Foam / Blur / CB0.**

- الحالة: NOT_PREPARED — لا APK حتى الآن.
- APK/versionCode/applicationId/SHA256: **لا ملف تنزيل موثق بعد**.
- المصدر SHA + CI: لا يوجد بناء مختبر Android فعلي مثبت حتى الآن.
- testpack: يحدد عند حاجة حقيقية؛ ليس إلزامياً الآن.
- مسار السجل: `/storage/emulated/0/Download/Games/cl/test/t2-<lab>-<session>/`.
- المطلوب قبل READY_TO_TEST: 2–10 حالات واضحة، baseline والمتوقع، وصف تجربة المالك، رابط APK/Artifact موجود وصالح، SHA256/size/package/version/source SHA، logs/screenshots المطلوبة.
- لا تمحُ نتائج أجهزة سابقة؛ أضف سجل الإصدار والنتيجة هنا. بعد التحقق حدّث [صفك وحده في مركز الاختبارات](../../TEST_CENTER.md) وفق [البروتوكول](../../LAB_PROTOCOL_AR.md).

## 2026-11-08 — bounded diagnostic protocol (not a GPU test)

- [Six-case T2 water testpack](../../examples/t2-water-render-testpack.json) defines baseline, positive/negative render-pass controls, original binding check, FFT controls with T1, and artifact provenance.
- All six cases are `note` because the generic host has **no Spectrum/Foam/Blur GPU renderer**. The pack is a non-executable test plan; importing it cannot test original shaders, GPU passes, CB0, FFT or Raft pixels. Do **not** mark READY_TO_TEST or ask the owner to run it as a graphics benchmark.
- Next: coordinate with T1/T3/T5 on a minimal compiled GLES/Vulkan renderer, prove a positive-control offscreen roundtrip and explicit invalid-pass failure, then integrate only authenticated original shader bindings. No proprietary shader bytes in public testpacks.
- Owner's 8 Nov CL session reports 74,359 invalid water passes and 11,165 invalid FFT kernels; counts are session-specific and not GPU output validation. Mouse button/scroll ownership remains T4; Resolution remains T5.
