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


## GFX-MULTI-022 — exhaustive linked-variant reflection sweep (2026-11-10)
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) **SUCCESS**, 119 tests; source ZIP2 SHA locked. All **1,435/1,435** original Shader48 stage-variant link rows validated, including legacy and Unity 2021 player records; **524** exact keyword/hardware-tier VS/FS pairs; **1,275** unique referenced stage programs decoded as bounded authentic DXBC. RDEF present **0/1,275**; RDEF absent **1,275/1,275**. Across all 1,435 linked rows: `m_Parameters` blocks 0, texture parameter arrays/entries 0, constant-buffer binding arrays/entries 0, top-level sampler metadata rows 0, top-level constant-buffer metadata rows 0. The first attempt [CI42742873015](https://github.com/alwansan/raf/actions/runs/42742873015) completed the source scan but failed its summary assertion because zero-valued Counter keys were omitted; explicit zero counters fixed it. Private source purge succeeded in both attempts.

**Decision:** `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS`. This is stronger than the 14 representative-stage census, but does not include unreferenced entries in the 1,656-entry compiled table. The 56/56 DX11 t/s→SPIR-V symbolic mapping from GFX019 remains valid; the Material-property→source-register edge remains unknown. No original Shader48 Android runtime, GPU pixels, PC parity, APK, or owner acceptance. Original Shader48 restored=false.

**Next GFX-MULTI-023:** source-only Material/Texture2D semantic census across seven materials and 21 bound textures: role/format/color-space/mip/stream metadata, UV scale/offset, tint/color/float metadata, and role-specific decoded-channel statistics. Use authenticated sparse ZIP2 streams and publish safe aggregates only.


## الاستعادة الحية بعد GFX-MULTI-022
- أحدث جلسة: `20261110-GFX-chat-variant-reflection-sweep-23`; اقرأ `memory/sessions/20261110-GFX-chat-variant-reflection-sweep-23.md`.
- آخر commit موثق للتجربة: `32f60ca8cd39f5fd4615bbe4c364ac303a65620b`؛ تحقق من HEAD الأحدث قبل أي كتابة.
- [CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) SUCCESS؛ artifact `13730635053`، وملفات المصدر الخاصة حُذفت من runner.
- الحالة: property→DX11 t/s bridge blocked عبر جميع variant links المرجعية؛ لا Android Shader48 ولا GPU pixel parity.
- التالية GFX-MULTI-023: Material/Texture2D metadata + UV/tint + role-specific channel audit باستخدام sparse authenticated stream، source-only، no APK.


## GFX-MULTI-023 — original Material/Texture2D semantics and channel census (2026-11-10)
[CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) **SUCCESS**, 128 tests. Pinned ZIP2 source; six models, seven original Materials, 63 TexEnv slots (21 bound / 42 null), seven BaseColor + seven Normal + seven Metallic textures. All **21/21** original Texture2D images decoded with exact dimensions; 53,477,376 pixels examined privately. Only 15 authenticated stream chunks / 707,788,800 selected bytes were hydrated; safe aggregate artifact uploaded and all private source/texture/stream data purged.

Material facts: 14 color slots, 112 float slots, 0 int slots; all seven authored tint slots are identity white; all 21 role-specific UV scale/offset transforms are identity. Thus non-white tint and UV transforms do not explain the current material appearance differences.

Texture code distributions (raw serialized codes; do not infer color-space or format semantics from these counts alone): format code BaseColor 10×5 + 12×2, Normal 12×7, Metallic 12×7; color-space code BaseColor 1×7, Normal 0×7, Metallic 1×7; mip-count code BaseColor 11×3/12×4, Normal 11×3/12×4, Metallic 11×5/12×2; filter-mode code 1×21. Texture settings, anisotropy and mip-bias fields were present on all 21. Generic `m_WrapMode` code was unavailable in this type tree; axis-specific wrap fields still need inspection.

Channel census: BaseColor R/G/B variable 7/7; Alpha variable 2/7 and fully opaque 5/7. Normal R constant 7/7 while G/B/A variable 7/7; tested A+G with constant R+B signature candidate 0/7, so the conventional DXT5nm hypothesis is not supported by this simple channel signature. Metallic Alpha variable 7/7; this is only a candidate channel for additional data such as smoothness, not proof of shader semantics.

The first attempt [CI42743969290](https://github.com/alwansan/raf/actions/runs/42743969290) successfully planned the exact 15 chunks but failed when the audit re-read the manifest after sparse checkout intentionally excluded it. The correction reuses previously SHA-verified staged owner assets; [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) then completed all steps and private purge successfully. Artifact [13730562085](https://github.com/alwansan/raf/actions/runs/42744204412/artifacts/13730562085), expires 2026-11-17T02:40:48Z UTC.

**Limits:** raw numeric texture format/color-space codes are not yet semantically mapped; axis-specific wrap fields and float-property meanings remain open. No shader bytes, source names, pointers, raw pixels or image files were exported. No Shader48 execution, PC/GPU pixel parity, Adreno proof, APK or owner acceptance. `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`.


## الاستعادة الحية بعد GFX-MULTI-023
- أحدث جلسة: `20261110-GFX-chat-material-texture-semantics-24`; اقرأ `memory/sessions/20261110-GFX-chat-material-texture-semantics-24.md`.
- [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) SUCCESS، 128 tests، 21/21 texture decoded، 15 sparse chunks / 707,788,800 bytes؛ artifact `13730562085`؛ purge ناجح.
- النتيجة: tint أبيض 7/7 وUV identity 21/21؛ Normal R ثابت وG/B/A متغيرة، Metallic A متغيرة 7/7؛ لا تفسير نهائي لقنوات الشيدر.
- التالية GFX-MULTI-024: Material float/color semantics + TextureSettings WrapU/V/W + authoritative Unity 2021.3 enum mapping. No APK yet.

## GFX-MULTI-024 — verified result (2026-11-10)

- [CI42745345599](https://github.com/alwansan/raf/actions/runs/42745345599) FAILED after 139 unit tests: an incorrect uniqueness guard assumed seven material slots meant seven distinct Material21 assets. Source purge succeeded.
- Fixed to distinguish slot references from unique identities. [CI42745536309](https://github.com/alwansan/raf/actions/runs/42745536309) COMPLETED SUCCESS: 139 unit tests; original SHA-pinned ZIP2 source; six models, **7 renderer material slots / 6 distinct Materials**, **21 Texture2D links / 18 distinct images**. Runner private source purge succeeded.
- Original saved properties: **112/112 Float labels and 14/14 Color labels match Shader48's 27-property declaration**; this does NOT establish any property-to-register binding/CB byte offset. Seven slots have white RGBA tint; seven other saved color slots are nonidentity (unknown semantics).
- Float buckets: zero 33, one 58, strictly between 0 and 1: 21. Safe name categories: alpha-cutout 7, blend 14, depth 7, gloss 21, height 7, metallic 7, normal-strength 14, occlusion 7, render-mode 7, UV channel 7, unclassified 14. No raw names/values exported.
- Original TextureFormat: BaseColor DXT1×5 + DXT5×2; Normal DXT5×7; Metallic DXT5×7. Original internal TextureColorSpace: BaseColor sRGB×7, Normal Linear×7, Metallic sRGB×7. WrapU/V/W Repeat each 21/21, FilterMode Bilinear 21/21, Aniso=1 and MipBias=0 on all 21 original image links.
- Official Unity 2021.3 enum grounding: [UnityCsReference GraphicsEnums.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs) @ branch HEAD b052b1fe38b45d5aefa609a115c626ed2e74f3a6. Internal TextureColorSpace != PlayerSettings.ColorSpace.
- [Safe aggregate artifact 13730024662](https://github.com/alwansan/raf/actions/runs/42745536309/artifacts/13730024662), expires 2026-11-17T02:51:51Z UTC. No raw source Shader/ID/name/value, image, GPU pixel, APK, OBB, or third-party branch changes.
- Evidence level ORIGINAL_SOURCE. OriginalShaderRestored=false; original property→DX11 register mapping=false; Android GPU/PC pixel parity=false; rig/animation, water/FFT, smoke/fire still OPEN.

## Next: GFX-MULTI-025
Identify seven nonidentity second Color slots by exact shader property-name semantics without publishing original names/values; separately census shared Material21 / Texture2D identities across M00–M05. Do not infer emissive GPU behavior or convert Metallic sRGB to Linear without a controlled device/PC reference. Do not create an agent or game APK.

**Latest authoritative GFX session:** `memory/sessions/20261110-GFX-chat-float-wrap-color-25.md`; GFX-MULTI-024 CI42745536309 SUCCESS; next GFX-MULTI-025. Always verify HEAD and CI before edits.

## GFX-MULTI-025 — exact source secondary color and shared identity proof (2026-11-10)

[CI42746455458](https://github.com/alwansan/raf/actions/runs/42746455458) **COMPLETED SUCCESS**, **146 unit tests**, source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Source-private six selected models, seven Material21 Renderer slots and 21 original Texture2D links:
- Material alias groups: 5 single-reference groups and 1 double-reference group, **6 distinct original Material21 objects**; one material shared across models.
- Texture alias groups: 15 single-reference groups + 3 double-reference groups, **18 distinct original Texture2D objects**; three shared across models, **zero cross-role alias groups** (no reuse between BaseColor/Normal/Metallic roles).
- Source 14 saved Color slots match 14/14 Shader48 property names: seven known Base Tint white RGBA (RGB nonzero) and seven **`_EmissionColor` named property candidates with RGB exactly black and alpha exactly one**. Thus the seven nonidentity Color entries from GFX024 are *black emissive colors*, not failed diffuse tint. No GPU emissive-rendering equivalence has been proven.
- Only anonymous count histograms and safe allowlisted property categories published; no source name beyond public allowlist, private PPtrs, original vectors, IDs, shaders or textures exposed.
- Safe artifact [13730829715](https://github.com/alwansan/raf/actions/runs/42746455458/artifacts/13730829715), expires 2026-11-17T03:00:31Z UTC. All private source files purged (`GFX_MULTI025_ALL_PRIVATE_SOURCE_PURGED=true`).
- `originalShaderRestored=false`; source Material→DX11 t/s/CB offsets unknown; `android_gpu_pixels_verified=false`, `phase_closed=false`. No APK, no game assets in public Git, no changes to T1–T5 branches or main/zip2.

### GFX-MULTI-026 next
Audit seven original Shader48 Pass render-state declarations and original Materials' render queue/keywords/instancing; map what is explicitly present in original source vs missing or undecodable, using source-only bounded coverage. Do not invent Cull/Blend/ZTest/ZWrite/ColorMask states or declare original shader parity before Android GPU/PC reference.

Latest durable session: `memory/sessions/20261110-GFX-chat-secondary-color-alias-26.md`, CI42746455458 SUCCESS (146 tests); check latest branch HEAD before edits. Next GFX-MULTI-026 source Pass render-state audit; no Shader48 Android parity.

## GFX-MULTI-026S original seven-pass state census — CI42749148702 SUCCESS (2026-11-10)
Source-only, pinned ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, **154 unit tests** passed after an initial CI42749035585 sparse-checkout test setup failure (4 Unity contract tests looked for omitted Unity assets; source-free-only tests now skip Unity-only contracts when files are intentionally absent). Verified all **7/7** Shader48 source Pass rows have an `m_State` dictionary and tags, with metadata for Cull, ZWrite, ZTest, zClip, Blend separate, alphaToMask, stencil and fog; direct `rtBlend` and generic `colorMask` keys absent. Presence does NOT prove a correct runtime render state or effective Blend/ColorMask behavior. Seven original Material slot rows: instancing enabled 7, shader-default queue -1 in 5, explicit nonnegative queue in 2; `m_ShaderKeywords` direct field absent in 7/7 (not proof there are no keywords in alternate metadata). All source values and IDs private; runner purge successful. Safe artifact [13732363372](https://github.com/alwansan/raf/actions/runs/42749148702/artifacts/13732363372) expires 2026-11-17T03:24:33Z.
- **GFX-MULTI-026 APK build currently NOT completed:** [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) started at commit 818298ce8fcb71d7906f977c5d03cc8d619db57e, Unity 2021.3.45f2 real import/build IL2CPP ARM64 GLES3 is in progress. Six original SHA-authenticated models, 21 texture role links, original color-space vs forced linear diagnostic channel probe added. Package `com.alwansan.raft.graphicslab.channels`, Android minimal standalone APK only. Verify BuildPipeline, signature, package name, SHA256/CRC, artifact, purge before declaring APK issued.
- **Negative evidence:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `devicePixelsVerified=false`, `PCPixelParityVerified=false`. The new channel probe shader `Hidden/GfxLab/ChannelProbe` is independent diagnostic-only GLES3, **not Shader48**. WATER-001, RENDER-002 remain OPEN.

GFX live session now `memory/sessions/20261110-GFX-chat-sevenpass-channel-apk-27.md`; owner APK test has NOT happened; next check run CI42748792585 and update all five persistent files after its terminal status.


## GFX-MULTI-028S — تجربة قيم حالات الرسم الأصلية (2026-11-10)
- `session_id=20261110-GFX-chat-renderstate-enum-28`, origin=chat، resumed_from=`20261110-GFX-chat-sevenpass-channel-apk-27`، baseline `dfe32cd9ce38e7dad44560065aab67c8b771d8bc`.
- بعد نجاح GFX-MULTI-026S CI42749148702 (154 tests، 7 Passes م_State، 7 material instancing، 5 default queue/2 explicit)، نقرأ القيم المعلّمة `val/name` لـCull/ZWrite/ZTest/AlphaToMask مقابل Unity2021.3 enum ونفصل named_dynamic عن fixed enums ونفحص keywords البديلة. لا نخرج قيم shader الأصلية أو shader source؛ لا نعتبر نتائج CPU حالة GPU. Workflow `gfxlab-multi-safe-state-enums.yml`، CI pending.
- تجربة Android GFX-MULTI-026 CI42748792585 مستقلة وفي مسار BuildPipeline، لا تعديل على ملفاتها أو T-team. حدّث سجل هذه الجلسة وSTATE/MEMORY/OPEN_WORK بعد نتيجة CI.


## GFX-MULTI-026 APK — SUCCESS (2026-11-10)
[CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) verified real Unity 2021.3.45f2 IL2CPP ARM64 OpenGLES3 build, single signed APK, valid AndroidManifest/classes.dex/arm64 libunity.so/ZIP CRC, apksigner/aapt verified `com.alwansan.raft.graphicslab.channels`, and private asset purge. APK: `GfxLab-Multi-Six-Channel-Probe.apk`, 65,963,109 bytes, SHA256 `8fef68d82748cd214b1f5f5f9c0b3903a80f343513ccb15fc35e12649c02ad52`. [Artifact 13733300521](https://github.com/alwansan/raf/actions/runs/42748792585/artifacts/13733300521), expiry 2026-11-17T03:32:17Z. 6 original meshes, 21 original Texture links; diagnostic `Hidden/GfxLab/ChannelProbe` displays SOURCE/LINEAR imported sampled RGB/R/G/B/A per BaseColor/Normal/Metallic. **Never call diagnostic shader restored Shader48.** Phone test/PC pixel parity/rig/Shader48 register-identity `OPEN`; `originalShaderRestored=false`, `ownerDeviceTestPending=true`. Session: `memory/sessions/20261110-GFX-chat-sevenpass-channel-apk-27.md`, test instructions `gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md`.

## GFX-MULTI-028S VERIFIED CI42749968983 — source-only negative GPU gate
- [CI42749968983](https://github.com/alwansan/raf/actions/runs/42749968983) COMPLETED SUCCESS, **159** unit tests; authenticated ZIP2 Shader48 (source SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385) 7 Pass state records and seven source Material21 slots.
- **7/7** Passes for each `culling`, `zWrite`, `zTest`, `alphaToMask` have `name` dynamic parameter override; `val` is not safe to interpret as fixed effective GPU enum without resolving material/source property. No static Cull/Depth/AlphaToMask state was proven. **7/7** have `rtSeparateBlend=false`; direct `rtBlend` field absent 7/7, which is not evidence that Blend is disabled.
- `m_ValidKeywords` nonempty in **7/7** source material slots, `m_InvalidKeywords` empty in **7/7**, direct legacy `m_ShaderKeywords` absent in **7/7**. Therefore old metadata absence must not be interpreted as source keyword absence.
- Ground enum names: official [Unity 2021.3 GraphicsEnums.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs). Fail-closed unit tests cover numeric enum fallback, invalid/unrecognized value and named dynamic override. Original numeric state values, private property names and source Shader48 bytes never exported; runner purge verified.
- OriginalShader48Restored=false; actual Android diagnostic channel APK (GFX026 [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585)) is a separate shader `Hidden/GfxLab/ChannelProbe`, not original Shader48; owner GPU channel images/COPY LOG remain pending. Signed APK checksum documented by parallel delivery owner in RESTORE and `gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md`.
- Next **GFX-MULTI-029S**: verify each dynamic `m_State.{culling,zWrite,zTest,alphaToMask}.name` is a true Shader48 `m_PropInfo` property and occurs in original seven Material `m_SavedProperties.m_Floats`/typed property tables. Reject mismatched alias and unknown parameter; do not guess enum from numeric fallback or source property array order.


## GFX-MULTI-029S — تجربة ربط أسماء حالات Shader48 الديناميكية بFloat الأصلية
- `session_id=20261110-GFX-chat-passstate-material-binding-29`, origin=chat، resumed_from=`20261110-GFX-chat-renderstate-enum-28`، base_sha=`2972cfce2736c0790db5fb317d201c313c69fdbf`.
- اختبار source-only جديد لاسم `m_State.{culling,zWrite,zTest,alphaToMask}.name` ضد Shader48 m_PropInfo original property name وضد سبع Material `m_SavedProperties.m_Floats` وEnum value category. لا نشر أسماء/قيم المصدر؛ عند غياب المطابقة لا تُخمن. Workflow `gfxlab-multi-state-material-floats.yml`. حتى لو 100% names match، هذا ليس original ShaderLab على GPU.
- APK diagnostic GFX-MULTI-026 الموقّع متاح للاختبار على الهاتف، original Shader48 still FALSE. تحديث الجلسة والذاكرة بعد CI.


## GFX-MULTI-029S — آخر نتيجة: ديناميكية حالات Shader48 أُثبتت جزئياً فقط
[CI42750996280](https://github.com/alwansan/raf/actions/runs/42750996280) **SUCCESS 164 tests**، 7 Passes و7 Material slots أصلية من ZIP2. جميع Cull/ZWrite/ZTest/AlphaToMask لها أسماء معلمات source parseable في كل Pass. لكن مطابقة `m_State.name` مع Shader48 m_PropInfo والمادة saved m_Floats: Cull **0/7** pass name match /0 material Float، ZTest **0/7**/0، AlphaToMask **0/7**/0؛ ZWrite **2/7** original shader property matches، **14** Float matches (2 Passes ×7 Material slots، وليست 14 مادة مستقلة)، كلها values 0/1 مسموحة. لا تستنتج أن بقية حالات الرسم مُعطّلة ولا تقرأ numeric `val` كحالة GPU نهائية. الأسماء والقيم المصدرية خاصة ومُحيت بعد CI. Android original Shader48=false، owner device test of diagnostic GFX026 pending.
- آخر جلسة `memory/sessions/20261110-GFX-chat-passstate-material-binding-29.md`، دليل دائم `gfxlab/SHADER48_DYNAMIC_PASS_STATE_EVIDENCE_AR.md`. التالي GFX-MULTI-030S فحص Pass m_NameIndices/compiled metadata البديلة + PC pixel reference إن لزم.
