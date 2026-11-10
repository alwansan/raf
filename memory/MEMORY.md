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

## Actual first lab — GFX-AVATAR-001 (2026-11-10 checkpoint)
**CI real pass:** [42702078254](https://github.com/alwansan/raf/actions/runs/42702078254), Unity2021.3.45f2 Android IL2CPP ARM64 / GLES3, actual original ZIP2 three SHA owner files, one source player-like SkinnedMeshRenderer Mesh extracted as OBJ (375 vertices, 420 faces; **probably only one component, not proven entire player**), Unity import and build PASS, APK signature checked. [APK artifact](https://github.com/alwansan/raf/actions/runs/42702078254/artifacts/13711903486), bytes 9686808, SHA256 `727a0ad7174d720629d0fa5cd8723a810319ba224c92b4793a392cd1baf7bc3f`, package `com.alwansan.raft.graphicslab`. Standalone APK delivered directly in chat; user's device **not yet tested**. No OBB, no game-level shaders restored, no complete avatar proven.

**Runtime UI:** white Standard vs Unlit white, drag/pinch orbit, spin/reset, COPY LOG (clipboard JSON), persistentDataPath/gfxlab/report.json, original model category and mesh/GPU counters. Keep evidence stage distinct (source import success != Android device pixels). Detailed state/session: `memory/sessions/20261110-GFX-chat-avatar-001-42702078254.md`.

**Next:** owner checks the APK and reports screen/clipboard. Then group same-root SkinnedMeshRenderer parts and transforms/bindposes to build full character, verify source identity, recover actual material/shader/colors with T3 coordination. Do not run another heavy Unity build for minor source-only changes or mislabel a one-part mesh as whole player.


## تصحيح هوية الموديل وتعافيه — Shears (10 نوفمبر 2026)
**تصحيح نتيجة v0.1:** المستخدم شغّل APK الأبيض على Xiaomi 23013PC75G / Adreno 730 / OpenGL ES3.2 / Linear / Unity2021.3.45f2؛ رأى **Shears (مقص قص الصوف)**، لا اللاعب الكامل. GPU shader white Standard/Unlit مدعوم، 375 vertex/420 triangle، 1 renderer، errors=0. تصنيف المصدر `original_player_like_skinned` كان بسبب GameObject أب يحمل اسم Player، وهو **ليس** برهان هوية Mesh نفسها؛ لا تكرر هذا الوصف.

**تحقق المصدر الأصلي:** [GFX-SHEARS-002 CI42705610994](https://github.com/alwansan/raf/actions/runs/42705610994) SUCCESS، Mesh→SkinnedMeshRenderer→Material21→Shader48 كلّها نفس الأصل SHA، Material واحد، shader فيه **2 SubShaders / 7 Passes**، خانتا color، 9 TexEnv: ثلاث bound (Texture2D28 حقيقية) وست null أصلية، 3 bone pointers/root bone، 375 UV وNormal.

**أصل الصور:** [GFX-SHEARS-003 CI42706123513](https://github.com/alwansan/raf/actions/runs/42706123513) SUCCESS: albedo/basecolor + normal + metallic ثلاثة Texture2D، 3,145,728 original pixels في موارد .resS خارجية. [GFX-SHEARS-004 CI42707235695](https://github.com/alwansan/raf/actions/runs/42707235695) SUCCESS: استعادة PNG الثلاث داخل runner مؤقتاً مع exact Git-object SHA لثلاث قطع فقط 141,557,760 بايت من مورد resS واحد، واسترجاع source albedo tint الأصلي، دون تحميل 1.779GB كاملة أو نشر الصور المفردة.

**الفصل العلمي:** الأبيض في v0.1 قُصد به اختبار هندسة فقط. بيانات BaseColor الأصلية **موجودة**، ولم يكن غيابها إثباتاً لعيب GLES. تجربة GFX-SHEARS-005 تضع الألوان/normal/metallic في Unity Standard **تشخيصياً**، وليس استعادة shader الأصلي المعقد 7-Pass. [الـActions الحالي](https://github.com/alwansan/raf/actions/runs/42707671345)؛ لا تعلن APK/نجاح بكسلات حتى اكتمال الـCI وتجربة الهاتف. الحزمة الجديدة `com.alwansan.raft.graphicslab.shears` مستقلة عن البيضاء وتدعم أربعة أوضاع للمقارنة.

**خطوة الاستعادة التالية:** تحقق من نتيجة CI GFX-SHEARS-005 وسجلها في أحدث session، ثم APK فعلي وصورة + JSON من هاتف المالك عند النجاح. بعد ذلك فقط اعزل shader7-pass الحقيقي، ومختلف blend/z/cull/keywords/CB/input/output وتحويل D3D11→Unity Android، وقارن مع مرجع واقعي قبل اقتراح نقل الإصلاح إلى T3 في feature.

### GFX-SHEARS-005 confirmed real APK (latest)
[GitHub Actions 42707671345](https://github.com/alwansan/raf/actions/runs/42707671345) COMPLETED SUCCESS. Actual Editor Unity2021.3.45f2 Android ARM64 IL2CPP build signed and audited. [Artifact 13714487772](https://github.com/alwansan/raf/actions/runs/42707671345/artifacts/13714487772) expires 2026-11-16 22:06 UTC. APK **10,887,469 B**, SHA256 **f50f59f547a9d1dcdd934f0993df825a1df57e0312aa20f8a63e3bba1f0b1af2**, app id com.alwansan.raft.graphicslab.shears. Direct APK current chat delivery. Original user-confirmed Shears model source 375v/420t, exact original Albedo+Normal+Metallic and tint imported; Unity Standard white/albedo/PBR approximate modes. **No original 7-pass shader restored, no on-device v0.2 pixels proven.** Next owner tests four modes + COPY LOG. Detailed checkpoint memory/sessions/20261110-GFX-chat-shears-textures-42707671345.md and gfxlab/SHEARS_OWNER_TEST_GUIDE_AR.md.


## GFX-MULTI-001–003 — ستة موديلات أصلية (جلسة 10 نوفمبر 2026)
**دليل المالك الحديث:** الصور الثلاث وJSON من Shears v0.2 على Xiaomi 23013PC75G/Adreno730/OpenGLES3/Linear أظهرت ألوان BaseColor وNormal/Metallic مشهودة دون مشاكل بصرية واضحة؛ `errors=0` في جميع JSON الثلاثة، `originalShaderRestored=false`, `runtimeColoredPixelsVerified=false`. لا تعني نتيجة جميلة أن Shader7Pass الأصلي استُعيد؛ استخدام Unity Standard fallback كان مقصوداً ويجب الحفاظ على هذه التفرقة.

**نتيجة مصدر ثابتة:** [GFX-MULTI-001 CI42711514279](https://github.com/alwansan/raf/actions/runs/42711514279) SUCCESS. جرد SHA-original لـ1973 links renderer/mesh مع 824 typed Material→Shader chains؛ اختير 5 إضافية غير مكررة عن Shears:
- `M01`: 5095 vertices, skinned source مع 100 bones، category person من اسم source leaf + rig وليس إثبات شخصية اللاعب كاملة؛ داخل النسخة OBJ pose ثابت **ليس skinning أصلياً**.
- `M02`: static large_prop 1598 vertices, 1 material/3 images.
- `M03`: static large_mesh 5093 vertices, 1 material/3 images.
- `M04`: static tool 6514 vertices, 1 material/3 images.
- `M05`: static multi-material 2163 vertices, 2 materials/6 images.
- `M00`: Shears مقص المالك 375 vertices، مرجع baseline.

**الإخراج المصدر:** [GFX-MULTI-002 CI42712118731](https://github.com/alwansan/raf/actions/runs/42712118731) SUCCESS. ستة OBJ أصلية وسبع مواد و21 Texture2D مفكوكة فعلياً داخل Actions، 16 immutable Git chunks لإعادة إمداد .resS مجموعها 754,974,720 byte؛ لم تُرفع الصور ولا أسماء/معرفات source خاصة. اختبار source ≠ استيراد Unity ≠ هاتف.

**المختبر الحديث:** `gfxlab/unity/Assets/Scripts/GfxMultiViewer.cs` + `Assets/Editor/GfxMultiAndroidBuilder.cs`, يتيح اختيار 6 من شريط جانبي وأربعة أوضاع WhiteLit/WhiteUnlit/SourceAlbedoStandard/SourcePBRStandardApprox، تدوير/تكبير، إخفاء القاعدة، COPY LOG لكل موديل مع `modelId` و`sourceBones` و`originalShaderRestored`. يحاول بناء Unity 2021.3.45f2/Android GLES3/ARM64 مستقل `com.alwansan.raft.graphicslab.multi`.

**CI بناء حقيقي:** [GFX-MULTI-003 Actions 42712833407](https://github.com/alwansan/raf/actions/runs/42712833407). *لا تفترض نجاحه؛ اقرأ التشغيل الحالي والتوقيع والـartifact أولاً*. معايير قبول المرحلة هي Unity import actual six, 7 submesh slots, 21 original textures, signed APK, ثم المالك يختبره. `originalShaderRestored=false` و`originalAnimationRestored=false` حتى يثبت لاحقاً تكافؤ Shader48/rig الحقيقي.

**استعادة/دليل:** `prompt/graphics-lab/RESTORE_AR.md` أعيدت كتابته لتضمين آخر 3 تجارب؛ `gfxlab/MULTI_OWNER_TEST_GUIDE_AR.md` يشرح فحص M00–M05 وCOPY LOG. لا تعدل `main` أو فرع الفريق أو ZIP2 أو CL. لكل دورة ملف جلسة مستقل + STATE تحديث. 

## GFX-MULTI-003 — ثلاث إخفاقات Unity مثبتة، اختيار هندسي جديد (20261110-GFX-chat-reselected-sourcepack-03)
- CI42712833407: Unity OBJ importer أعاد صفر Mesh لموديل M02 (الاختيار التاريخي). CI42714952065: original fallback أعاد 1598 vertices و2095 triangles لكن Bounds رفض. CI42718266273: فحص source vertices أثبت `GFX_MULTI_DEGENERATE_SOURCE_VERTEX_BOUNDS_M02`. لا APK ولا توقيع في هذه التجارب.
- Commit 4839bdcef377d07c4aa47eea9357d05fd942e748 أدخل اختبار المصدر الفعلي بدل Renderer.bounds؛ commit b21b16c6f9937060a64ce7b3835d867cd576b7bd أدخل فحص المصدر float32 قبل اختيار أي نموذج.
- [GFX-MULTI-001 CI42719663373](https://github.com/alwansan/raf/actions/runs/42719663373) **SUCCESS**: رفض 12 مرشحا مع مساحة OBJ غير صالحة؛ خمسة أصلية جديدة M01 person 5095v/100 bones، M02 tool skinned 1666v/8 bones، M03 static multi_material 2163v/2 materials، M04 unidentified skinned 2445v/100 bones، M05 generic skinned 4452v/2 bones. M00 Shears 375v. المصدر ZIP2@15964ea8 ثابت، 7 material slots و21 texture links متوقعة.
- أرقام 16 chunks/754974720 bytes والـShader48 المصدر المشترك في GFX-MULTI-004 42715492781 للترتيب **القديم**؛ لا تُعمّم على الاختيار الجديد قبل إعادة source pack + shader audit. Re-run source-only workflows first; real Android APK build and owner pixels pending.
- أثناء الإصلاح استُعيد هذا الملف من قاعدة سابقة كاملة (HEAD 64a35a88404b387868de081f0e14d1f204d6f4eb)، لأن جلسة كتابة سابقة استبدلت المحتوى خطأ بنص `undefined`. الاحتفاظ بالذاكرة الأصلية أولى من تلخيص يطمس أدلة سابقة.

## اعتماد نموذج المصدر الجديد قبل Android (20261110-GFX-chat-six-android-retry-04)
- [GFX-MULTI-002 42720399689](https://github.com/alwansan/raf/actions/runs/42720399689) **SUCCESS**: ستة Mesh أصلية M00–M05 بالترتيب الجديد؛ 7 Material slots، 21 صور أصلية، 15 Git stream parts = 707788800 bytes، 0 generated normals، الأصلي-only في runner دون نشر صور أو OBJ/GUID/PPtr.
- [GFX-MULTI-004 42720400057](https://github.com/alwansan/raf/actions/runs/42720400057) **SUCCESS** للاختيار الجديد: Shader48 واحد أصلي مشترك، 2 SubShaders /7 Passes (4+3)، الـAndroid native shader parity FALSE، والريغ الأصلي غير مستعاد.
- بعد source stage PASS، نسخة Android الحقيقية تعيد Unity2021.3.45f2 IL2CPP ARM64 بناء 6 models 7 materials 21 images، وتشدد Triangle count parity للمصدر عند الاستيراد؛ تجعل التوقيع والتحقق من package عبر aapt إلزاميين. نتيجة البناء لا تُعرف حتى انتهاء CI، ولا تستخدم علامة نجاح مزيفة.

## GFX-MULTI-003 — نسخة Android الحقيقية الأولى للستة الجديدة (42720920391)
- [Actions 42720920391](https://github.com/alwansan/raf/actions/runs/42720920391) **COMPLETED SUCCESS** عند HEAD ee96e4d86dd6679be6814e4116368a664362b12a؛ Unity2021.3.45f2 Android IL2CPP ARM64 GLES3: ستة موديلات أصلية `M00–M05` استُوردت، Material slots = 7 وTexture links =21، وM03 ذات مادتين. Triangle count parity guard مرّ؛ build `GFX_MULTI_UNITY_REAL_BUILD_PASS` مثبت. أصل Shader48 المشترك 2 SubShaders/7 Passes لم يُنقل/يُستعد إلى Android، وRig/Animation لم يُسترد.
- `apksigner verify --verbose` و`aapt dump badging` اجتازا فحص التوقيع واسم الحزمة `com.alwansan.raft.graphicslab.multi`، ثم Artifact uploaded [ID 13721725242](https://github.com/alwansan/raf/actions/runs/42720920391/artifacts/13721725242) (انتهاء UTC 2026-11-16 23:39:48).
- APK المستخرج من artifact verified ZIP CRC، ARM64 Unity/IL2CPP، الحجم **24098726** بايت، SHA256 **`ef2b86b9384144fc3dd13c93d9b3a4e98cc07bfba3493b6a5c59b52d8db13f6c`**؛ طابق كلًّا من GitHub CI وفحص مستقل. لا OBB ولا إصدار اللعبة الكاملة.
- **Owner Android device six-model pixels=NOT_TESTED**. المطلوب اختبار M00–M05 عبر SOURCE_PBR_STANDARD_APPROX وتقديم 6 صور و6 COPY LOG، والتركيز على M01/M04 (Skinned source static) وM03 (مادتان). قبول المالك السابق يخص Shears v0.2 فقط.
- المصدر الأصلي SHA-pinned فقط داخل GitHub runner، لا raw OBJ/PNG/GUID/PPtr على الفرع العام. تسليم أولي ليس RENDER-002/WATER-001 READY.

## GFX-MULTI-005 — الهاتف وشروط إغلاق المرحلة (2026-11-10)
المالك سلّم 14 صورة و12 سجل JSON للموديلات الستة على Adreno730 GLES3؛ جميعها errors=0 مع originalShaderRestored=false وoriginalAnimationRestored=false. كود الاختبار يستخدم Unity Standard fallback وليس Shader48 الأصلي. عدد رؤوس M01 وM04 في Unity أقل من المصدر ويلزم vertex-stream parity. تجربة GFX-MULTI-005 مصدرية لتعداد بيانات Pass الأصلية، ولا تغلق Shader/rig. سجل: memory/sessions/20261110-GFX-chat-owner-six-shader-gap-05.md، المعايير: gfxlab/PHASE_CLOSURE_GATES_AR.md.

GFX-MULTI-005 CI42725841763 SUCCESS: 48 tests; original Shader48 source one linked object for 7 slots, 2 subshaders/7 passes, and all 7 have render-state, vertex, fragment and program-mask metadata. **This is SOURCE ONLY, not Android shader parity.** No full-stage closure. Next exact stage code/variant/CB/sampler audit.

## GFX-MULTI-006 and GFX-MULTI-007 — verified 2026-11-10
- [006 CI42726999353](https://github.com/alwansan/raf/actions/runs/42726999353) PASS, 52 tests: Unity2021 m_PlayerSubPrograms contains 7-pass original VS/FS source variant metadata; source compiled-platform metadata=1, compression-metadata=1. There are substantive original variants with source blob indexes and keyword metadata, but not Android equivalents.
- [007 CI42727286357](https://github.com/alwansan/raf/actions/runs/42727286357) PASS, 54 tests: all OBJ original vertices used in triangles, so Unity M01 and M04 374-vertex delta and M02 4-vertex delta are NOT caused by unused OBJ indices. Test 008 pending tests float32 attribute identical dedup.
- Exact original Shader48 Android runtime remains FALSE; rig and PC parity remain open.

GFX-MULTI-008 [CI42727777657](https://github.com/alwansan/raf/actions/runs/42727777657) SUCCESS 57 tests: unique float32 position+UV+normal vertex attribute counts exactly match Unity import ALL six models (M01 5095→4721 delta374, M04 2445→2071 delta374, M02 1666→1662 delta4; M00/M03/M05 unchanged). All original vertex indices are referenced per CI007. Difference strongly explained by duplicate attribute merging, NOT disappearing triangles. Full face-index parity/rig/source Shader48 still open.

## GFX-MULTI-009 SOURCE binary original Shader48 table (2026-11-10)
[CI42728348900](https://github.com/alwansan/raf/actions/runs/42728348900) SUCCESS 59 tests. Original source private UnityPy parser found a compiled ShaderProgram table with 1656 entries, platform metadata D3D11 but mixed program type labels incl GLES family 188; every source payload magic classified other. compressed blob 163501 bytes, total parsed program code bytes 242218471. **Not Android shader proof; unusual mixed types/memory expansion need independent validation**. GFX-MULTI-010 audits pass variant references to binary table with no raw bytes/public source, in session 20261110-GFX-chat-shader-binary-variant-links-10.

## GFX-MULTI-010 verified source DX11 links (2026-11-10)
[CI42731206453](https://github.com/alwansan/raf/actions/runs/42731206453) completed SUCCESS with 62 tests. All 1435 original Shader48 source VS/FS variant links to compressed compiled table are valid and exact GPU type match (0 mismatches/invalid), all seven passes reference DX11 programs with embedded DXBC signature, not general table's orphan GLES family records. Compressed blob bytes 163501; decompressed LZ4 buffer 4338048; sum of bytes of all parsed program-code records 242218471. Presence/source structure NOT Android proof. GFX-MULTI-011 attempts a single exact paired VS/FS DXBC translation privately. See session 20261110-GFX-chat-shader-pass-pair-spirv-11.


## GFX-MULTI-011 exact DXBC pair CPU translation (2026-11-10)
[CI42731898965](https://github.com/alwansan/raf/actions/runs/42731898965) SUCCESS with 65 tests. One genuine original Shader48 Pass 0 VS+FS pair with identical original keyword and hardware bucket was privately extracted; both original DXBC containers translated by vkd3d-compiler to Vulkan1.1 SPIRV and passed spirv-val. All seven Passes have >=1 exact original source stage pair (total 524 pairs across passes). This is **CPU feasibility, not shader restoration on Unity Android or PC pixel equivalence**. GFX-MULTI-012 now tests SPIRV stage interface and GLSL ES offline conversion. Session 20261110-GFX-chat-shader-gles-stage-io-12.


## GFX-MULTI-012 original shader GLSL ES310 offline proof (2026-11-10)
[CI42732370025](https://github.com/alwansan/raf/actions/runs/42732370025) SUCCESS with 69 tests. Exact original single DXBC VS+FS pair both Vulkan1.1 SPIRV validated and SPIRV-Cross GLSL ES 310 sources offline syntax compiled with glslangValidator. Reflect safe stage IO: seven VS outputs and seven FS inputs, all seven locations/types equal; 0 missing/type differences. Resources: fragment 7 UBO/7 separate images/6 separate samplers; vertex 5 UBO. Original Shader48 runtime on Android FALSE. GFX-MULTI-013 evaluates one exact pair for all 7 Passes; see 20261110-GFX-chat-all-seven-pass-gles-13.

## 2026-11-10: GFX-MULTI-013 7/7 source pass CPU proof, not device shader
[CI42732808109](https://github.com/alwansan/raf/actions/runs/42732808109) SUCCESS 71 tests. All 7 authentic original Shader48 passes (2 SubShaders, 4+3 Pass) had at least one exact keyword/tier matched original DXBC VS+FS pair privately translated DXBC→Vulkan1.1 SPIR-V→GLSL ES310 offline; 14/14 stage compile/syntax validations succeeded and seven VS/FS stage IO location/type checks matched. 524 exact original pairs exist but only 7 representative pairs tested. Program bindings (CB/sampler/image), all variants, pass states, original rig, Unity Android GPU/Adreno, PC pixels remain UNPROVEN. Stage OPEN, not ready to create the mass model restoration agent. See gfxlab/REUSABLE_MODEL_RESTORATION_GATES_AR.md and 20261110-GFX-chat-all-seven-pass-gles-13.


## 2026-11-10 GFX-LAB persistent session updates / source RDEF correct interpretation
The owner requires updating `prompt/graphics-lab/RESTORE_AR.md`, `memory/sessions/<session_id>.md`, `memory/STATE.json`, `memory/MEMORY.md`, and `gfxlab/OPEN_WORK_AND_IDEAS_AR.md` at the end of every work cycle; this was added to live restore. GFX-MULTI-014 [CI42733664716](https://github.com/alwansan/raf/actions/runs/42733664716) SUCCESS found no RDEF in real Shader48 Pass0 VS/FS; original CB/resource counts **unknown**, not zero. Source parser corrected to JSON null on missing RDEF. Device shader still NOT restored. Next GFX-MULTI-015 count RDEF/chunk availability on all 7 passes. Latest session 20261110-GFX-chat-persistent-roadmap-15.


## GFX-MULTI-015 selected for source-only next step (2026-11-10)
Latest session `20261110-GFX-chat-rdef-seven-pass-source-16`, resumed after persistent roadmap. Tests original RDEF coverage for 14 stage containers from all seven Shader48 passes, one source-exact VS/FS pair each. CI pending at commit creation. RDEF missing must be JSON null/unknown, NOT zero. This is source-only, original Android shader and material/CB sampler semantic parity remain open; see `gfxlab/OPEN_WORK_AND_IDEAS_AR.md` and live restore.


## GFX-MULTI-015 source RDEF all-pass coverage (2026-11-10)
[CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) SUCCESS, 80 tests. Genuine Shader48 2 SubShaders/7 Passes, one original exact keyword/tier VS/FS per Pass (14 total): **RDEF absent in all 14**, each has SHDR and source IO signature chunks. Thus original RDEF CB/binding counts UNKNOWN, even though translated SPIRV includes resource descriptors. No Android shader restored, no full variant coverage. Next GFX-MULTI-016 strict SHDR declaration opcode inspection/independent register semantic reflection; persistent backlog updated. Latest session 20261110-GFX-chat-rdef-seven-pass-source-16.


## Started GFX-MULTI-016 original stripped DX11 declaration inventory (2026-11-10)
The original Shader48 per-pass selected DXBC stage chunks contain SHDR, not RDEF; [GFX-MULTI-015 CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) 14/14 RDEF absent. GFX-MULTI-016 uses authoritative Microsoft's D3D10_SB_OPCODE_TYPE enum (resource 88 / CB 89 / sampler 90 / raw 161 / structured 162) and fail-closed token stream parsing to count source declarations in all 14 stages. No original register indexes or shader bytes public; no CB/Material binding or Android GPU equivalence. Latest session 20261110-GFX-chat-shdr-declaration-census-17, backlog maintained.


## GFX-MULTI-016 SHDR resource declarations SOURCE success (2026-11-10)
[CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984) SUCCESS 85 tests. Real Shader48 selected 14 source DXBC stage token streams: 66 original dcl_constant_buffer, 29 dcl_resource, 27 dcl_sampler, no raw/structured. Source Pass0 VS 5 CB, FS 7 CB/7 texture/6 sampler, agrees in counts with SPIRV reflect report. **Actual DX11 b/t/s register slots not yet decoded; equal counts do not prove matching material bindings, CB offsets or GPU parity.** Next GFX-MULTI-017 private register operand parsing. Session 20261110-GFX-chat-shdr-declaration-census-17, backlog persisted.


## Started GFX-MULTI-017 exact original DX11 operand source slot audit
Following GFX-MULTI-016 [CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984), source SHDR has 66 CB/29 Resource/27 Sampler declaration entries on 14 representative stages. GFX-MULTI-017 parses operand type, index dimension and immediate32 slot numbers privately with fail-closed tests. Aggregate counts only public; not yet SPIRV binding equivalence, not Android Shader48. Session 20261110-GFX-chat-original-register-operands-18; backlog updated.


## GFX-MULTI-017 original DXBC registers recovered privately (2026-11-10)
[CI42737442510](https://github.com/alwansan/raf/actions/runs/42737442510) SUCCESS 89 unit tests. Fourteen original Shader48 VS/FS SHDR streams' declaration operands passed strict type/index-dimension/immediate32 parsing. Private register slots: 66 CB declarations (66 with nonzero CB declared size), 29 resource, 27 sampler; **0 duplicate slots within stage**. No register indices/CB sizes exported. Does NOT prove source-to-SPIRV descriptor binding, material/normal/metallic sampler layout, or Android GPU Shader48. Next GFX-MULTI-018 compare original register index sets vs reflected SPIRV descriptor sets privately, then full material binding/CB layout. Latest session 20261110-GFX-chat-original-register-operands-18; persistent backlog updated.


## GFX-MULTI-018 started: independent source register vs converted SPIRV reflection numbers (2026-11-10)
After GFX-MULTI-017 CI42737442510 success (private original source 66 CB/29 resource/27 sampler unique slots on 14 shader stages), GFX-MULTI-018 compares private original immediate32 register sets to reflected SPIRV `set/binding` resource entries for one authentic VS/FS pair per 7 Passes. Reports aggregate counts/overlaps only. Numeric parity, if observed, does not prove source material, CB offsets or Android shader correctness. Latest session `20261110-GFX-chat-source-vs-spirv-binding-19` and backlog updated.


## GFX-MULTI-018 NUMERIC REGISTER REMAP discovered (2026-11-10)
[CI42738042943](https://github.com/alwansan/raf/actions/runs/42738042943) SUCCESS 93 tests, 7 authentic Shader48 original passes, 14 VS/FS stages. Original declaration counts equal SPIRV reflections in 42/42 groups, 122 resource declarations/122 reflected rows, no missing/duplicate descriptor bindings. **All 14 CB source-register sets numerically equal corresponding SPIRV binding sets**, but original fragment DX11 texture resource register sets equal SPIRV binding sets in **0/7** and samplers in **0/7**; 28/42 overall exact numeric groups include 14 empty vertex resource/sampler sets. This exposes texture/sampler descriptor remap, not missing original textures. Semantically exact source t#/s# to converted SPIRV descriptor map and source Material TexEnv/CB layout remain OPEN. Do not install as real Android ShaderLab until mapping proven. Source shader private; run purged. Latest session 20261110-GFX-chat-source-vs-spirv-binding-19, roadmap updated.


## GFX-MULTI-019 symbolic vkd3d register name binding probe (2026-11-10)
Started session 20261110-GFX-chat-symbolic-binding-map-20 on source ZIP2 fixed SHA, after CI42738042943 numerically proved resource/sampler SPIRV binding renumbering. vkd3d-shader public source indicates generated OpName tN, sN, cbN_size; GFX-MULTI-019 privately tests exact names against source SHDR register declarations and reflected set/binding for 14 stages/7 passes. Names and original register indices never public; even complete generated symbol match is not original Material TexEnv or CB byte-layout semantic proof, no Android shader runtime claim. Live restore and persistent backlog updated.


## GFX-MULTI-019 proven real original DX11 t/s names to SPIR-V descriptors (2026-11-10)
[CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) SUCCESS 98 tests. Original Shader48 7 genuine source Passes, 14 paired stages; **all 29 source texture t# and all 27 source sampler s# registers matched exact compiler-generated vkd3d OpNames to SPIRV descriptor set/binding** (56/56). All 56 descriptor binding numbers differed from original DX11 register numeric IDs, so direct source binding is WRONG. 66 source CB generated names unrecognized, 28/42 groups fully matched include 14 empty vertex t/s sets; full resource-name identity FALSE. Original material m_TexEnv property to t/s register, CB byte layout, proper normal/sRGB/smoothness semantics and GPU Android still unverified. First CI 42739322749 failed synthetic fixture only; corrected CI 42739427552 succeeded. Next GFX-MULTI-020 investigate independent Shader48 SerializedSubProgram m_TextureParams/m_Samplers plus property name-index table to Material TexEnvs. Restore 20261110-GFX-chat-symbolic-binding-map-20, backlog kept.


## Started GFX-MULTI-020 independent Shader48 original TextureParam to Material TexEnv metadata (2026-11-10)
GFX-MULTI-019 [CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) verified private source t/s symbolic SPIRV descriptor mapping 56/56 while 66 CB names remained unmatched. GFX-MULTI-020 now uses Unity 2021.3 m_Parameters.m_TextureParams and per-Pass m_NameIndices to independently associate original shader t/s register indices with named Texture parameters and seven original Material m_SavedProperties.m_TexEnvs. Source registers/texture/property names kept private, only safe counts exported. This is not shader GPU/CB/pixel proof. Latest session 20261110-GFX-chat-original-material-texenv-21, backlog updated.


## GFX-MULTI-020 authentic original Material and Shader metadata bridge absent (2026-11-10)
[CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) SUCCESS 103 tests. Original ZIP2 6 Mesh / 7 Material21: 63 `m_TexEnvs`, 21 bound original Texture2D and 42 source null; original Shader48 had 27 serialized shader properties and 7 Passes with per-pass NameIndices, **but none of the 14 selected source DX11 VS/FS program rows contain SerializedProgramParameters m_Parameters**. Thus no authoritative Material property name→source DX11 t/s register association from that field; 0 mapped, and originalShaderRestored=false. This confirms prior GFX-MULTI-006 had zero parameter metadata variants, rather than proving no textures. Prior GFX019 established t/s register→SPV 56/56, but not material name mapping. Next source-only GFX021 detect any actual original m_Script/text/sidecar source reference; then fail closed and preserve blocker. Session 20261110-GFX-chat-original-material-texenv-21, backlog and restore updated.


## GFX-MULTI-021 original embedded Shader48 source text and Material property proof (2026-11-10)
After GFX-MULTI-020 CI42740776655 confirmed 7 material source TextureEnv tables (63 slots, 21 bound) but 0/14 Shader48 source m_Parameters, GFX-MULTI-021 checks whether m_Script / actual embedded original HLSL text survives and how many bound Material TexEnv property labels appear in original Shader48 m_PropInfo. Text and proprietary names stay private, report counts only. No source property->DX11 t/s semantic map claim until explicit evidence. Latest session 20261110-GFX-chat-original-shader-text-source-22, backlog maintained.


## GFX-MULTI-021 original Shader48 material-to-property identity proven, embedded shader source absent (2026-11-10)
[CI42741817991](https://github.com/alwansan/raf/actions/runs/42741817991) SUCCESS 107 tests. ZIP2-original Shader48 27 serialized shader properties (9 texture-type). All 63 saved TexEnv slot names across 7 original Material21 records match Shader48 properties, all 21 bound Texture2D entries match, distributed 7 basecolor/7 normal/7 metallic. All other 42 original TexEnv slots are null; do not fill with placeholders. Original class48 shader typed object has no `m_Script` source field, 0 bytes, no CG/HLSL/register text. With GFX020 0/14 selected `m_Parameters` and GFX015 14/14 RDEF absent, original Material property name→DX11 register bridge is NOT AUTHORITATIVELY RECOVERED from selected fields. GFX019 separately proved DX11 56 t/s slots to SPV descriptor names, but does not bridge property names. Before concluding globally check nonrepresentative variants and same-export source evidence (GFX-MULTI-022). Original Shader48 on Android false. Latest session 20261110-GFX-chat-original-shader-text-source-22; blocker doc `gfxlab/SHADER48_MATERIAL_REGISTER_BRIDGE_BLOCKER_AR.md`; persistent backlog updated.


## GFX-MULTI-022 — exhaustive linked-variant reflection sweep (2026-11-10)
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) **SUCCESS**, 119 tests; source ZIP2 SHA locked. All **1,435/1,435** original Shader48 stage-variant link rows validated, including legacy and Unity 2021 player records; **524** exact keyword/hardware-tier VS/FS pairs; **1,275** unique referenced stage programs decoded as bounded authentic DXBC. RDEF present **0/1,275**; RDEF absent **1,275/1,275**. Across all 1,435 linked rows: `m_Parameters` blocks 0, texture parameter arrays/entries 0, constant-buffer binding arrays/entries 0, top-level sampler metadata rows 0, top-level constant-buffer metadata rows 0. The first attempt [CI42742873015](https://github.com/alwansan/raf/actions/runs/42742873015) completed the source scan but failed its summary assertion because zero-valued Counter keys were omitted; explicit zero counters fixed it. Private source purge succeeded in both attempts.

**Decision:** `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS`. This is stronger than the 14 representative-stage census, but does not include unreferenced entries in the 1,656-entry compiled table. The 56/56 DX11 t/s→SPIR-V symbolic mapping from GFX019 remains valid; the Material-property→source-register edge remains unknown. No original Shader48 Android runtime, GPU pixels, PC parity, APK, or owner acceptance. Original Shader48 restored=false.

**Next GFX-MULTI-023:** source-only Material/Texture2D semantic census across seven materials and 21 bound textures: role/format/color-space/mip/stream metadata, UV scale/offset, tint/color/float metadata, and role-specific decoded-channel statistics. Use authenticated sparse ZIP2 streams and publish safe aggregates only.


## GFX-LAB persistent state after GFX-MULTI-022
- Latest session: `20261110-GFX-chat-variant-reflection-sweep-23`; source ZIP2 remains pinned to `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; write scope remains only `experiment/android-graphics-rootcause`.
- The 1,435 linked Shader48 variant rows / 1,275 unique referenced DXBC programs have now been surveyed. All 1,275 lack RDEF and all 1,435 rows lack parameter/sampler/CB reflection metadata. The property-name→DX11 register bridge is blocked for the full referenced set; do not guess.
- GFX-MULTI-023 is the next source-only Material/Texture2D semantic audit. Keep shader execution, Android pixels, PC parity, rig, water/FFT, fire and smoke as separate open gates.


## GFX-MULTI-023 — original Material/Texture2D semantics and channel census (2026-11-10)
[CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) **SUCCESS**, 128 tests. Pinned ZIP2 source; six models, seven original Materials, 63 TexEnv slots (21 bound / 42 null), seven BaseColor + seven Normal + seven Metallic textures. All **21/21** original Texture2D images decoded with exact dimensions; 53,477,376 pixels examined privately. Only 15 authenticated stream chunks / 707,788,800 selected bytes were hydrated; safe aggregate artifact uploaded and all private source/texture/stream data purged.

Material facts: 14 color slots, 112 float slots, 0 int slots; all seven authored tint slots are identity white; all 21 role-specific UV scale/offset transforms are identity. Thus non-white tint and UV transforms do not explain the current material appearance differences.

Texture code distributions (raw serialized codes; do not infer color-space or format semantics from these counts alone): format code BaseColor 10×5 + 12×2, Normal 12×7, Metallic 12×7; color-space code BaseColor 1×7, Normal 0×7, Metallic 1×7; mip-count code BaseColor 11×3/12×4, Normal 11×3/12×4, Metallic 11×5/12×2; filter-mode code 1×21. Texture settings, anisotropy and mip-bias fields were present on all 21. Generic `m_WrapMode` code was unavailable in this type tree; axis-specific wrap fields still need inspection.

Channel census: BaseColor R/G/B variable 7/7; Alpha variable 2/7 and fully opaque 5/7. Normal R constant 7/7 while G/B/A variable 7/7; tested A+G with constant R+B signature candidate 0/7, so the conventional DXT5nm hypothesis is not supported by this simple channel signature. Metallic Alpha variable 7/7; this is only a candidate channel for additional data such as smoothness, not proof of shader semantics.

The first attempt [CI42743969290](https://github.com/alwansan/raf/actions/runs/42743969290) successfully planned the exact 15 chunks but failed when the audit re-read the manifest after sparse checkout intentionally excluded it. The correction reuses previously SHA-verified staged owner assets; [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) then completed all steps and private purge successfully. Artifact [13730562085](https://github.com/alwansan/raf/actions/runs/42744204412/artifacts/13730562085), expires 2026-11-17T02:40:48Z UTC.

**Limits:** raw numeric texture format/color-space codes are not yet semantically mapped; axis-specific wrap fields and float-property meanings remain open. No shader bytes, source names, pointers, raw pixels or image files were exported. No Shader48 execution, PC/GPU pixel parity, Adreno proof, APK or owner acceptance. `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`.


## GFX-LAB persistent state after GFX-MULTI-023
- Latest session: `20261110-GFX-chat-material-texture-semantics-24`; all 21 original textures were decoded privately and safely summarized, with no source image/pixel export.
- The seven materials have white identity tint and all 21 UV transforms are identity. Source texture format/color-space/mip codes and channel variability are recorded in the session; do not interpret raw codes without an authoritative Unity 2021.3 mapping.
- Next: GFX-MULTI-024 inspects material scalar semantics and wrap U/V/W; original Shader48 and Android GPU proof remain false.

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

## GFX-MULTI-026S original seven-pass state census — CI42749148702 SUCCESS (2026-11-10)
Source-only, pinned ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, **154 unit tests** passed after an initial CI42749035585 sparse-checkout test setup failure (4 Unity contract tests looked for omitted Unity assets; source-free-only tests now skip Unity-only contracts when files are intentionally absent). Verified all **7/7** Shader48 source Pass rows have an `m_State` dictionary and tags, with metadata for Cull, ZWrite, ZTest, zClip, Blend separate, alphaToMask, stencil and fog; direct `rtBlend` and generic `colorMask` keys absent. Presence does NOT prove a correct runtime render state or effective Blend/ColorMask behavior. Seven original Material slot rows: instancing enabled 7, shader-default queue -1 in 5, explicit nonnegative queue in 2; `m_ShaderKeywords` direct field absent in 7/7 (not proof there are no keywords in alternate metadata). All source values and IDs private; runner purge successful. Safe artifact [13732363372](https://github.com/alwansan/raf/actions/runs/42749148702/artifacts/13732363372) expires 2026-11-17T03:24:33Z.
- **GFX-MULTI-026 APK build currently NOT completed:** [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) started at commit 818298ce8fcb71d7906f977c5d03cc8d619db57e, Unity 2021.3.45f2 real import/build IL2CPP ARM64 GLES3 is in progress. Six original SHA-authenticated models, 21 texture role links, original color-space vs forced linear diagnostic channel probe added. Package `com.alwansan.raft.graphicslab.channels`, Android minimal standalone APK only. Verify BuildPipeline, signature, package name, SHA256/CRC, artifact, purge before declaring APK issued.
- **Negative evidence:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `devicePixelsVerified=false`, `PCPixelParityVerified=false`. The new channel probe shader `Hidden/GfxLab/ChannelProbe` is independent diagnostic-only GLES3, **not Shader48**. WATER-001, RENDER-002 remain OPEN.


## GFX-MULTI-028S source-only Shader48 render state enum categories started (2026-11-10)
The branch progressed to GFX-MULTI-026S [CI42749148702](https://github.com/alwansan/raf/actions/runs/42749148702) SUCCESS 154 tests: seven Shader48 m_State blocks present, typed state metadata for Cull/ZWrite/ZTest etc.; direct rtBlend/colorMask keys absent. Material slots instancing 7/7, 5 default queue and 2 explicit; m_ShaderKeywords direct field absent, not keyword absence. GFX-MULTI-028S now checks source fixed enum vs dynamic name overrides and alternate Unity Material keyword fields with official Unity2021.3 CullMode/CompareFunction code; source values and shader IDs private. Android channel GFX026 build CI42748792585 independent in progress; not original Shader48. Session 20261110-GFX-chat-renderstate-enum-28, all plans persistent.
