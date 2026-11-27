# GT G4 — مقارنة الإحداثيات الفعلية وتشخيص جدول الكلمات

## GT — G4: نتيجة تشخيص FFT Utilities والبوابة الفعلية | 27 نوفمبر 2026

راجعنا [الفشل التاريخي44781701884](https://github.com/alwansan/raf/actions/runs/44781701884)، job136445781719، وتقرير الأنواع القديم (6 sample float و0 integer في الأصل/roundtrip) وإيصال HLSLcc المحلي الذي لا يثبت Unity. فحص أنماط سجل الفشل أعاد تشخيص Expected Coordinate to be float scalar or vector مرة واحدة في gt_fs_main، بلا رقم pass موثوق؛ لم نحتفظ بمحتوى خاص. لا جلب ZIP2 أو أصول اللعبة أو برامجها. أُنشئت 7 ممرات مؤلفة: 6 Sample/SampleLevel (float، swizzle، bitcast، signed/unsigned numeric conversion) وLoad واحد integer. استدعينا attach_programs وcompiler_control من كود الإنتاج عبر AST المحدود، وفرق المرشحين 7 pragma فقط. لم نغيّر تعبيرات الأصل أو gate الإنتاج.

[المقارنة45935871773](https://github.com/alwansan/raf/actions/runs/45935871773) على الرأس 5b6f8f21627269d946aa549cd7055384914cdf82: **failure في النتيجة الكلية**، لأن الفاحص strict zero_keywords رفض جدول الأسماء بعد نجاح مرحلتي Unity2021.3.45f2 Android Vulkan AssetBundle (DXC pragma / HLSLcc-default، job140298837257 و140299709457، 7Pass، 1 SVC، errors0، bundle حقيقي). لا ندعي attestation مستقل لمسار المترجم الداخلي من اسم الوضع. CPU: 14 glslang/val لكل وضع (28 إجمالاً)، الإيصال متطابق بالبايت. تبديل operand لنوع إحداثيات خاطئ عمداً أعاد رسالة Sample التاريخية ورفض Fetch float؛ أربع عمليات رفض إجمالاً. **لم يعاود Unity نفسه إنتاج خطأ الإحداثيات في العينتين**. لا تحويل شامل، لا إصلاح مؤكد للسبب الأصلي. [الإيصالات الخام](cpu.json)، [DXC](dxc-unity.json)، [HLSLcc](hlslcc-unity.json)، [مراجعة الأرشيفين](artifact-review.json). بصمات ZIP والأعضاء وCRC متحققة محلياً؛ جسم الشيدر مطابق بعد إزالة pragma.

[Replay45936590347 SUCCESS](https://github.com/alwansan/raf/actions/runs/45936590347)، job140301098539، على الرأس `e79e09151def7abe680b03dc230cdff9ff41b27e`، CPU-only، قرأ فقط الأرشيفين المؤلفين artifact15171100631 و15170637402 ببصمتيهما. لا Unity جديد. UnityPy1.23.0 وSMOL-V وspirv-val Vulkan1.1 وspirv-dis فكوا **14 module فريداً لكل حزمة (28 مجموع العدّين)** و7Pass VS/FS في كل وضع؛ 21 fragment reference لكل وضع، صفر invalid module وصفر wrong image family. كل الممرات في الوضعين لها empty route pair، ولا أي keyword indices مستخدمة في أي lane. في جدول الأسماء المتسلسل توجد 4 أسماء Stereo: STEREO_INSTANCING_ON، UNITY_SINGLE_PASS_STEREO، STEREO_MULTIVIEW_ON، STEREO_CUBEMAP_RENDER_ON؛ flags=[0,0,0,0]، used=[]، جميع route_keys=[[]]. لذلك شرط جدول الأسماء الفارغ الحالي يرفض هاتين الحزمتين رغم صلاحية البرامج وعدم استعمال أي اسم. لا تعميم لهذا إلى الأصل أو السماح لأي اسم غير معروف/مستخدم؛ البوابة الأصلية بقيت دون تغيير. هذا كشف خلل محدد في شرط قبول الحزم المؤلفة، **ليس إصلاح FFT الأصلي**.

[أرشيف التشخيص الكامل المحفوظ](actual-replay-45936590347.zip) حجمه3561B SHA256 `5bd5ce19f2cf64bc16ee09cd2b8f2434c7b92c1317f54de076eef3db6a93f95e`، العضو diagnostic.json (63206B) SHA256 `9eafaf0a84a04a85183b0b4a53396be2fd7ffa8fa4f7d95894f5c0bfb92b9a21`. تحقق CRC وبصمات الحزمتين ومطابقة كل صف/موديول محلياً، لم نعد فك الحزمة أو ترجمتها محلياً. أرشيفا الحزمتين الخام موجودان في Actions إلى 11 ديسمبر، الإيصالات والبصمات وأدوات التوليد والفحص والأرشيف التشخيصي مثبتة في Git لاستعادة النتائج وإعادة بناء العينة بعد انتهاء المرفقات. حارس runner45935871899 و45936590335 ناجحان. 131 ملفاً محلياً سابقاً بقيت مطابقة؛ لا clone كامل.



## إعادة الإنتاج
- في checkout نظيف مأذون للرأس الحالي: `python3 -B tools/synthetic_material_alpha/fft_coordinate_probe.py selftest`. وضع fft-coordinate في workflow raft-gt-synthetic-material-alpha.yml يولد عينتين من المصدر المؤلف، ثم يبني حزمة Android Vulkan فقط لكل mode. لا أصل أو player build.
- من Actions45935871773 حمّل artifact15171100631 و15170637402 (أسماء وبصمات في artifact-review.json). أعد فحصهما بالأداة review_coordinate_artifacts.py، مع run-id-prefix `45935871773-1-5b6f8f21627269d946aa549cd7055384914cdf82` وjob-success 0 لكليهما؛ هذه الأداة تفحص الأرشيفات ولا تعيد المترجم. وضع fft-coordinate-replay الحالي مربوط بهذين الأرشيفين وهوياتهما (لا يعمل بعد expiry إلا إذا أُعيد توليد المدخلات، أو استُعيدت نسخة مسموحة مطابقة). أعد التشغيل بمسارات جديدة وهويات جديدة إذا انتهت صلاحية المرفقات؛ لا تنسب النتيجة الجديدة إلى التشغيل القديم.
- فك [أرشيف التشخيص](actual-replay-45936590347.zip) وتحقق من بصمة العضو diagnostic.json؛ كل module له SHA/model/op/validator_exit، وكل pass له تفاصيل row/keywords ومراجع SHA. هذا الأرشيف محفوظ في Git وليس اعتماداً على sandbox. [evidence.json](evidence.json) يحفظ البصمات وهويات المرفقات والحدود.

**عند Continue:** البند النشط G4-FFT-bundle-gate. قوِّ البوابة بشكل محدود ومغلق عند الغموض: افصل أسماء Stereo الأربعة المعروفة غير المستخدمة عن المسارات الفعلية ذات indices فارغة، مع إثبات مصدر مأذون/طوبولوجيا، وإثبات أسماء/flags، والتحقق الفعلي لكل SPIR-V مفكوك والتزام SHA/bytes للإيصال والحزمة. اختبر على الحزمتين الموجودتين وضوابط unknown/active keyword، missing stage، نفس الحجم مع بايت مختلف، wrong coordinate. لا تُخفف البوابة الأصلية أو تغيرها بلا الأدلة والضوابط، ولا تعتبر التشخيص إصلاحاً للخطأ التاريخي. بعد ذلك انتقل إلى أقرب إصلاح G4/G5 أو A3 عند مصدر مأذون؛ لا تعيد Unity المؤلف نفسه بلا سبب. جرد 688/786 Custom و98 Dummy/37GUID تاريخي دون تغيير. G0–G6 مفتوحة، لا بكسلات لعبة/Android، لا XAPK ولا هاتف جزئي، الأنيميشن مؤجل، CL والمختبر للقراءة فقط، BLACK خارج النطاق.

---



## سجل المرشح الأولي (تاريخي)

# GT G4 — تشخيص نوع إحداثيات FFT Utilities (عينات مؤلفة فقط)

رأس البدء 38458644d1399d008cee87c9def05a67d6768f76. الأدلة التاريخية: 44781701884 / Unity2021.3.45f2 DXC أخفق في gt_fs_main، Expected Coordinate to be float scalar or vector؛ تقرير gt-fft-coordinate-types-safe.json السابق يحصي 6 إحداثيات Sample float في الأصل وroundtrip، و0 integer. إيصال HLSLcc المحلي السابق ترجمة مصدر فقط وليس Unity. لا اقتناء ZIP2 أو برامج/خامات أصلية؛ لا تغيير للأصل أو GUID. لا تحويل نوع شامل.

أداة fft_coordinate_probe.py تختار 7 برامج HLSL مؤلفة من الصفر، 6 Sample/SampleLevel (float2، float4 swizzle، bitcast غير تافه، signed/unsigned numeric conversions) وLoad واحد بإحداثيات int3. تستخدم attach_programs وcompiler_control الفعليين من gt_fft_utilities_restore.py عبر AST المحدود. الفرق بين مرشحي DXC/HLSLcc إزالة سبع pragma فقط. 3/3 اختبارات محلية لأداة الاختبار، والبصمة SHA256 72a29611d92211dc31a206daf10efbe4f535b78ef890ec0fbe4e9942356d3870. 131 ملفاً محلياً سابقاً جُردت بصماتها قبل العمل. لا مترجم أو Unity أو clone كامل محلياً.

هدف التنفيذ: compile/validate لكل VS/FS مؤلف، تبديل نوع operand عمداً في Sample وFetch للتحقق من رسالتي رفض spirv-val؛ ثم تشغيل مصفوفة مؤلفة Android Vulkan AssetBundle فقط (DXC/HLSLcc، كل منهما مستقل) باستخدام محرر FFTUtilitiesShaderValidation.cs المنشور دون تغييره. فك الحزمة الفعلية عبر UnityPy وSMOL-V، تحقق من 7 مسارات لكل مرحلة وspirv-val للموديولات المشار إليها من Fragment، وتصنيف OpImageSample/OpImageFetch. لا تعتبر الاسم أو pragma وحدهما إثباتاً لمسار compiler داخلي. لا قبول إلا بعد الإيصال ونتيجة التشغيل. هذا مرشح ينتظر CI. لا APK أو هاتف أو XAPK. A3 معلق، G0–G6 مفتوحة.

إذا نجحت الطريقتان، فهذا عدم إعادة إنتاج في العينة المحدودة لا إصلاح الأصل. إذا اختلفتا، احفظ الدليل وحدد نطاق السبب دون افتراض تكافؤ برامج اللعبة. إذا تعذر، سجل العائق وانتقل إلى أقرب عمل منتج في G4/G5.
