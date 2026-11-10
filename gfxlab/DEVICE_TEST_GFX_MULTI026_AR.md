# GFX-MULTI-026 — دليل اختبار الموديلات الستة وقنوات GPU على الهاتف

**GFX-LAB | المصدر ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 | هذا APK مختبر مستقل، وليس Raft الكاملة**

## شرط التسليم

لا يعتبر رابط APK مقبولاً حتى يثبت GitHub Actions: `BuildPipeline.BuildPlayer = Succeeded`، وجود APK واحد حقيقي، `arm64-v8a/libunity.so` و`AndroidManifest.xml` و`classes.dex`، `apksigner verify`، و`aapt badging` للحزمة `com.alwansan.raft.graphicslab.channels`، ثم SHA256 وحفظ Artifact. بعد ذلك يُحدَّث هذا الدليل برابط التشغيل والتحقق.

## تجربة الهاتف

- نزّل ملف الـArtifact من Actions وافتح ZIP واستخرج `GfxLab-Multi-Six-Channel-Probe.apk` وثبّته. هذا اسم حزمة **جديد** يمكن وضعه إلى جانب اختبار الستة السابق `com.alwansan.raft.graphicslab.multi`، وليس إلى جانب ملفات اللعبة الكاملة بالضرورة. لا تحتاج OBB.
- افتح التطبيق أفقياً، وجرّب القائمة الجانبية M00–M05. M03 مهم لأنه يحتوي على مادتين، وM01/M04 نموذجان `skinned` لكن وضعية العرض الحالية OBJ ثابتة وليست Animation أو Rig أصلياً.
- لكل موديل التقط صورة في وضع `SOURCE_PBR_STANDARD_APPROX` ثم اضغط `COPY LOG`. أرسل JSON مع الصورة واذكر إذا حصل تكسّر، ألوان مفقودة، Alpha غريب، أو مادة اختفت. هذا الوضع يستخدم Unity Standard تقريبي.
- اختبر أزرار لوحة الصور على اليمين: `BASECOLOR` ثم `NORMAL` ثم `METALLIC`. داخل كل دور بدّل `RGB/R/G/B/A`؛ الصورة الناتجة هي **ناتج أخذ عينة GPU من شيدر فحص مستقل**، وليست Renderer Shader48 الأصلي.
- بدّل `SOURCE COLORSPACE` و`FORCE LINEAR` لقياس الاختلاف في أخذ عينات sRGB/Linear. لا تستنتج تلقائياً أن النسخة الأفتح/الأغمق أكثر أصالة. أصلاً BaseColor وMetallic مخزنتان sRGB في المصدر وNormal Linear، وقد تختلف معاني القنوات الدقيقة بحسب Shader48.
- في M03 جرب `SURFACE 1/2` و`SURFACE 2/2` مع BaseColor/Normal/Metallic، وصورة/LOG لكل مادة. إن ظهرت `NO SOURCE TEXTURE / PROBE UNSUPPORTED` فدوّن الدور والموديل والقناة.
- قيّم شيدر التشخيص، الرسوم، الموديلات، الاختيار، الكاميرا، حالات Copy Log، FPS إن توفر خارجياً، والانهيارات. لا تدّعِ أن Original Shader48 شُغّل بسبب ظهور ألوان أو قنوات صحيحة.

## القيم التي سنراجعها في COPY LOG

`experiment=GFX-MULTI-026`، `modelId`، `materialMode`، `diagnosticProbeStatus=DIAGNOSTIC_SHADER_NOT_SOURCE_SHADER48`، `diagnosticRole`، `diagnosticChannel`، `diagnosticSampling`، `diagnosticTextureAssigned`، `diagnosticShaderSupported`، `diagnosticMaterialSurface`، `deviceModel`، `gfxDevice`، `gfxApi`، `colorSpace`، `errors`، `firstError`. القيم `originalShaderRestored=false` و`originalAnimationRestored=false` و`coloredPixelsAutomaticallyVerified=false` يجب ألا تُرفع إلى true بغير دليل.

## حدود قبول الأدلة

- source links/PNG in runner + signed Unity APK = مرحلة `UNITY_IMPORT_COMPILE` فقط.
- ظهور قنوات GPU على الجهاز مع لقطات أصلية وJSON = `GPU_EXPERIMENT` للمختبر وحده، وليس `ANDROID_GAME_PIXELS`.
- تكافؤ شيدر اللعبة الأصلي `Shader48` (2 SubShaders/7 Passes، keywords/CB/sampler bindings/render state) وRig/Animation وPC↔Android pixel parity لم يثبت.
- `RENDER-002/WATER-001` لا يغلقان بهذه التجربة.


## GFX-MULTI-026 signed APK released — verified CI 42748792585
[Download six-model GPU channel APK Artifact 13733300521](https://github.com/alwansan/raf/actions/runs/42748792585/artifacts/13733300521) — in ZIP: `GfxLab-Multi-Six-Channel-Probe.apk`. APK exactly **65,963,109 bytes**, SHA256 `8fef68d82748cd214b1f5f5f9c0b3903a80f343513ccb15fc35e12649c02ad52`, package `com.alwansan.raft.graphicslab.channels`, expiry **2026-11-17T03:32:17Z UTC**. Real Unity2021.3.45f2 IL2CPP ARM64 GLES3 pipeline + signature + Android package checks successful and private ZIP2 source purge confirmed. Device owner has not yet tested. Diagnostic shader is NOT original Shader48; visual parity and game readiness remain OPEN.


## 2026-11-10 — GFX-OWNER-001 actual owner phone review and Shader48 recovery gates
The owner **has now tested GFX-MULTI-026 on Xiaomi 23013PC75G Adreno730**. 16 screenshots/13 COPY LOG JSON, six models with two Standard fallback modes, zero reported errors across available snapshots, Normal/Metallic GPU preview images visible. However all copied probe states were BASECOLOR/RGB/SOURCE/surface0; no matching per-toggle log or real Shader48 rendering. Source remains SHA-pinned ZIP2 and user screenshots/ShaderCache binaries remain off public Git.

- [GFX-OWNER-001 CI42752583864](https://github.com/alwansan/raf/actions/runs/42752583864): SUCCESS **171 tests**, safe ZIP auditor.
- [GFX-MULTI-030S CI42753634633](https://github.com/alwansan/raf/actions/runs/42753634633): SUCCESS **176 tests**, all 7 Shader48 Passes have m_NameIndices source strings, but **0/7 exact same-pass dynamic state name matches for Cull/ZWrite/ZTest/AlphaToMask**, only ZWrite 2/7 declared source Shader property with 14 Material-slot float matches. GPU states still unresolved.
- [GFX-OWNER-002 CI42754132240](https://github.com/alwansan/raf/actions/runs/42754132240): SUCCESS **179 tests**, all 7 original source Glossiness values **differ** from Standard lab hardcoded 0.45; source Metallic sRGB 7/7 differs Unity Standard renderer's Metallic Linear importer 7/7. Model PBR remains approximation, not source identity.
- **Closure matrix (currently NOT CLOSED):** `gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md`. Main source blockers: Shader48 property→DX11 t/s/CB (RDEF absent 1,275/1,275) and incomplete dynamic Pass state 7/7; Unity actual Shader48 GLSL/ShaderLab and PC↔Adreno parity still absent. Original rig/skinning for skinned M01/M04 absent from static OBJ viewer. Do not create a worker/agent now; keep owner-defined future agent protocol pending; water/FFT, fire/smoke, lighting/PostFX separately scoped.
