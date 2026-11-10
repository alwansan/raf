# GFX-LAB | قرار إغلاق مرحلة موديلات/ميش/ماتيريال/تكستشر/Shader48
**10 نوفمبر 2026 — مراجعة اختبار المالك المرفوع GFX-MULTI-026 — قرار: NOT CLOSED**

> هذا الملف وثيقة تسليم تقني قابلة للاستعادة، وليس إنشاء عامل جديد. لا يجوز اعتماد عبارة «استعيدت جميع الشيدرات» بناء على نجاح Unity Standard أو قراءة ShaderCache من اختبار الهاتف.

## 1. المصدر والأدلة المنفصلة
- المصدر الأصلي المثبّت: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- APK الاختبار: `com.alwansan.raft.graphicslab.channels`, `GFX-MULTI-026`, [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585), signed APK SHA256 `8fef68d82748cd214b1f5f5f9c0b3903a80f343513ccb15fc35e12649c02ad52`.
- دليل المستخدم: أرشيف اختبار خاص SHA256 `adc08713ad67a987d0b30ac01b1b6e9004342b359aeb97ed1ee61866fecc4238`، ZIP CRC verified. فُحص محلياً، **لم تُرفع صور المالك أو binaries الخاصة به إلى GitHub**.
- الأرشيف: 16 لقطة JPEG × 2400×1080؛ 13 JSON `COPY LOG`؛ آخر `multi-report.json`؛ عشر ملفات binary `UnityShaderCache`، وبيانات IL2CPP التطبيق. وجود ملفات ShaderCache يثبت أن التطبيق يملك كاش مترجماً، **ولا يثبت هوية Shader48** ولا أن هذه العشرة تكافئ شيدرات PC.
- الهواتف والسجلات: `Xiaomi 23013PC75G` / Adreno (TM) 730، `OpenGLES3` (ES 3.2)، Unity `2021.3.45f2`، `Linear`. أكواد `errors=0` في **13/13 لقطات JSON المتوفرة فقط** و`firstError=""`; هذا لا يحل محل `adb logcat` أو GPU capture أو ضمان عدم وقوع خطأ خارج وقت التسجيل.
- شملت السجلات **كل M00–M05**؛ 7 لقطات PBR Standard Approx و6 Albedo Standard (كل موديل له الحالتان، وM00 له PBR إضافية). كل `COPY LOG` بقي `BASECOLOR/RGB/SOURCE_TEXTURE_COLORSPACE_IMPORT/SURFACE 0`، رغم أن **الصور** تتضمن عرض Normal وMetallic لـM00. لا توجد تسجيلات موثقة لـR/G/B/A منفصلة أو Force Linear أو Surface2/2 لـM03.
- ملفات الصور يدوياً: M00 المقص بمواد رمادية ونحاسية؛ M01 شخصية برتقالية ببدلة كاملة في pose ثابت؛ M02 أداة/قوس؛ M03 طبق متعدد المواد بألوان سليمة؛ M04 ذراعان منفصلتان ضمن mesh المختار، غير مثبت أن هذا خلل لأن العينة `complex_skinned_unidentified`؛ M05 جسم/أداة أسطوانية. لا تظهر في العينة مساحات white-dummy عامة أو كسر ميش واضح. الاختلافات المرئية بين Albedo وPBR هي استجابة تقريبية للإضاءة لا مرجع Shader48/PC.

## 2. مصفوفة البوابات (العدد والعينة فقط، لا تعميم)

| Gate | ما نطلبه للاكتمال | الدليل الحاضر | الحكم |
|---|---|---|---|
| G0 AUTHENTIC_SOURCE | SHA/Renderer/Mesh/Material/Texture exact identity | ZIP2 owner SHA مثبت؛ 6 موديلات المصدر؛ M00 Shears 375 vertex/420 triangle | PASS للعينة |
| G1 STATIC_MESH_TOPOLOGY | استعادة vertex/index/submesh/UV/normal/tangent بلا تخمين | OBJ مصدّر، triangles audited و6 موديلات ظهرت. لم تُغلق parity لكل tangent/vertex skin stream | PARTIAL |
| G2 SOURCE_MATERIAL_GRAPH | exact source refs, UV/tints, shared identities | 7 Renderer Material slots = 6 Material21 فريدة، 21 bound Texture links = 18 Texture2D فريدة؛ 63 TexEnv stored /42 null | PASS لجرد المصدر؛ **Unity alias preservation ليس مثبتاً** |
| G3 TEXTURE_SOURCE_SEMANTICS | exact format/channel/color space, wraps/mips and pixel parity | 21/21 decoded، DXT1×5 وDXT5×16، Normal Linear×7، BaseColor/Metallic sRGB×14، wrap Repeat وبقية settings | PASS لبيانات المصدر، GPU parity OPEN |
| G4 ANDROID_GLES_VIEWER | مصدر + Unity + هاتف مع تقارير واضحة | 16 صورة، 13 JSON، M00–M05 وكل Albedo/PBR، zero reported app errors | PASS لعرض Standard fallback فقط |
| G5 GPU_CHANNEL_MATRIX | BASE/NORMAL/METALLIC × RGB/R/G/B/A × SOURCE/FORCE_LINEAR + M03 slot1/2، JSON مربوط بصورة | Normal/Metallic previews بالصور؛ كل COPY LOG مسجّل BASECOLOR/RGB/SOURCE/surface0 | PARTIAL — يحتاج توثيق تجارب |
| G6 SOURCE_FLOAT_COLOR_VALUE | Material Float/Color semantics and exact import without defaults | 112/112 Floats و14/14 Colors match Shader48 property names؛ BaseTint white×7، Emission RGB black×7 | PARTIAL — Unity PBR يستعمل glossiness **0.45 hardcoded** |
| G7 SHADER48_AUTHENTIC_PROGRAM | نفس Shader48 2 SubShaders/7 Passes، compiled GL3/Vulkan binaries and 524 valid exact keyword/tier pairs, not Standard | source has 7 passes, 524 pairs, 1,435 linked rows, 1,275 referenced DXBC stage programs. `Shader.Find("Standard")` في APK؛ `originalShaderRestored=false` | **FAIL/BLOCKED** |
| G8 SHADER48_BINDINGS | exact Material property↔t#/s#/CB offsets/VS↔FS semantics and sampler state | 1,275/1,275 referenced DXBC without RDEF؛ `m_Parameters` absent، GFX029 ZWrite partial only | **FAIL/BLOCKED** |
| G9 RENDER_STATES | actual Cull, Blend, ZWrite, ZTest, AlphaToMask, ColorMask and pass/queue/shadow semantics | 7 Pass m_State؛ dynamic overrides 7/7; GFX029 only ZWrite linked 2/7 with 14 slot matches؛ Cull/ZTest/AlphaToMask 0/7 direct Material bridge | **FAIL/BLOCKED** |
| G10 SKINNED_RIG | exact bones, bind poses, weights, bone indices, animation & GPU skinning | M01/M04 source bones×100 and static-pose OBJ imported; `originalAnimationRestored=false` | **FAIL للـskinned** |
| G11 MATCHED_PC_DEVICE_PIXELS | matched PC/Android source shader and same camera pose/lighting/keywords/texture output, archived hashed captures, owner acceptance | صورة Android Standard فقط، لا PC المرجع ولا original Shader48 runtime | **FAIL/BLOCKED** |
| G12 REUSABLE_WORKER | deterministic extraction/import/shader recipe for unseen source items, same-export GUIDs, fail-closed report and per-family gates | أدوات SHA/source/CI جيدة، لكن shader-identity bridge not solved؛ لا تعميم على shader families أخرى | **NOT READY لإعلان استعادة كاملة** |

**قرار هذه الجلسة:** `ITEM_STATIC_ART_AND_STANDARD_VIEWER_EVIDENCE=true`، لكن `ORIGINAL_SHADER48_RESTORED=false` و`ALL_ITEM_SHADER_PHASE_CLOSED=false`. الأصلي يجب أن يظل Shader48 لا Dummy ولا نسخة Unity Standard توصف بأنها مكافئة بلا إثبات.

## 3. اختلافات فعلية اكتُشفت في الكود الحالي
1. `gfxlab/unity/Assets/Editor/GfxMultiAndroidBuilder.cs`: `imp.sRGBTexture=role=="basecolor"` في TextureImporter الخاص بعرض Standard؛ بينما أصل الصور الـMetallic محفوظ `m_ColorSpace=1` (sRGB) ×7 [GFX024](https://github.com/alwansan/raf/actions/runs/42745536309). **هذا source↔viewer discrepancy، وليس دليلاً وحده أن Standard Metallic يجب تغييره دون اختبار**؛ فمعنى channels/shader sampling الأصلي مجهول.
2. `pbr[slot].SetFloat("_Glossiness",.45f)`: ثابت تجريبي لا يستمد قيمة المصدر؛ Shader48 الأصل يحمل saved Float properties. أزل الوهم بأن `SOURCE_PBR_STANDARD_APPROX` استعادة تامة؛ يمكن لاحقاً حمل القيم الأصلية مؤقتاً داخل runner وتجربة A/B موثّقة.
3. يكوّن Unity builder مواد منفصلة لكل Renderer slot، مع أن مصدر العينة يحوي 6 Material21 فريدة مقابل 7 slots، و18 Texture2D مقابل 21 روابط. **اعتماد هوية الأصول المشتركة في استعادة project (ليس مجرد viewer) ما زال ناقصاً**.
4. نظام Log يسجل الحالة عند ضغط `COPY LOG` وليس كل تغيير موثّق بالصور. بصرياً جُرّب Normal/Metallic لكن القيم المرسلة في `text 3.txt` لا تغطيها. واجهة معاينة SOURCE COLORSPACE مقصوصة قليلاً على 2400×1080؛ إصلاح UX مستقل وليس blocker للأصل.
5. عارض `GfxMultiViewer.cs` مشهد استوديو إضاءة اصطناعية وStandard/ChannelProbe، ولا يحتوي ربط Shader48 المنفذ داخل اللعبة. لا ترقيه إلى مستوى `ANDROID_GAME_PIXELS`.

## 4. خطة الإغلاق ذات الأولويات

### P0-A — اعثر على ربط البرنامج الأصلي دون تخمين
- استمر في تدقيق metadata الأصلي `m_NameIndices` لكل Pass وحالات `m_State`/valid keywords؛ اربط name إلى Material/Shader property **بالمطابقة الحقيقية** فقط، ولا تستخدم order/fallback.
- حل missing reflection: 0/1,275 RDEF و0/1,435 program parameters. ابحث عن ShaderLab/HLSL الأصلي غير الموجود في typed `m_Script`، أو مصدر PC runtime/Shader reflection موثق ومستقل أو GPU capture محدد بنفس الـShader48؛ إن تعذر، اكتب `BLOCKED_NO_AUTHENTIC_MATERIAL_TO_CB_MAP` ولا تركّب CB/registers بالحدس.
- لكل واحد من 7 Passes، تحقق من VS/FS IO interpolation وt#/s#/CB، depth/alpha, cull, shadow/light, fog, GPU keywords. لا تستخدم `SPIRV-val PASS` وحده لإثبات التطابق.

### P0-B — بنية استعادة Shader48 فعلية
- فقط بعد اكتمال source register/CB bridge، أنشئ ShaderLab تحت هوية مستقلة وأثبت 2 SubShaders/7 Passes مع برنامج صالح GLES3 أو Vulkan وحالات RenderState/keywords الموثقة. لا تخلط شيدر التشخيص.
- برنامج البنية المصدرية يرفض أي Pass/variant ناقص؛ CSV-safe aggregate يشمل عدد variants المحققة، لا source DXBC/GLSL/HLSL.
- طبّق Renderer→Material→Shader exact chain في نسخة الاختبار، واربط original Material Float/Color/TexEnv دون `_Glossiness=.45` أو fallback مخفي.

### P1 — الإخراج البصري وRig
- اختبر أبسط سطح M00، متعدد الماتيريال M03، وskinned M01/M04. نقل bones/weights/bind poses الأصلية من SHA-pinned المصدر منفصل عن static OBJ viewer. لا تسمّ `M04 arms only` خطأً ما لم يؤكده source selected mesh وRenderer.
- التقط نفس الأصل على PC وAndroid مع camera/lighting/keyword/API ثابتة، ثم قارن pixel/normal/alpha/depth/shadows بمقاييس معلومة وحد قبول يعلن مسبقاً.
- أعد فحص sampler/color-space في Metallic: أصل sRGB، بينما importer للمادة Standard Linear. أعطِ GPU experiment Source-vs-Linear لا تنفّذ «تصحيح» تلقائياً قبل مرجع PC.

### P1 — إكمال قياس هاتف GFX026
- للـM00 وM03 على الأقل: `COPY LOG` بعد كل تغيير Role (BaseColor/Normal/Metallic)، Channel (RGB/R/G/B/A)، Sampling (SOURCE/FORCE_LINEAR)، وSurface 1/2 بـM03، وصورة لكل مجموعة. اختبارات logger جديدة تتحقق من قيم Android GLES في كل تقرير.
- إذا ظهر شيدر مفقود أو لون غير صحيح، اربطه بمرجع SHA للـMaterial/Texture الأصل وليس بقيمة RGB مرسومة يدوياً. نريد logcat/Unity errors إن ظهرت، لا نستنتج من zero errors في snapshot.

### P2 — مرحلة agent/mass restore بعد نجاح G7–G12
- صمّم هيكل worker مؤجل: source hash/identity checks → model/mesh/bones → exact source Materials/Texture2D semantics & alias reuse → restore correct Shader48 family and variants → Unity import/compile → GPU/PC pixel parity → owner acceptance. الفشل في أي طبقة يحوّل العنصر إلى `BLOCKED` لا `RESTORED`.
- أخرج لكل عنصر `source_sha, renderer_count, mesh_topology, mat_ref_identity, texture_roles, color_space, shader_family_id, passes, keyword_exact_pairs, CB_sampler_bridge, GPU_parity, rig_status, acceptance` بصيغة آمنة بلا GUID/raw assets.
- **لا ننشئ العامل الآن**؛ المالك سيعطي تعليمات تعيينه لاحقاً. لا نلمس `main` أو `feature/android-native-port` أو T1–T5 أو `zip2`.

## 5. الفصل عن المشاريع التالية
- **ماء وFFT/Compute:** عائلة مختلفة `WATER-001`، 9 compute source وkernel/GLSL/GPU stages؛ ليست جزءاً من نجاح Shader48 للموديلات.
- **دخان/نار/Particles:** شيدرات شفافية/Blend/Cull وParticle vertex streams مختلفة؛ يفتح محور جديد بعد معايير الفريق، لا يُعلن جاهزاً لمجرد أن M00 ألوانه صحيحة.
- **إضاءة/PostFX/ظلال:** الإضاءة الأساسية لموديل Standard على استوديو ليست parity للـPostFX والإضاءة والظلال داخل مشاهد Raft.
- **الرسوم لكل عناصر اللعبة:** هذه العينة **Shader48 واحد** لـ6 Meshes، وليست 165 Shader families أو جميع عناصر PC.

**القرار النهائي الحالي: NOT CLOSED.** لا نقل إلى مرحلة أخرى بناءً على ادّعاء نجاح Shader48. استكمال العمل يجب أن يبقى على P0-A/P0-B إلى أن تتوفر الأدلة الحقيقية، وعند الحاجة إلى مرجع PC/أصل shader مفقود نصرّح بعائق المصدر بدلاً من إخفائه.
