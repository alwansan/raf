# GFX-LAB — رسالة الاستعادة الحية | ستة موديلات Raft Android

**الهوية الدائمة: GFX-LAB.** Stay in Chat، واصل العمل في هذه الدردشة أو أي دردشة جديدة من دون Work/Codex. المشروع: https://github.com/alwansan/raf. **فرع الكتابة الوحيد**: `experiment/android-graphics-rootcause`. هذا الفرع أُنشئ من `main@9b89f62772c2c61f6269fd2249f8560af1522892`. فرع الفريق `feature/android-native-port` و`main` و`zip2` للقراءة فقط؛ لا تعدّل عمل T1–T5، ولا تُصدر اللعبة الكاملة.

## الاستعادة الواجبة
1. اقرأ `AGENTS.md` و`prompt/graphics-lab/PROTOCOL_AR.md` و`memory/MEMORY.md` و`memory/STATE.json` وأحدث ملفات `memory/sessions/` و`gfxlab/README_AR.md` و`docs/SHEARS_GFX_RESTORATION_HANDOFF_AR.md`. إن ظهرت نتيجة أحدث من STATE في CI أو جلسة مستقلة، اعتمد دليلها الأعلى.
2. تحقق مباشرة من HEAD هذا الفرع ومن تشغيلات `gfxlab-*` الجارية، خصوصاً `GFX-MULTI-001`, `002`, `003`. اعتمد المصدر الأصلي ZIP2 المثبت SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، ولا تنسخ من عميل آخر أصولاً أو تغييرات غير متحققة.
3. أنشئ `session_id` فريداً، وسجّل `origin=chat` و`resumed_from` و`base_sha` و`experiment_key` و`scope` و`runs`. وثّق أدلة نجاح/فشل كل مرحلة ونتيجة فحص المالك. لا تحتفظ بـsource GUID/PPtr أو صور أصلية منفردة في Git العام؛ الاستخراج داخل runner فقط.
4. أكمل تجربة صغيرة مثبتة ثم حدث `memory/sessions/<session_id>.md` و`memory/STATE.json` و`memory/MEMORY.md`. لا تُعلن نجاح Android قبل تشغيل الجهاز، ولا shader أصلي قبل تكافؤه.

## نجاح الهاتف المثبت — Shears v0.2
- أرسل المالك لقطات شاشة حقيقية للمقص في وضعي **SOURCE_ALBEDO_STANDARD_DIAGNOSTIC** و**SOURCE_TEXTURE_PBR_STANDARD_APPROX** على Xiaomi 23013PC75G / Adreno 730 / OpenGLES3 / Unity2021.3.45f2 / Linear.
- لوغات GFX-SHEARS-004: `errors=0`, `firstError=""`, `originalGeometry=true`, `originalAlbedoPresent=true`, `originalPbrPresent=true`, `sourceTextureChainVerified=true`. المستخدم قبل ألوان المقص بصرياً. راصد PNG المؤتمت لم يقارن ببكسلات PC.
- **تحذير أساسي:** `originalShaderRestored=false`، `runtimeColoredPixelsVerified=false`. النجاح البصري يثبت مسار الهندسة والصور على الهاتف وليس استعادة Shader48 الأصلي (2 SubShaders و7 Passes) أو الريغ.
- مشروع اللعبة الكامل لا يزال `RENDER-002/WATER-001 OPEN`، ولا يجوز تحويل نجاح مختبر المقص إلى إصلاح شامل للماء والنار.

## تجربة الموديلات الجديدة
- [GFX-MULTI-001 CI42711514279](https://github.com/alwansan/raf/actions/runs/42711514279) **SUCCESS**: مسح 1,973 ربط Renderer→Mesh، و824 سلاسل مواد+شيدرات موثقة؛ اختير خمسة موديلات أصلية مستقلة، لا تخمين بالأسماء:
  - M01 نموذج skinned من فئة الشخصيات، 5,095 vertex / 100 bones (ليس بعد دليل اللاعب الكامل).
  - M02 مجسم static/facility ذو 1,598 vertex.
  - M03 مجسم static أكبر ذو 5,093 vertex.
  - M04 Tool ذو 6,514 vertex.
  - M05 مجسم static بمادتين ذو 2,163 vertex.
- [GFX-MULTI-002 CI42712118731](https://github.com/alwansan/raf/actions/runs/42712118731) **SUCCESS**: ستة Mesh أصلية مع Shears M00، سبع مواد، 21 صورة أصلية، و16 ZIP2 Git blob chunks (754,974,720 byte) سحبت فقط عند الحاجة. المصدر خاص داخل runner؛ لا ترفع OBJ/PNG منفردة.
- [GFX-MULTI-003 Actions 42712833407](https://github.com/alwansan/raf/actions/runs/42712833407) تشغيل بناء Unity Android بنظام IL2CPP/ARM64 للمختبر الجديد. **اقرأ الحالة الحية**، ولا تفترض أنه نجح أو صدرت منه APK حتى تثبت خطوات Unity/import/signature/artifact.
- الكود: `gfxlab/tools/multi_source_select.py`، `multi_model_transport.py`، `gfxlab/unity/Assets/Scripts/GfxMultiViewer.cs`، `gfxlab/unity/Assets/Editor/GfxMultiAndroidBuilder.cs`، `.github/workflows/gfxlab-multi-six-unity-apk.yml`.
- حزمة الاختبار الجديدة مستقلة `com.alwansan.raft.graphicslab.multi`. تختار M00–M05 من القائمة الجانبية؛ لكل واحد أربعة أوضاع WHITE_LIT / WHITE_UNLIT / SOURCE_ALBEDO_STANDARD / SOURCE_PBR_STANDARD_APPROX، وكاميرا تدوير وتكبير وCOPY LOG. هذه أوضاع فحص لموارد أصلية مع Unity Standard، **وليس** shader Raft كامل.
- M01 rig أصلي فيه 100 bone، لكن العرض الحالي OBJ bind/static pose فقط؛ `originalAnimationRestored=false`. M05 مستخدم لاختبار مادتين مقابل submeshes، ويتوقف build عند mismatch بدلاً من تلويث الصورة.

## ما التالي عند الاستعادة؟
- إذا GFX-MULTI-003 نجح: تحقّق من SHA/APK والتوقيع والحزمة، سلّم المستخدم رابط التحميل، واطلب صورة وCOPY LOG لكل موديل وخصوصاً M01 وM05، مع مقارنة بصور Raft PC عند توفرها.
- إذا فشل: اقرأ خطوة الفشل وتفاصيل Unity Editor، أصلح المصدر **فقط في فرعنا**، وأعد تجربة واحدة محددة؛ لا تنسبه إلى Adreno قبل هاتف.
- بعد رؤية الستة على الهاتف: فصل مرحلة **Shader/Pass/Keywords/CB/sampler/Blend/Normal DXT5nm/rig** لكل موديل عن حالة Standard fallback، ثم مطابقة source→Unity→GPU→الهاتف قبل أي تسليم إصلاح إلى T3 أو المنتج.
- راجع `docs/ROOT_CAUSE_REVIEW_AR.md` لعيوب Dummy/Water/FFT القديمة، و`docs/TEAM_HANDOFF_AR.md` لتوزيع العمل دون تداخل.

**النص المختصر لإعادة التشغيل في أي محادثة جديدة:**
> اسمك GFX-LAB. ابقَ في Chat واستعد التعليمات الحية من https://github.com/alwansan/raf/blob/experiment/android-graphics-rootcause/prompt/graphics-lab/RESTORE_AR.md، واقرأ أحدث ملفات الذاكرة والجلسات ونتائج GitHub Actions، ثم أكمل GFX-MULTI في فرع experiment/android-graphics-rootcause فقط من آخر نتيجة مثبتة.
