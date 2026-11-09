# T3 — قنوات DXBC المستخدمة مقابل قنوات SPIR-V المعلنة للدخان الأصلي

**9 نوفمبر 2026 | العامل T3 | RENDER-002: OPEN / NOT_READY 0/3**

## السؤال الهندسي
[CI42691211652](https://github.com/alwansan/raf/actions/runs/42691211652) أثبت 7 مدخلات DXBC PS أصلية تتوافق دلاليًا مع 7 مخرجات VS، و28 قناة *معلنة*. لكن ذلك لم يثبت كم قناة يقرأ برنامج Fragment فعليًا. بينما [CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) أثبت أن أسماء SPIR-V التي يولّدها المترجم تختلف كليًا بين النسخة الأصلية والدائرية، وبالتالي لا تصلح لربط دلالة DXBC بموقع SPIR-V.

## الفحص الجديد
`scripts/t3_original_smoke34_ps_readmask_spirv.py` يعيد توثيق الهوية الأصلية الخاصة **Shader48 المرتبط بـ17 ParticleSystemRenderers/34 Material slots** بواسطة ZIP2 SHA ثابت `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، 6 مشاهد + 4 owners، ويتحقق من حالته المصدريّة RGB ColorMask وalpha-dependent blending وZWrite OFF. يقرأ `ISGN/ISG1.ReadWriteMask` لا `Mask` وحده لكل من زوجَي VS/FS ذوي keyword/player-bucket متطابق؛ يتحقق من المكونات المغطاة فعليًا من Vertex؛ ثم يحوّل فقط برنامجي DXBC Fragment إلى SPIR-V أصلي / HLSL / SPIR-V مشتق ويقرأ انعكاس الإدخال على runner خاص. يمنع تسريب البرامج الأصلية، أسماء Semantic، PathIDs، GUIDs والملفات الوسيطة.

[GitHub Actions 42692895633](https://github.com/alwansan/raf/actions/runs/42692895633): **SUCCESS**، 14/14 اختبار جديد +21/21 قديم DXBC +7/7 جرد مصدر Stage = **42/42**. Artifact JSON آمن [13708091567](https://github.com/alwansan/raf/actions/runs/42692895633/artifacts/13708091567)، تاريخ الانتهاء 16 نوفمبر 2026 20:26 UTC.

## النتائج الأصلية — مجموع زوجَي PS

| القياس | النتيجة |
|---|---:|
| عدد أزواج المصدر ذوي keyword مطابق | 2 |
| سجلات PS الأصلية ذات دلالات مستخدم | 7 |
| القنوات المعلنة في DXBC PS | **28** |
| القنوات المقروءة فعلًا حسب DXBC ReadWriteMask | **22** |
| القنوات المعلنة لكنها غير مقروءة | **6** |
| سجلات الدلالة ذات استخدام جزئي | 4 |
| سجلات الدلالة غير المقروءة كليًا | 0 |
| قنوات ReadMask غير المغطاة في VS الأصلي | 0 |
| قنوات إدخال Fragment المعلنة في SPIR-V الأصلي | **28** |
| قنوات إدخال Fragment المعلنة بعد HLSL roundtrip | **28** |
| عدد متغيرات PS المدخلة على كلا SPIR-V | 7 لكل منهما |
| عدد permutation التي تساوي فيها ReadMask مع SPIR-V المعلن | 0/2 |
| عدد permutation حيث أصلي SPIR-V = دائري SPIR-V في العدد | 2/2 |

**التفسير الضروري:** فرق 6 قنوات ناجم عن المقارنة بين فئتين مختلفتين من القياسات؛ DXBC `ReadWriteMask` يتتبع المكونات المستخدمة، بينما `spirv-cross --reflect` يحصي المتغيرات المعلنة وأحجامها. التطابق في *عدد* القنوات الـ28 بين المصدر والدائري لا يثبت أن المتغيرات تحتفظ بمعنى Semantic أو نفس `Location`، وكذلك 22 مقابل 28 لا يثبت تشوهات بصرية أو فقدان قيم حيّة.

## ما لم يتم إثباته
لم يتم بناء ShaderLab بديل أو استيراده إلى Unity. لم نثبت مراسلة `SemanticName+Index+Register+Component` في DXBC مع `Location+Component` المشتق، ولا interpolation أو دقة ألوان الدخان/Texture alpha، ولا هاتف Android/Adreno، ولا أن المربع المرصود على الهاتف سببه هذا الشيدر. **لا تغيير للعبة، APK، OBB أو ملفات العملاء الأخرى.**

**التجربة التالية:** البحث عن provenance صريح لربط source DXBC semantics مع SPIR-V Location وتعقب استعمالات المتغيرات، مع منع الاستنتاج من أسماء مترجم غير مستقرة أو متجهات متكررة vec4. بعد ذلك ShaderLab/Unity test وضبط pixels قبل إعلان إصلاح. لا تختبر هاتفًا جديدًا الآن.
