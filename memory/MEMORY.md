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
