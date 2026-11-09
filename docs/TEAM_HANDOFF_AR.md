# تسليم تشخيصي للأعمال القادمة مع T1–T5 — GFX-LAB
**إعداد GFX-LAB، 2026-11-09. هذا ليس تغييراً لأوامر العاملين ولا موافقة على بناء APK.** اقرأ آخر جلسات كل عامل على `feature/android-native-port` قبل اقتراح أي نطاق حتى لا يتكرر عمله.

## مسارات تكامل غير متداخلة
| العامل | مصدر/تجربة يملكها | سؤال GFX-LAB الدقيق المطلوب من دليل جديد |
|---|---|---|
| T3 — RENDER-002 | استعادة الشيدرات والمواد وSmoke34 وrenderer exact original identity | أولوية 1: هل original Shader48 ذو 921 slot ما زال Dummy **في آخر same-instance postrestorer**؟ هل shader Smoke34 المرتبط بالهوية الصحيحة يحتفظ ColorMask RGB/alpha وكم compiled variant usable؟ **لا تعالج** texture/Material RGBA التي أثبتت parity في عيناتها. |
| T2 — WATER-001 | Foam/Spectrum/Blur، original managed Shader.Find / Material(Shader) dataflow | هل runtime `Shader.Find` يرجع Shader حقيقي وليس Dummy/null على Unity Android؟ أعد نفس المصدر/CB/sampler/pass indices ولا تُستدل على أصل Foam من Material PPtr غير موجود. |
| T1 — WATER-001 | FFT/Kernels، أصل DXBC، original SPIR-V ↔ Unity trace | ما الدليل على هوية kernel indices 2 و6 في شيدر runtime؟ هل جميع read sites/coordinates والمخرجات متكافئة؟ الاختبارات synthetic OpenGLCore ليست Adreno. |
| T5 — integration/mini-lab | آخر native postrestorer audit، النسخة الموقعة APK/OBB، المختبر الموحد | عند build **مرخص مسبقاً**: خزّن safe aggregate exact Shader identity/dummy/compiled variants وpass errors؛ رقم النسخة والـOBB والـGPU API. لا تُطلق build فقط لأجل هذه الملاحظة. |
| T4 — runtime world/input | دخول العالم/الحفظ/controls | حافظ على نجاح save/reopen في APK89 ومعلومات scene boundaries؛ لا نطلب منه تعديل الرسوم أو تعريض بيانات اللاعب. |

## طلب تجربة A/B موثوقة
1. من الصورة المشوهة حدد game scene/Renderer Material slot في scratch خاص أو اسم عام إذا كان public-safe. لا تنقل كل أسماء أو GUIDs الأصلية للمستودع العام.
2. ثبّت original Shader48 → exported same-instance GUID → actual postrestorer program → Unity import → real Raft runtime shader identity، مع مستقلة cache/manifest لكل حلقة.
3. قارن PassCount/IsSupported/Shader keywords/texture binding/CB layout، ثم PNG للبكسلات من game camera عبر تجربة جهاز محددة؛ mini GLES color لا يكفي.
4. صنّف النتائج: `SOURCE_PROGRAM_DUMMY`, `PASS_MISSING`, `VARIANT_STRIPPED_OR_UNSUPPORTED`, `TEXTURE_BINDING_OR_SRGB_MISMATCH`, `LIGHT_POSTFX_MISMATCH`, `UNKNOWN`. لا تستنتج "الجهاز ما يدعم" دون تقرير API/compiler رسمي.
5. إن تبيّن أن المصدر/Unity صالح لكنه على الهاتف سيئ، أطلق testpack متحداً بالتنسيق مع T5، وتوقف عند أول mismatch بدل تجربة 5 APKات.

## إحالات أساسية
- [T3 actual postrestorer](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_NATIVE_POSTRESTORER_DUMMY_EVIDENCE_2026-11-05.md)
- [T3 Smoke34](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_SMOKE34_AUTHENTIC_SPIRV_TRANSLATION_2026-11-09_AR.md)
- [T2 Foam Shader.Find typed return flow](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T2_ORIGINAL_FOAM_SHADERFIND_RESULT_FLOW_2026-11-06.md)
- [T1 FFT evidence](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md)
- [T5 APK89 feedback](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md)

**مهم:** كل رقم مقيّد بمصدره ومراحله؛ لا تستبدل تخميناً ميزة مشوهة بل اقبل `UNKNOWN` حين لا توجد هوية shader runtime الأصلية.
