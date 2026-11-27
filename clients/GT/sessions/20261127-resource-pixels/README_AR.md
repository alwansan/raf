# GT G2 — تحقق metadata → compiler → Unity Vulkan → pixels

## GT — G2: نجاح مسار metadata إلى Unity/Vulkan بالبكسلات المؤلفة | 27 نوفمبر 2026

[Run45934006734 SUCCESS](https://github.com/alwansan/raf/actions/runs/45934006734) على الرأس المثبت `e867b31791ca00c58108ce2d3ea3933aee5234a2`، job140292902788. تحقق جديد فعلي: أُعيد فك ParameterBlob مؤلف واستخدام stage_parameter_records وrebind وتطبيع التسجيلات ودمج VS/FS؛ 14 glslang compile و14 spirv-val Vulkan1.1 و10 spirv-opt، أربع مقارنات قبل/بعد إعادة الربط. **ناتج combined.hlsl الفعلي (596B)**، نفسه من bare وspace0، غُلّف في ShaderLab بدون تغيير جسمه. SHA256 الشيدر 1087B: `bbac74071676cec0867db4d3dfab35c9107475f36e6de8babab129c0c093c473`. 18/18 اختبارات CI (10 موارد +3 depth +5 oracle). لا مصادر لعبة، فحوص CB/mesh/varying غير المتعلقة بالموارد بقيت ببدائل معلنة. تعديل resource_register_probe.py أضاف source_factory وcombined_out اختياريين، بقي المسار الافتراضي السابق.

Unity **2021.3.45f2 Linux/Vulkan Linear llvmpipe** استورد الشيدر الفعلي، وربط _MainTex مع sampler_MainTex عبر Material API مع _OldTex decoy. ثماني حالات 4×4، **128 بكسلاً و512 RGBA بأقصى خطأ0**. علامة R تعتمد على Vertex SampleLevel مستقلة، وG/B/A على Fragment Sample، مع straight-alpha فوق خلفية ثابتة. تحقق Point/Bilinear وClamp/Repeat وتبديل A/B ثم A دون بقايا من B، وwhite/decoy substitutes صريحة. ألفا صفر تحفظ الخلفية، والجزئية تمزجها، والكاملة تعرض المصدر. سبع مقارنات رقمية مع نتائج خاطئة (أصغر قيمة لأقصى فصل0.09375)، وليست سبع حقن عطل في المحرك. ليست تجربة فقدان texture أصلي أو قبول إصلاح النار أو المجسمات البيضاء في اللعبة.

[الأرشيف الفعلي الكامل](actual-run-45934006734.zip) (4911B، SHA256 `f4c4fdd5a55d9745017ada7fcf6a8a34ec41b02d79bed80df3a65bd2e4271624`)، [إعادة الحساب](artifact-review.json)، [أداة الإعادة](review_resource_pixels.py)، [جلسة التنفيذ](README_AR.md). طابقنا بصمة GitHub وCRC والأعضاء الستة، وأعدنا حساب جميع البكسلات من الإيصال الخام، وتطابق التقرير مع runner. 2514 سطر log فُحصت بأنماط C# errors وshader errors وTraceback فكانت العدادات0 (لا ادعاء شمول كل أخطاء/تحذيرات). فحص runner guard45934006683 ناجح، أوضاع الاختبار الأربعة الأخرى skipped عمداً. 26 ملفاً محلياً سابقاً بقيت مطابقة. لا Unity أو glslang محلياً، لا clone كامل؛ الاختبار التنفيذي كان Actions، والإعادة المحلية رقمية فقط.



## إعادة الإنتاج

من checkout مصدري مأذون نظيف، مع أدوات glslang وSPIRV-Tools، استخدم مجلدات إخراج جديدة:

```sh
python3 -B tools/synthetic_material_alpha/resource_pixels.py selftest
python3 -B tools/synthetic_material_alpha/resource_pixels.py stage --project /tmp/gt-resource-project --results /tmp/gt-resource-results --run-id local-authored
python3 -B clients/GT/sessions/20261127-resource-pixels/review_resource_pixels.py --archive clients/GT/sessions/20261127-resource-pixels/actual-run-45934006734.zip --sha256 f4c4fdd5a55d9745017ada7fcf6a8a34ec41b02d79bed80df3a65bd2e4271624 --run-id 45934006734-1-e867b31791ca00c58108ce2d3ea3933aee5234a2 --out /tmp/gt-resource-review.json
```

الثاني يولد المشروع فقط، والثالث يعيد الحساب من الأرشيف ولا يعيد تشغيل Unity. لتجربة رسم جديدة عند الحاجة استخدم وضع resource-pixels في workflow raft-gt-synthetic-material-alpha.yml، أو أمر Unity الموضح فيه، ثم verify مع نتائج ذلك التشغيل وهويته. لا تفترض أن PASS من fixture اختبار مزدوج يثبت التنفيذ؛ يلزم مطابقة تشغيل Actions الفعلي. جميع المدخلات والأرشيف مؤلفة. لا APK/OBB/XAPK. لا إضافة ثنائية خاصة أو أصول غير مصرح بها. [evidence.json](evidence.json) يحفظ التفاصيل والبصمات.

**عند Continue:** راجع الرأس وActions والبصمات. اكتملت بوابة G2 المؤلفة من metadata إلى البكسلات؛ **لا تكررها بلا سبب**. A3 الأصلي ما زال معلقاً على مصدر مأذون مثبت. انتقل إلى G4/FFT Utilities: اقرأ الحالة الأحدث لـHLSLcc/DXC والأدلة، اعزل خطأ gt_fs_main التاريخي Expected Coordinate to be float scalar or vector (44781701884) على HLSL/SPIR-V مؤلف، ميّز Sample/SampleLevel عن Load، واختبر بالمترجم الحقيقي وUnity ضمن التفويض. لا تحويل شامل للأنواع ولا ادعاء إصلاح الأصل إذا لم يُعد إنتاج الخطأ. إذا تعذر، وثق السبب واختر أقرب إصلاح مأذون من G4/G5. لا تخمّن kernel6. تابع A3/الدفعات العشر عند توفر مصدر مأذون، وكل G0–G6 قبل XAPK. الجرد التاريخي 688/786 Custom و98 Dummy/37GUID دون تغيير. لا قبول لعبة/Android، لا هاتف جزئي، الأنيميشن مؤجل. CL والمختبر للقراءة فقط، BLACK خارج العمل.

---



## سجل المرشح الأولي (تاريخي)

# GT G2 — مرشح اختبار Unity للربط المولّد من metadata

رأس البدء `26b081408e3c16388b33038885823cc6dcc3821f`. لا أصل مأذون جديد لـA3؛ لذلك ننفذ خطوة G2 التالية في الخطة. الاختبار السابق 45932314286 أثبت المترجم وليس Unity. أضفنا إمكانية اختيار مصنع HLSL مؤلف وحفظ combined.hlsl من نفس بوابة stage_parameter_records/rebind/strip/merge بعد النجاح فقط. المسار الافتراضي القديم بقي كما هو. جسم المرشح الجديد يقيس في R أخذ عينة Vertex مستقلة من _MainTex، وفي G/B/A عينة Fragment. اختلاف تَسجيلات VS (t21/s16) وFS (t9/s4) مؤلف، والـslot الأصلي المؤلف t3/s7؛ override يربطه بـ_MainTex، لا _OldTex. تُفحص صيغ bare وspace0 وتُرفض space1 والربط الناقص والبرنامج المختلف عبر بوابة المترجم الموجودة، ثم يُغلَّف جسم الناتج دون تعديل داخل ShaderLab.

مشهد Unity المؤلف 4×4، ثماني حالات: A/B وتبديل Point/Bilinear وClamp/Repeat، إعادة A، وwhite/decoy كضوابط صريحة. لا ادعاء أنها قيم اللعبة أو اختبار فقدان تكستشر فعلي؛ هي مواد مؤلفة. الهدف 128 بكسلاً و512 مركبة RGBA مع straight-alpha فوق خلفية ثابتة. الـEditor يسجل البكسلات، وPython يعيد حساب القيم ويطابق shader/combined/receipt hashes، ويرفض exit غير ناجح. نجحت محلياً 5/5 اختبارات Python للعقد ورفض 9 تحريفات، وsyntax للملفين. لم يترجم C# أو ينفذ Unity محلياً؛ 26 ملفاً محلياً سابقاً بقيت مطابقة للبصمات. لا clone كامل.

المرشح ينتظر اختبار glslang/SPIR-V الفعلي ثم Unity 2021.3.45f2 Linux/Vulkan. هذا commit يحمل [skip ci]؛ إطلاق التجربة من workflow المؤلف فقط، بعد مراجعة الفرق. لا أصول لعبة أو LFS أو APK أو XAPK. احفظ الفشل أو النجاح الفعلي، ثم تابع G4/G5 أو A3 عند توفر مدخل مأذون. لا تغيير في جرد 688/786 و98Dummy/37GUID.
