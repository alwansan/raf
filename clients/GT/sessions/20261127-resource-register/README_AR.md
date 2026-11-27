# GT G2 — دمج مسار تسجيلات الموارد والتحقق بالمترجم الحقيقي

## GT — دمج إصلاح G2 للموارد وتحقق فعلي من SPIR-V | 27 نوفمبر 2026

A1 وA2 تبقيان ناجحتين في نطاقهما المؤلف. راجعنا A3 وملفات ZIP2 وقرار المالك: وثائق النقل والبصمة لا تثبت وحدها حقوق استعمال الأصول الأصلية. **لم نجلب الأصل**، وA3 يبقى مشروطاً بمصدر مأذون. اتبعنا الخطة بالانتقال إلى إصلاح G2 فعلي في الكود المشترك، لا إعادة اختبار route0.

أضيف `scripts/gt_resource_register_contract.py` وربط بأربعة ملفات إنتاج: `w1_rebind_depth_resources.py` و`gt_original_921_resource_rebind.py` و`gt_original_921_all_variants.py` و`gt_original_921_shaderlab.py`. يدعم register العادي وspace0 ويحفظ مجموعات RESOURCE الأربع، ويرفض nonzero spaces والتكرارات الملتبسة. يمنع dict overwrite الصامت داخل كل metadata lane ويحتفظ بأولوية variant على common. تُحفظ أرقام التسجيل المترجمة عند إعادة الأسماء ثم تُزال في تطبيع Unity؛ لا تخمين من ترتيب descriptor. القارئ محدود بنصوص HLSL المترجمة، لا descriptor arrays أو UAV أو macro-expanded HLSL.

[Run45932314286 SUCCESS](https://github.com/alwansan/raf/actions/runs/45932314286) على الرأس `a02b194c82abab1344101f2efaabf5a600a3fb48`، job140287488334. 10/10 اختبارات جديدة +3/3 legacy depth، **14 ترجمة glslang فعلية و14 تحقق spirv-val Vulkan1.1 و10 spirv-opt** (تشمل حالة رفض برنامج مختلف). أربع مقارنات موجبة قبل/بعد إعادة أسماء Texture/Sampler متطابقة بعد strip-debug، وملف HLSL المدمج VS/FS للصيغتين مطابق بالبايت (501B) وبرنامجا المرحلتين متطابقان بالبصمات. فُك ParameterBlob مؤلف حجمه72B بالقارئ الفعلي واستُدعيت stage_parameter_records كاملة لمسار الموارد، مع بدائل اختبار معلنة لفحوص CB/mesh/varying خارج النطاق. رُفضت نسخة SPIR-V صحيحة لكنها تغير sampling، ورفض حالتا space1/missing sampler. **لا Unity أو بكسلات Android جديدة**.

[التشغيل الأول45932233741](https://github.com/alwansan/raf/actions/runs/45932233741) فشل عند جمع tool version في stdout (النسخة طبعت إلى stderr)، لا إيصال نهائي؛ حفظنا الفشل ولم نحسبه نجاحاً. أُصلح التسجيل فقط ثم نجح التشغيل الثاني. فحص توافق runner45932233934 نجح. لا أصل/أسرار/تنشيط Unity/حزمة؛ الاختبار CPU معزول. [الأرشيف الخام](actual-run-45932314286.zip) (2029B، SHA256 a7fe89aa4875ba343f2afb72642214d094f1cbcb34a3cae65dc979e0cd37a95f) و[إعادة الفحص](artifact-review.json) و[جلسة التنفيذ](README_AR.md). تحقق CRC والأعضاء الثلاثة وتطابق الإيصال، لم تُعد الترجمة محلياً. لا clone كامل؛ جرد 17 ملفاً من A2 والأرشيف الخامس المحلي بقي مطابقاً. لا اعتماد على sandbox.



## إعادة الإنتاج من checkout مصدري مأذون نظيف
```sh
python3 -B -m unittest discover -s tests -p test_gt_resource_register_contract.py -v
python3 -B -m unittest discover -s tests -p test_w1_depth_resource_rebinding.py -v
python3 -B tools/synthetic_material_alpha/resource_register_probe.py --out /tmp/gt-resource-compiler.json --run-id local-authored-probe
python3 -B clients/GT/sessions/20261127-resource-register/review_resource_artifact.py --archive clients/GT/sessions/20261127-resource-register/actual-run-45932314286.zip --sha256 a7fe89aa4875ba343f2afb72642214d094f1cbcb34a3cae65dc979e0cd37a95f --run-id 45932314286-1-a02b194c82abab1344101f2efaabf5a600a3fb48 --out /tmp/gt-resource-review.json
```
يلزم glslangValidator وspirv-val وspirv-opt للتجربة الثالثة؛ مسارات الإخراج جديدة. التجربة الرابعة تعيد التحقق من الأرشيف والاتساق والبصمات، لا ترجمة جديدة. وضع resource-bindings في workflow الاصطناعي يفحص المصدر المعزول فقط. احتفظنا بالـZIP الفعلي الذي يحتوي compiler.json وسجلَي الاختبارات؛ SPIR-V binaries مؤلفة قابلة لإعادة الإنشاء، بصماتها في الإيصال. لا ندعي التحقق الكامل من كل callers أو من مشهد اللعبة. قبل أي تفعيل على أصل مأذون، راجع دعم القارئ المحدود ونتائج حالات رفضه.

**عند Continue:** افحص HEAD وActions والبصمات. A3 لا يزال معلقاً حتى توفر مصدر أصلي مأذون مثبت؛ لا تخمّن نطاق الكلمات أو تستنتجه من العينة. إن لم يتوفر، أكمل G2 بتجربة Unity Vulkan فعلية تمرر shader مولداً من مسار metadata/rebind الجديد وتتحقق من اختيار Texture/Sampler باسم المادة وقراءة البكسلات، لا تكرر fixture ألفا القديم دون مسار الدمج الجديد. بعد ذلك انتقل إلى أقرب إصلاح من G4/FFT/Foam/Depth أو G5 المتاح، ثم استعادة المواد الأصلية والدفعات العشر عند توفر المصادر المأذونة. لا قبول للأبيض أو النار حتى اللعبة الفعلية، ولا تغيير في الجرد التاريخي 688/786 Custom و98 Dummy/37GUID. G0–G6 مفتوحة، الأنيميشن مؤجل، CL والمختبر للقراءة فقط، BLACK خارج العمل، لا XAPK ولا هاتف جزئي. خطة الحالة الآلية وذاكرة GT محدثتان.

---



## سجل المرشح الأولي (تاريخي)

# GT — دمج إصلاح تعداد وربط تسجيلات الموارد الافتراضية | 27 نوفمبر

رأس البدء `f4698e504ce6cebe1ea68dbbb586d51ff6ad2819`. A1 وA2 مكتملتان ضمن العينات المؤلفة فقط. فُحصت وثائق مصدر ZIP2 وتوجيه المالك؛ بصمات وأذونات الوصول لا تكفي وحدها لتأكيد حقوق بيانات اللعبة الأصلية. لم نجلب أي أصل، وبقي A3 مشروطاً بالمدخل المأذون. اخترنا عملاً منتجاً من G2: القارئ القديم في stage_parameter_records وrebind_resources وunity_resource_bindings كان يسقط explicit space0؛ كما كانت dict overwrites تخفي تكرار خانة metadata داخل lane واحد.

أضفنا قارئاً محدوداً لنصوص HLSL المترجمة، يقبل bare وspace0 ويحافظ على أربع مجموعات RESOURCE، يرفض nonzero/ambiguous slots وأسماء غير قابلة للربط. الممر depth rebind يستخدم القارئ نفسه. stage_parameter_records يحفظ أولوية variant على common بعد رفض تكرارات كل lane. إعادة الربط تبقي register annotations حتى بوابة SPIR-V، والتطبيع يزيلها للربط بأسماء Unity. لا ادعاء دعم descriptor arrays أو UAVs أو macro-expanded HLSL. 10/10 اختبارات العقد محلياً نجحت. الكود منشور كمرشح دمج ينتظر تجربة compiler حقيقية في CI مؤلف. لا قبول للعبة أو Unity. الملفات المختبرة الأساسية مطابقة Git blobs؛ clone كامل غير متاح. لا تغيير لمواد اللعبة أو GUID أو XAPK.

خطوة التنفيذ التالية: push مستقل يغيّر ملف workflow الاصطناعي فقط ليختبر هذا الرأس في مسار CPU-only؛ لا تشغيل workflow الأصلي عند تعديل scripts. الاختبار يجمع metadata مؤلفة وبايتات ParameterBlob فعلية للـdecoder وVS/FS عبر rebind_resources وglslang وSPIR-V val/opt، ويستدعي merger الفعلي. فحوص CB/mesh/varying غير المعنية ممثلة صراحةً ببدائل اختبار ولا يُدعى نجاحها. عند فشل compiler أو اختلاف البايتات لا نقبل المرشح. لا أسرار أو LFS أو بناء APK.
