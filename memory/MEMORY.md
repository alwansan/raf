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
