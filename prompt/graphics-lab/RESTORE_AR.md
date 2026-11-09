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
- M01 rig أصلي فيه 100 bone، لكن العرض الحالي OBJ bind/static pose فقط؛ `originalAnimationRestored=false`. **كان M05 في الاختيار التاريخي** مستخدمًا لاختبار مادتين مقابل submeshes، وأصبح **M03** في الاختيار الجديد، ويتوقف build عند mismatch بدلاً من تلويث الصورة.

## تحديث مثبت — اختيار هندسة جديدة بعد إخفاق Unity
- [GFX-MULTI-003 المحاولة الأولى 42712833407](https://github.com/alwansan/raf/actions/runs/42712833407) فشلت عند استيراد M02؛ [المحاولة الثانية 42714952065](https://github.com/alwansan/raf/actions/runs/42714952065) أعادت بناء OBJ الأصلي 1598 رأسًا/2095 مثلثًا ثم فشلت Bounds؛ [المحاولة الثالثة 42718266273](https://github.com/alwansan/raf/actions/runs/42718266273) حددت `GFX_MULTI_DEGENERATE_SOURCE_VERTEX_BOUNDS_M02`. **لا APK** لهذه المحاولات.
- [GFX-MULTI-001 المعدل 42719663373](https://github.com/alwansan/raf/actions/runs/42719663373) **SUCCESS**: فحص float32 الحقيقي لإحداثيات source OBJ استبعد 12 مرشحًا غير صالح للعرض، واختار خمسة موديلات موثقة جديدة. المصدر ZIP2 نفسه لا يتغير.
- **ترتيب الاختيار الجديد (يلغي وصف M02–M05 القديم عند اختبار APK جديد):** M01 person/skinned 5095v/100bones؛ M02 tool/skinned 1666v/8bones؛ M03 multi_material/static 2163v/**مادتان**؛ M04 complex_skinned_unidentified/skinned 2445v/100bones؛ M05 generic/skinned 4452v/2bones؛ M00 Shears 375v.
- **إعادة الاختبارات اكتملت الآن:** [GFX-MULTI-002 CI42720399689](https://github.com/alwansan/raf/actions/runs/42720399689) **SUCCESS**: six original Mesh/7 Materials/21 Texture PNG، و15 chunks/707788800 bytes داخل runner فقط. [GFX-MULTI-004 CI42720400057](https://github.com/alwansan/raf/actions/runs/42720400057) **SUCCESS**: هوية Shader48 واحد أصلي مشترك باثنين SubShader و7 Passes (4+3)، إثبات source-only لا Android ShaderLab.
- الحالة المرجعية: `ORIGINAL_SOURCE_SELECTION=PASS`؛ `SOURCE_PACK_NEW=PASS`؛ `UNITY_APK_NEW=SIGNED_SUCCESS_OWNER_TEST_PENDING`؛ `ANDROID_SIX_DEVICE=NOT_TESTED`. M01/M04 وغيرها Skinned OBJ ثابتة وليست أصل Animation/Rig؛ shad​​er الأصل غير مستعاد.

## أحدث نتيجة مثبتة — ستة موديلات APK Android فعلي
- **[GFX-MULTI-003 Actions 42720920391](https://github.com/alwansan/raf/actions/runs/42720920391) COMPLETED SUCCESS** على Commit `ee96e4d86dd6679be6814e4116368a664362b12a` بعد اختيار M02 بديل ذي هندسة صالحة. Unity 2021.3.45f2 Android IL2CPP ARM64 OpenGLES3 نجح بإدخال الستة، 7 Materials، 21 Textures، ومطابقة عدد المثلثات، وM03 بمادتين.
- **[تحميل GitHub Artifact 13721725242](https://github.com/alwansan/raf/actions/runs/42720920391/artifacts/13721725242)** (انتهاء 2026-11-16T23:39:48Z UTC). ملف APK نفسه 24098726 بايت، SHA256 `ef2b86b9384144fc3dd13c93d9b3a4e98cc07bfba3493b6a5c59b52d8db13f6c`، `com.alwansan.raft.graphicslab.multi`. التوقيع واسم الحزمة تم التحقق منهما في CI، والـSHA256/CRC/ARM64 IL2CPP فُحصت بشكل مستقل بعد تنزيل Artifact. لا OBB أو بناء لعبة كاملة.
- اختبار المالك **مطلوب ولم يحصل بعد** للستة: صورة واحدة + COPY LOG JSON من `SOURCE_PBR_STANDARD_APPROX` لكل M00–M05. عند ظهور خلل أضف صورة `SOURCE_ALBEDO_STANDARD`. راجع **M03 مادتين** و**M01/M04 Skinned static OBJ** خاصة.
- لا تغيّر الحقيقة السلبية: `originalShaderRestored=false` و`originalAnimationRestored=false` و`runtimeColoredPixelsVerified=false` على الستة حتى فحص الهاتف؛ نتائج Shears v0.2 السابقة باقية مستقلة. `RENDER-002/WATER-001 OPEN`.

## ما التالي عند الاستعادة؟
- إذا GFX-MULTI-003 نجح: تحقّق من SHA/APK والتوقيع والحزمة، سلّم المستخدم رابط التحميل، واطلب صورة وCOPY LOG لكل موديل وخصوصاً M01 وM03 وM04، مع مقارنة بصور Raft PC عند توفرها.
- إذا فشل: اقرأ خطوة الفشل وتفاصيل Unity Editor، أصلح المصدر **فقط في فرعنا**، وأعد تجربة واحدة محددة؛ لا تنسبه إلى Adreno قبل هاتف.
- بعد رؤية الستة على الهاتف: فصل مرحلة **Shader/Pass/Keywords/CB/sampler/Blend/Normal DXT5nm/rig** لكل موديل عن حالة Standard fallback، ثم مطابقة source→Unity→GPU→الهاتف قبل أي تسليم إصلاح إلى T3 أو المنتج.
- راجع `docs/ROOT_CAUSE_REVIEW_AR.md` لعيوب Dummy/Water/FFT القديمة، و`docs/TEAM_HANDOFF_AR.md` لتوزيع العمل دون تداخل.

**النص المختصر لإعادة التشغيل في أي محادثة جديدة:**
> اسمك GFX-LAB. ابقَ في Chat واستعد التعليمات الحية من https://github.com/alwansan/raf/blob/experiment/android-graphics-rootcause/prompt/graphics-lab/RESTORE_AR.md، واقرأ أحدث ملفات الذاكرة والجلسات ونتائج GitHub Actions، ثم أكمل GFX-MULTI في فرع experiment/android-graphics-rootcause فقط من آخر نتيجة مثبتة.
