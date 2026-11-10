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

## أحدث GFX-MULTI-009–013 — مراجعة المصدر والـCPU
- GFX-009 CI42728348900 SUCCESS: original Shader48 compressed source platform D3D11 and compiled table 1656 records; raw GPU program type labels alone not Android proof.
- GFX-010 CI42731206453 SUCCESS: 1435/1435 original pass VS/FS variant blob links valid, 0 type mismatches, all actual linked programs DX11 with embedded DXBC. General table GLES labels do not correspond to the seven referenced original passes.
- GFX-011 CI42731898965 SUCCESS: one exact keyword/tier VS/FS source pair translated privately to Vulkan1.1 SPIR-V and validated 2/2 stages; 7/7 source passes have at least one exact matching pair, 524 matched pairs total.
- GFX-012 CI42732370025 SUCCESS: one original pair transformed to GLSL ES310 and compiled offline, VS/FS IO location/type 7/7 matched; source-only.
- **GFX-013 CI42732808109 SUCCESS**: all seven original Shader48 passes (4+3) have one matched variant pair each converted to SPIR-V then GLSL ES310 and accepted by offline validators. 14 stage programs and per-pass VS/FS reflected location/type match. Not 524/524 variants, not ShaderLab running on Android, originalShaderRestored=false.
- **Current stage OPEN**: source→Unity→Adreno+PC pixel parity, constant buffers/samplers/texture mapping/normal DXT5nm, source render states/keywords, rig/animation, multi-part assembly remain unverified. See `gfxlab/REUSABLE_MODEL_RESTORATION_GATES_AR.md`. Never declare restored original Shader48 or completion of all item types from CPU proof alone.


## إلزام الاستعادة المتواصلة بناءً على طلب المالك (2026-11-10)
بنهاية **كل دورة** يجب حفظ: (1) `memory/sessions/<session_id>.md` مع `resumed_from/base_sha/origin=chat` وروابط CI وحالة النجاح/الفشل والحدود والخطوة التالية، (2) `prompt/graphics-lab/RESTORE_AR.md` مع آخر دليل مثبت ومسار الجلسة، (3) `gfxlab/OPEN_WORK_AND_IDEAS_AR.md` بجميع الخطط والأفكار المفتوحة وأولوياتها، (4) `memory/MEMORY.md` و`memory/STATE.json`. تحقق من commit SHA قبل الادعاء بالحفظ. إذا تعذر الرفع صرّح بذلك ولا تقل إن الحالة حفظت. عند الاستئناف اقرأ الخمسة وCI قبل الكتابة. لا تُنشئ العامل العام حتى يحدد المالك قواعده.

## فحص GFX-MULTI-014 الأخير
[CI42733664716](https://github.com/alwansan/raf/actions/runs/42733664716) SUCCESS: DXBC أصلي لممثّل Shader48 Pass0 VS/FS بلا RDEF؛ الأعداد الأصلية للـConstant Buffers/Bindings `unknown/null` وليست 0. عدد SPIR-V resource بعد التحويل VS5 UBO، FS7 UBO/7 image/6 sampler؛ لا يعني دلالة binding مكافئة. التصحيح وفتح خارطة الدوامة بجلسة `memory/sessions/20261110-GFX-chat-persistent-roadmap-15.md`. التجربة التالية GFX-MULTI-015، راجع القائمة الدائمة.


## جلسة حيّة جديدة — GFX-MULTI-015
- session_id: `20261110-GFX-chat-rdef-seven-pass-source-16`; origin=chat، resumed_from=`20261110-GFX-chat-persistent-roadmap-15`، base_sha=`7c0e37af4f83934264393626b77868fada53daa2`.
- تجربة أصلية مصدرية خاصة `GFX-MULTI-015`: فحص RDEF وجرد chunks في 14 Stage من 7 Passes حقيقية، وليس ShaderLab ولا APK.
- اقرأ نتيجة CI من `.github/workflows/gfxlab-multi-rdef-seven-pass.yml`، وسجّلها في `memory/sessions/20261110-GFX-chat-rdef-seven-pass-source-16.md` و`gfxlab/OPEN_WORK_AND_IDEAS_AR.md` وملف الاستعادة وSTATE/MEMORY قبل انتهاء الدورة.


## أحدث نتيجة مثبتة — GFX-MULTI-015
[CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) SUCCESS، 80 اختبار، 14/14 source Shader48 VS/FS DXBC Stage بلا RDEF، وجميعها تتضمن SHDR وInput/Output signature؛ مصدر CB/register binding UNKNOWN ولا يُعبّر عنه بـ0. هذا ممثل واحد من كل Pass من أصل 524 pair، لا استعادة Android أصلية. ملف الجلسة الحالي `memory/sessions/20261110-GFX-chat-rdef-seven-pass-source-16.md`. قائمة الأفكار `gfxlab/OPEN_WORK_AND_IDEAS_AR.md` محدثة. الخطوة الأولى GFX-MULTI-016 قراءة SHDR declaration tokens بحدود ومراجعة opcode رسمية؛ الفصل عن shader runtime وPC/device pixels واجب.


## العمل الجاري — GFX-MULTI-016
- `session_id=20261110-GFX-chat-shdr-declaration-census-17`، origin=chat، resumed_from=`20261110-GFX-chat-rdef-seven-pass-source-16`، base_sha=`af00b6e067b07347e7937c0b90a27f51d4ba019d`.
- `GFX-MULTI-016`: اقرأ تعليمات DXBC SHDR (وليس RDEF الغائب) في 14 stage، احصِ DCL_RESOURCE/CB/SAMPLER بمواصفة Microsoft وأبقي المصدر داخل runner. رابط CI بعد تشغيل workflow `gfxlab-multi-shdr-declaration-census.yml`.
- بعد نجاح/فشل الاختبار حدّث الجلسة وRESTORE وBACKLOG وMEMORY وSTATE، ثم تحقق من commit؛ originalShaderRestored=false، ولا APK أو تعديل T-TEAM.


## أحدث GFX-MULTI-016 — عدّ تعليمات موارد SHDR الأصلية
[CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984) SUCCESS، 85 اختبارًا، جرد source-only لبرامج Shader48 الأصلية الـ14 (ممثل VS+FS واحد لكل Pass): 66 `dcl_constant_buffer` و29 `dcl_resource` و27 `dcl_sampler` و0 Raw/Structured. كل البرامج اجتازت فحص طول token الأصلي. Pass0 VS5 CB وFS7 CB/7 Resource/6 Samplers؛ تتوافق مع أعداد SPIR-V، لكن **لا دليل على DX11 register index→SPIRV descriptor binding** بعد. آخر جلسة `memory/sessions/20261110-GFX-chat-shdr-declaration-census-17.md`، وخارطة المستقبل `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`، التالية GFX-MULTI-017.


## GFX-MULTI-017 — فحص فهارس سجلات DX11 الأصلية
جلسة `20261110-GFX-chat-original-register-operands-18`، origin=chat، resumed_from=`20261110-GFX-chat-shdr-declaration-census-17`، base SHA `eeda17d6570315b3362eb4d6685b2ce2342af509`. أداة Source-only جديدة لفحص `OperandToken0` في تعليمات SHDR الأصلية عبر 14 stage: نوع السجل، index dimension، immediate32 representation. قيم b#/t#/s# وحجم CB لا تُنشر؛ report counts only. اقرأ CI workflow `gfxlab-multi-source-register-shape.yml` ودوّن النجاح/الفشل. المصدر Shader48 ما زال غير مستعاد على Android؛ بعد التجربة حدّث كل ملفات الاستعادة والمهام الخمسة.


## أحدث نتيجة مثبتة — GFX-MULTI-017
[CI42737442510](https://github.com/alwansan/raf/actions/runs/42737442510) **SUCCESS** 89 اختبارًا. مصدر Shader48 الأصلي: 14 stage، أخرجنا داخليًا 66 CB register declarations ذات أحجام معلنة غير صفرية، و29 Resource و27 Sampler، بلا تكرار فهارس داخل المرحلة نفسها. فهارس b/t/s وأحجام CB لم تُنشر. لا توجد حتى الآن مطابقة source register→SPIR-V binding أو Material TexEnv/CB offsets. آخر جلسة `memory/sessions/20261110-GFX-chat-original-register-operands-18.md`، وآخر خارطة `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`. التالية GFX-MULTI-018 لمقارنة المجموعات الخاصة مع SPIRV-Cross مع منع افتراض التطابق.


## GFX-MULTI-018 جارٍ — source DX11 ↔ SPIR-V binding
جلسة `20261110-GFX-chat-source-vs-spirv-binding-19`، origin=chat، resumed_from=`20261110-GFX-chat-original-register-operands-18`، base_sha=`36fbf0fece5abb5f3e84792f09416cbb4e551e8f`. مقارنة سرية لسجلات b/t/s من SHDR الأصلي مع SPIRV-Cross `set/binding` لنفس البرامج الـ14، نشر أعداد توافق/اختلاف فقط. الفرق الرقمي قد يكون remap صادر عن المترجم، وحتى التطابق الرقمي لا يثبت Material/CB semantic mapping. اقرأ `gfxlab-multi-source-spv-bindings.yml` وحدث الجلسة وRESTORE/OPEN_WORK/MEMORY/STATE بعد CI. لا Android ShaderLab أو APK حاليا.


## GFX-MULTI-018 — أحدث نجاح مثبت وسبب نقص الربط
[CI42738042943](https://github.com/alwansan/raf/actions/runs/42738042943) SUCCESS 93 اختبارًا؛ 7 Passes /14 source Shader48 stages أصلية. المصدر وSPIRV يتساويان في **عدد** مجموعات الموارد 42/42 (122/122 عنصر)، بلا missing/duplicate descriptor. source CB register numbers تطابق SPIRV binding sets في 14/14، بينما **Texture وSampler في Fragment لا يتطابقان رقميًا في 0/7 لكل نوع**. لذا لا تستخدم source t#/s# مباشرة مع SPIR-V GLSL؛ يجب استعادة mapping. التطابق الرقمي لمجموعة CB لا يثبت CB byte offsets أو semantics. آخر جلسة `memory/sessions/20261110-GFX-chat-source-vs-spirv-binding-19.md`. الخطوة الموثقة `GFX-MULTI-019` في `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`: mapping مصدر→SPIRV→Material TexEnv قبل أي Android APK. originalShaderRestored=false.


## GFX-MULTI-019 — تجربة رموز vkd3d الجارية
- جلسة `20261110-GFX-chat-symbolic-binding-map-20` origin=chat، resumed_from=`20261110-GFX-chat-source-vs-spirv-binding-19`، base_sha=`3686ec91b4b940ba36393e15d54545ee7ec546b9`.
- فحص source-only حقيقي لـ 14 stage من Shader48، تستخرج سجلات b/t/s من SHDR وتفحص ما إذا كانت أسماء SPIRV-Cross المشتقة من vkd3d `tN/sN/cbN_size` تتطابق مع مصدر DX11 و`set/binding`. النشر أعداد أسماء صحيحة/مفقودة ومعدّلة فقط؛ قيم الأصل وأسماء shader تبقى سرية.
- أداة `gfxlab/tools/multi_shader_vkd3d_symbolic_register_map.py` وworkflow `gfxlab-multi-vkd3d-symbolic-binding.yml`. حل compiler binding لا يثبت ارتباط Material TexEnv أو Color/Normal/Metallic أو CB byte offsets. استعادة Shader48 على Android=false. بعد CI حدّث الجلسة وRESTORE/STATE/MEMORY/OPEN_WORK وتحقق من commit.


## أحدث نجاح GFX-MULTI-019 — source t/s → SPIRV OpName
[GFX-MULTI-019 CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) SUCCESS، 98 اختبارًا؛ شيدر Shader48 الأصلي، 7 Passes/14 Stage ممثلة: 29/29 Texture/Resource `t#` و27/27 Sampler `s#` تطابقت أسماء vkd3d المصدرية مع `set/binding` في SPIR-V، وجميعها أعاد المترجم ترقيمها. 66 Constant Buffer أسماء غير معروفة في grammar الحالية، رغم التطابق الرقمي السابق. عدد المجموعات المكتملة بالاسم 28/42 فقط (14 مجموعة Vertex فارغة +14 Fragment t/s حقيقية). لا Material TexEnv mapping، ولا original Android shader. آخر جلسة `memory/sessions/20261110-GFX-chat-symbolic-binding-map-20.md`؛ التالي GFX-MULTI-020 لاستكشاف `SerializedSubProgram.m_TextureParams / m_Samplers / m_ConstantBufferBindings` الأصلية وربطها بMaterial ومعاني الـRegisters.


## GFX-MULTI-020 جارٍ — source Shader texture property / Material TexEnv
- `session_id=20261110-GFX-chat-original-material-texenv-21` origin=chat، resumed_from=`20261110-GFX-chat-symbolic-binding-map-20`، base_sha=`3cdf399d4656dc05692fcc7f559069372e8f2977`.
- للمرة الأولى نجرب من المصدر `SerializedPass.m_NameIndices` و`SerializedSubProgram.m_Parameters.m_TextureParams` (NameIndex/Index/SamplerIndex) بمقارنة DX11 SHDR t#/s# وسبع مواد أصلية `Material.m_SavedProperties.m_TexEnvs`. فقط أعداد exact source metadata bridges تُنشر، بدون أسماء أو أرقام.
- workflow `gfxlab-multi-original-material-texenv.yml`. *حتى إن تطابقت الأسماء والإشارات* ما يزال originalShaderRestored=false وMaterial/CB/Adreno visual parity unproven. عند نهاية الدورة حدّث كل ملفات الاستعادة.


## أحدث نتيجة GFX-MULTI-020 — TexEnv المصدر موجود، ميتاداتا الـProgram مفقودة
[CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) **SUCCESS**، 103 tests، 6 Mesh و7 Materials أصلية: 63 m_TexEnvs (21 Texture2D مرتبطة، 42 null)، Shader48 يحتوي 27 Serialized shader properties. لكن 14/14 source Shader48 selected stage row بلا `m_Parameters`، لذلك `m_TextureParams/m_SamplerIndex` الخاص بربط shader property إلى DX11 t/s غير قابل للفحص من هذه الـRows، وverified material-property-to-register mappings=0. هذه **فجوة البيانات المصدرية**، لا فقدان الصور؛ 56/56 t/s register→SPIRV name association من GFX019 تبقى صحيحة لكن بدون اسم المادة. كانت GFX-MULTI-006 قد سجلت 0 parameter metadata variants سابقاً. آخر جلسة `memory/sessions/20261110-GFX-chat-original-material-texenv-21.md`؛ اقرأ `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`. التالي GFX-MULTI-021 فحص m_Script/مصدر Shader أصلي بديل مع fail-closed، ثم CB/Normal/PC pixel evidence.


## GFX-MULTI-021 — البحث عن مصدر Shader48 الأصلي المفقود
جلسة `20261110-GFX-chat-original-shader-text-source-22`، origin=chat، resumed_from=`20261110-GFX-chat-original-material-texenv-21`، baseline `090993480abe7b4fc3f541b03357f71fa3fc1a77`. نفحص هل Shader48 الأصلي يحتفظ بـ`m_Script` حقيقي يتضمن CG/HLSL وregister syntax، ونقيس مطابقة أسماء TexEnv المرتبطة (21) لقائمة خصائص Shader48 الأصلية (27)، من دون نشر أي اسم أو نص شيدر. حتى وجود HLSL النصي لا يكفي لتأكيد property→t# mapping إلا إذا ثبت رابط صريح. workflow `gfxlab-multi-shader-text-evidence.yml`، CI pending. بعد التشغيل حدّث كل ملفات الاستعادة/المهام.


## GFX-MULTI-021 آخر نتيجة مثبتة — أسماء الصور الأصلية صحيحة، النص الأصلي غائب
[CI42741817991](https://github.com/alwansan/raf/actions/runs/42741817991) SUCCESS 107 اختبارات: Shader48 الأصلي عنده 27 properties (9 Texture properties). سبع Materials أصلية: **63/63 m_TexEnvs property names** موجودة في قائمة Shader48، و**21/21 bound Texture2D names** مطابقة: 7 BaseColor +7 Normal +7 Metallic. Shader48 المصدر **بلا m_Script field، 0 bytes**، ولا HLSL/CGPROGRAM أو register syntax text. مع 0/14 `m_Parameters` من GFX020 وغياب RDEF في 14/14 source pairs من GFX015، لا يوجد حتى الآن رابط موثّق `Material property name → original DX11 t/s register` من هذه الحقول. لا تستنتج عدم توفر المصدر في **جميع الـ524 variants**؛ هذه عينة ممثلة فقط. Original Shader48 Android/restored false.
- آخر جلسة `memory/sessions/20261110-GFX-chat-original-shader-text-source-22.md`؛ دليل العائق `gfxlab/SHADER48_MATERIAL_REGISTER_BRIDGE_BLOCKER_AR.md`؛ خارطة المهام `gfxlab/OPEN_WORK_AND_IDEAS_AR.md`.
- التالي GFX-MULTI-022 عيّنات variants أخرى/مصادر same-export مستقلة للتحقق من RDEF/metadata بدل التخمين، وبعده PC pixel/CB/normal correctness بشكل منفصل. حدث ملفات الاستعادة بعد كل دورة.
