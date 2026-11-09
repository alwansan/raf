# ذاكرة GFX-LAB الدائمة — تحقيق شيدرات وألوان Raft Android
**أُنشئت 9 نوفمبر 2026 · role=GFX-LAB · origin=chat · مستقل عن T1–T5.**

## هدف صاحب المشروع
تشخيص سبب غياب الألوان الصحيحة والـshaders الديناميكية والإضاءة والنار والدخان والماء في نسخ Raft Android، ثم تجريب إصلاحات صغيرة مثبتة دون العبث بعمل الفريق. طلب المالك إنشاء فرع تجارب **مباشرة من main** ونظام ذاكرة يتيح استكمال العمل من دردشة أخرى بقراءة رسالة استعادة واحدة.

## هيكل العمل المستمر
- GitHub `alwansan/raf`; **فرع كتابتنا** `experiment/android-graphics-rootcause`، مصدره `main@9b89f62772c2c61f6269fd2249f8560af1522892`، وهو أصل خفيف (وليس نسخة كاملة من ملفّات feature).
- فرع الفريق `feature/android-native-port` للقراءة والمقارنة والتسليم **فقط**؛ CL/raft log وCL/test للقراءة فقط؛ ZIP2 المصدر الحقيقي المثبت `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- نقطة الاستعادة: `prompt/graphics-lab/RESTORE_AR.md`، بعدها `PROTOCOL_AR.md` و`docs/ROOT_CAUSE_REVIEW_AR.md` و`docs/EXPERIMENT_ROADMAP_AR.md` وذاكرة الجلسات.
- في كل دورة: `session_id` + `origin` + `resumed_from` + `base_sha` + `experiment_key` + `evidence_level`، ثم نتائج CI/حدود/next_step؛ حفظ ملف جلسة مستقل ولا مسح القديم.

## أدلة عالية الثقة (تقارير مرجعية)
1. [T3 postrestorer native](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_NATIVE_POSTRESTORER_DUMMY_EVIDENCE_2026-11-05.md): في تصدير CI42058825739 **بعد** restorers وقبل Unity يوجد **110/142** Dummy `.shader`، و**770/1536** Material-doc dummy references، links broken=0. «وجود GUID لا يعني برنامجاً حقيقياً». هذا سبب مؤكد في ملف التصدير، ولا يثبت أن كل جسم أبيض ناتج عنه.
2. [T3 original material inventory](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/W3_FULL_MATERIAL_SHADER_INVENTORY_2026-11-03.md): أصل 82 owner = 1556 Material، 165 Shader؛ Standard 674، Skin_Amplify 208، Shimmer 96، fire 11، غيرها. أصلي 921 renderer slots على Shader48 واحد ذي 4 Pass/33 linked VS/FS; ما زالت Identity current native غير مثبتة لهذا الهدف.
3. [Original selected material parity](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_AUTHENTIC_MATERIAL_EXPORT_PARITY_2026-11-05.md): 41/41 Materials، 150/150 RGBA، 227/227 TexEnv/UV matching، 89/89 internal texture pointers; 25 external refs unknown. [106/106 DXT5 semantic textures](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_NORMALMAP_DXT5_SEMANTIC_TEXTURE_FIDELITY_2026-11-05.md) preserved. لا تُصلح اللون بطمس بيانات أصلية سليمة!
4. [Original color space](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/W2_COLOR_SPACE_SETTINGS_2026-11-03.md): Linear؛ [4,050 textures](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/W2_FULLGAME_TEXTURE_COLORS_2026-11-03.md): 1173 Gamma / 2877 Linear. اختلاف Android import/runtime ما زال غير مثبت، وB02 سياسة sRGB أصلية مُتنازع عليها، إصلاح تلقائي موقوف.
5. [Phone APK89](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md): صور يد وطوف بيضاء وتأثير مربع، ماء/FFT error flood؛ المالك دخل وحفظ وأعاد فتح العالم، أي لا تعد مشكلة دخول APK86 نتيجة 89.
6. [T3 Smoke34](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_SMOKE34_SAMEEXPORT_DUMMY_2026-11-09_AR.md): 17 smoke-named particle renderer و34 slots لـShader48 واحد (غير fire34)، ShaderLab real same-export بقي Dummy؛ أصل Pass alpha blend، ColorMask RGB وZWrite Off؛ 4 DXBC stages ترجمت structurally ولكن 4/4 SPIR-V IO drift لا قيمة بصرية مثبتة. لا تخلط synthetic GLES lab مع actual Raft.
7. [Water](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/W4_BUILTIN_GATE_AND_WATER_FRONTIER_2026-11-04.md): Spectrum 1/6، Foam 1/2، Blur 1/2 في تصدير سابق، Kernel FFT 6 invalid على الهاتف؛ أصل 9 compute/42 embedded DXBC (ليس 42 distinct Unity kernels)، لا تقل أنه أصلح.
8. [T5 OBB](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T5_REAL_CL_OBB_PATCH_GUID_DIAGNOSIS_2026-11-05.md): تحذيرات GUID الثلاثة للـpatch.89، لا main.89؛ don't blame OBB for colors from warning alone. ملاحظة GPU OOM قديمة لا تعني سبب أبيض APK89.

## ما بقي مجهولاً
- أي exact Shader48 وهوية renderer لـwhite hand/raft والمربع على APK مثبت؟ هل current postrestorer/Unity shader compiled effective أم Dummy؟
- فهرسة variants/CB0/samplers/texture importer flags، dynamic runtime shader replacement، lighting/pipeline state وAdreno Vulkan/GLES render اختلاف.
- فحوص نصوص أصلية DXBC↔SPIR-V/ShaderLab لا تساوي runtime Android acceptance.
- أحدث نتائج فريق T3 وما أصبح مثبتاً بعد آخر قراءة لهذه الذاكرة يجب فحصها كل دورة.

## قرار منهجي
`RENDER-002/WATER-001` ما زالت OPEN؛ اللعبة NOT_READY 0/3. أول تجربة GFX-01 exact 921-use/white renderer original→postrestorer GUID→program/Pass. لا APK جديد قبل تكافؤ وتجربة Android مبررة. حافظ على صوت/Settings ودخول العالم الموثق؛ لا تتعارض مع الفريق. اقرأ [خارطة التجارب](../docs/EXPERIMENT_ROADMAP_AR.md).
