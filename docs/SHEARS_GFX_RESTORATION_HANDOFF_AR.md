# Shears — سلسلة استعادة رسوميات أصلية قابلة للأتمتة

**GFX-LAB | 10 نوفمبر 2026 | النطاق مستقل عن T1–T5**

## حقيقة تم إثباتها على الهاتف
صورة المالك من مختبر Unity 2021.3.45f2 على Xiaomi 23013PC75G/Adreno 730/OpenGL ES 3.2، Linear، أظهرت **Shears** (المقص) الأصلي في الوضع الأبيض. تمييزه السابق original_player_like_skinned سببه اسم GameObject أب؛ ليس Mesh لاعب قابل للعب. عدد الرؤوس 375 والمثلثات 420 وRenderer واحد و0 أخطاء في التقرير. **هذا نجاح Geometry وStandard white وليس فشلاً في شيدر أصلي لم نستورده بعد.**

## مسار المصدر الفعلي لا التخمين
| المرحلة | مصدر وقياس | الحد |
|---|---|---|
| Mesh → SkinnedMeshRenderer | exact ZIP2 @15964ea8، 375v/420t، 375UV/375normal، 3 bones/root bone | لا يزال OBJ ثابتاً، وSkinning الحي لم يستعد |
| Material21 | 1 أصل مربوط محلياً بنفس المصدر SHA | المصدر مكوناته لا تظهر تلقائياً في APK |
| Texture2D | 9 TexEnv، 3 bound أصلية class28 و6 null، أدوار BaseColor/Normal/Metallic، 3,145,728 px | الصورة البيضاء القديمة لا تقول إن الأصل أبيض |
| Shader48 | 2 SubShaders / 7 Passes في المصدر الحقيقي | **لم يُحوّل** إلى Android ShaderLab/GLES أصيل |
| External resS | 3 immutable ZIP2 Git parts **141,557,760 bytes** من `sharedassets0.assets.resS` بدلاً من ملف 1.779GB كامل | القطع المختارة موثّقة بهوية Git الموقعة في commit، ولم يثبت هاش المورد الكامل من subset |
| Texture decode | Python UnityPy 1.25.4 أعاد صور PNG الثلاث داخل runner، المالك لا يرى loose textures | حفظ الأصول الخاص لم يُنشر، بل بيانات إحصائية |
| Unity v0.2 | Standard fallback WHITE→ALBEDO→PBR، وحزمة مستقلة | **تشخيص ألوان، لا استعادة شيدر 7 Pass** |

روابط المصدر المثبت:
- [GFX-002 source graph PASS](https://github.com/alwansan/raf/actions/runs/42705610994)
- [GFX-003 texture role/stream PASS](https://github.com/alwansan/raf/actions/runs/42706123513)
- [GFX-004 sparse stream decode PASS](https://github.com/alwansan/raf/actions/runs/42707235695)
- [GFX-005 actual Unity APK build](https://github.com/alwansan/raf/actions/runs/42707671345) (تحقق من أحدث نتيجته قبل اعتبار PNG/device PASS).

## مخطط أتمتة متدرج للمستقبل
1. SOURCE_LOCK: provider commit وSHA لكل original assets container، والتأكيد على mesh fingerprint وPPtr typed، لا name guess.
2. SOURCE_MATERIAL: تطابق Material21/Shader48/Texture2D28 باستخدام same-export lineage، حفظ الألوان الأصلية/scale offset/keywords في scratch خاص.
3. SOURCE_STREAM: قراءة Texture2D StreamingInfo والـGit blob tree bounds، تنزيل قطع محددة، تأكيد Git blob identity قبل ملء private sparse resource stream.
4. ASSET_DECODE: اختبار semantic albedo sRGB/normal DXT5nm/metallic linear، أصل sampler wrap/filter، CRC/PNG dimensions وsubmesh UV، بدون normalization أعمى.
5. SHADER_RESTORE: استخراج original Shader48 passes/stages/keywords and render states (Cull/Blend/ZWrite/ZTest/ColorMask/CB/samplers)، تحويل مكافئ دلالياً بمتغيرات Unity Android، وعدم افتعال Passes/flags.
6. UNITY_IMPORT: build Editor2021/Android actual، تحقّق من GUID/SubShaders/passCount/variants/shader.isSupported قبل إعلان قبول.
7. DEVICE_PROOF: نفس Mesh وCamera، أربعة أوضاع مستقلة لمقارنة الأبيض وalbedo وPBR والشيدر الحقيقي لاحقاً، سجل GPU/API/PNG/owner-acceptance. لا تخلط نجاح CI مع بكسلات Android.
8. DELIVERY: بعد إثبات عمل شيدر أصيل جزئياً وتوثيق regressions، سلّم تقرير patch مقيّد إلى T3 على branch feature بدون أن نغير ملفاتهم بأنفسنا.

## العيوب التي تستلزم اختباراً منفصلاً بعد نجاح ألوان PBR
- Texture2D أصلي كامل لكن **Shader48 ذو 7 Passes** لم يسترجع (المعيق الأساسي للـfidelity).
- ملف Normal يمكن أن يحمل DXT5nm channel packing مختلفاً عن استيراد Unity الجديد؛ يجب مقارنة tangent-space على مصدر موثق.
- MetallicGlossMap قناة اللمعان/ألْفا وسلوك sampler قد يختلف عن Shader الأصل وStandard.
- العرض الحالي OBJ ثابت؛ three bones/skeleton والـskinning/animation والـparent transforms غير مكافئة للمصدر.
- أي مقارنة بصرية تحتاج صورة الهاتف مع mode وAPI ووقت/scene لا صورة خارجية وحدها.

لا تعدَل `zip2` أو `main` أو `feature/android-native-port`. هذا سجل GFX-LAB فقط.
