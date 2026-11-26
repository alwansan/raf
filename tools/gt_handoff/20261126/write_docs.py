from pathlib import Path
import json
repo=Path('/home/a/Documents/Codex/2026-11-13/new-chat/work/raf')
b=repo/'clients/GT/sessions/20261126-complete-handoff'
def put(name,text):p=b/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
put('README_AR.md','''
# تسليم GT الكامل — 26 نوفمبر 2026

هذه حزمة حفظ واستئناف، وليست إعلان اكتمال رسوميات اللعبة. طلب المالك الآن نشر جميع أدوات العمل والاختبارات والأدلة والخطط المهمة، بعد مراجعة المستودع، ليكمل في جلسة جديدة. هذا الطلب يجيز نشر الملفات الآمنة المذكورة هنا ويتجاوز حدود «تحديث RESTORE وحده» الواردة في السجل التاريخي؛ لا يعني استئناف التنفيذ الثقيل أو إنشاء XAPK في جلسة الحفظ. هدف الاستعادة كان موقوفاً مؤقتاً، وبقي كذلك.

## نقطة الدخول

انسخ [رسالة الاستعادة الحالية](../../RESTORE_AR.md) إلى الجلسة الجديدة. ابدأ بعدها بهذا الدليل، ثم [الخطة](PLAN_AND_GOALS_AR.md)، [النتائج والقيود](FINDINGS_AND_LIMITS_AR.md)، [الأدوات وإعادة التجهيز](TOOLS_AND_REPRODUCTION_AR.md)، [الاختبارات](TESTS_AND_RESULTS_AR.md)، [المراجع](REFERENCES_AR.md)، [النواقص المحلية](inventory/KNOWN_MISSING_LOCAL_ARTIFACTS.json)، وأخيراً [فهرس الملفات والبصمات](MANIFEST.json).

## ما حُفظ

- أدوات وC# probes وworkflows واختبارات FFT وNEXT23b التي كانت محلية، في مساراتها الطبيعية تحت scripts وtests وandroid-port و.github/workflows. المسودات غير المنفذة موسومة كذلك؛ رفعها ليس تفعيلها.
- إيصالات Actions رقمية أصلية من التشغيلات 44783011957 و44781701884 و45760877767 و45760345978 و45759923748. حُفظت ملفات JSON وبصمات ملفات ZIP المطابقة لبصمات GitHub؛ لا نعتمد على بقاء artifact مؤقت.
- أربع إيصالات FFT محلية، بما فيها فشل DXC/التحكم HLSLcc وفحص أنواع الإحداثيات؛ بصمة المرشح المولّد التزام تحقق، وليست نشر bytes الشيدر الأصلي.
- نتائج 740 ملف اختبار تاريخياً، و27 مقارنة على نسخة الأساس، والسجلات المتاحة كاملة داخل أرشيف zip مفهرس. هذه نتائج تاريخية لا اختبار جديد للرأس الحالي.
- نتائج الفحص المركّز الجديد يوم التسليم، وأمره ونطاقه. لا Unity أو Vulkan رسم أو أصل لعبة شُغّل لأجل هذا التسليم.
- نسخ مستقلة من RESTORE المنشور قبل التسليم، وRESTORE المحلي المتوقف، والملف المستورد من Downloads إن كان متاحاً. لم تُحذف توجيهات أو نتائج تاريخية؛ تغيرت نقطة الدخول فقط.
- أداتي التأليف التاريخيتين ومراجع أدوات الطرف الثالث وإصداراتها وبصماتها ووصفات تجهيزها، بدلاً من الاعتماد على مجلدات SDK محلية مجهولة.

## حدود الاكتمال

النسخ المتاحة من الأدوات والأدلة حُفظت. توجد ملفات ذكرتها الدفعات الاصطناعية 3–5 ولم توجد في الملفات المتاحة لهذه الجلسة؛ أسماؤها وبصماتها والبحث عنها محفوظة صراحة. لا يمكن استنتاج bytes مفقودة من SHA، ولا ندعي رفع أرشيف لم نحصل عليه. يجب إحضاره والتحقق منه أو إعادة التجربة بنواتج جديدة مع فصلها عن الدليل التاريخي.

لا تحتوي الحزمة على مفاتيح أو تفعيل Unity، ولا على ملفات اللعبة أو shader HLSL/DXBC/SPIR-V الخاصة المستخرجة، ولا نسخ Unity export أو ملفات نظام/بيئات Python أو cache. هذه نواتج يعاد توليدها من المصدر المصرح والمثبت بأدوات المستودع. بيانات CL الأصلية تبقى في مستودع CL مع مراجع مثبتة، والمحفوظ هنا تحليلها الرقمي فقط.

## حالة النشر

أساس المراجعة المنشور هو f3c8a2cdacf04fdbfbced5f87a1407da223e3a15. حُفظ العمل المحلي بعد دمج fast-forward لهذا الرأس؛ ملف RESTORE كان نقطة التداخل الوحيدة وحُفظت نسختاه. يستخدم commit التسليم `[skip ci]` لمنع تشغيل workflows ثقيلة بمجرد الحفظ. التخطي ليس نجاح CI. اقرأ رأس commit الحامل للحزمة بدلاً من تخمين SHA ذاتي داخل الملف.
''')
put('PLAN_AND_GOALS_AR.md','''
# الهدف الكامل وخطة الاستئناف

## الهدف الذي لم يتغير

استعادة ودمج المجسمات والخامات والألوان والتكستشرات والصور والـmips والشيدرات وخصائص المواد وkeywords وpasses/samplers/CB، والماء وFoam وDepth وFFT والنار والجسيمات والظلال وPostFX والموارد البصرية المرافقة. إعطاء الأولوية للمجسمات البيضاء والمربعات السوداء في النار. الأنيميشن والحركات مؤجلة بتوجيه المالك الأحدث. لا تختصر النجاح في إزالة Dummy أو نجاح مترجم.

استعد كل دفعة أصيلة ثم ادمجها مع أدلتها، واحفظ المصدر والـGUID و.meta وMaterial/YAML والمراجع. بعد اكتمال الاستعادة والدمج يأتي XAPK التوافق الشامل؛ إذا أُطلق بناء طويل فلا تنتظره بدلاً من المالك، ولا تطلق نسخة مكررة. لا تطلب تجربة هاتف جديدة لتجنب استكمال الاستعادة.

## ترتيب عملي للجلسة التالية

1. تحقق من رأس feature/android-native-port وحالة Actions الحالية، ومن MANIFEST والملفات المحلية المحفوظة. اقرأ KNOWN_MISSING_LOCAL_ARTIFACTS؛ لا تفترض وجود برامج الدفعات 3–5 لمجرد أن تاريخها مكتوب.
2. أغلق فجوة اختيار keywords وقت التشغيل في الدفعات العشر المسجلة في ten-group-runtime-keyword-audit.json. المصدر يركبها حالياً بـengine_keywords=False، فينشئ GT selector خاصاً بالترجمة؛ في غيابه يختار route0. يلزم إنتاج candidate بكلمات المصدر الأصلية، وإثبات runtime scope/pass type وUnity وبنية حزمة Vulkan قبل اعتماده إنتاجياً. NEXT23b draft لا يصلح بقية الدفعات تلقائياً.
3. راجع NEXT23b Unity draft قبل تشغيله: مصدر 4Pass/1156route/134برنامج مكتمل التركيب الخاص؛ أصلح حدود gate المذكورة في FINDINGS، ثم أثبت كل engine routes وSHA المرشح ومرحلتي VS/FS في الحزمة. بعد نجاح حقيقي فقط نفذ SAME-EXPORT original GUID وربط المواد والجرد؛ لا تستبق زيادة العدد إلى 711 أو خفض98.
4. راجع تحكم HLSLcc لشيدر FFT Utilities: المصدر12 برنامجاً و7Pass و14entrypoint اجتاز محلياً، لكن Unity DXC فشل. جرب compiler-control المحدد مع بقاء جسم HLSL مطابقاً، لا casts أو قيم مصطنعة، ثم حلل الحزمة المستقلة. المثبت الجديد جاهز للاختبار العقدي فقط؛ لا يُشغل دون الإيصالات الثلاثة الحقيقية.
5. تابع NEXT6: ما زال إثبات lane semantics لقراءة padding مصفوفة الأصل غير مكتمل. لا تبدل الخانات المجهولة أصفاراً ولا تخفض spirv-val أو Vulkan1.1 ولا تحذف الأصل لتجاوز overlap.
6. راجع إصلاحات تعداد/ربط الموارد الاصطناعية space0. المصدر المنشور RESOURCE لا يلتقط الصيغة الصريحة، وبعض التصحيحات المذكورة غير موجودة هنا. يجب فصل اختبار عقد مستنسخ عن تشغيل stage_parameter_records الفعلي، وربط الناتج بقياسات بكسلات جديدة.
7. تابع 98 Dummy/37GUID وجرد الموديلات/التكستشرات/المصفوفات/الألوان، ثم Spectrum7/Foam2/FFT Utilities7/Depth/compute وCB/samplers/RT، النار وalpha وPostFX والواجهات. لكل نقص دليل مصدر ثم تصدير ثم Unity ثم دمج؛ لا ترقي نتيجة اصطناعية إلى قبول لعبة.
8. قبل XAPK راجع G0–G6 في OWNER_DIRECTIVE_RESTORE_FIRST_AR.md مع تحديثاتها الأحدث في RESTORE. لا تعلن اكتمال أي بند لا يملك الدليل الموافق لنطاقه. بعد ذلك فقط اختبارات الهاتف والتوافق وإصلاحاتها.

## البوابات المرجعية

G0 جرد مورد بمورد؛ G1 المشاهد والمجسمات والمراجع؛ G2 تكستشرات ومصفوفات ومِيب وProperties/TexEnv/Keywords؛ G3 البرامج والشيدرات والجرد بعد الدمج؛ G4 الماء/FFT/Depth والربط؛ G5 النار والظلال والجسيمات والمؤثرات؛ G6 سلامة المصدر والتصدير والمراجع وفحوص Unity وعدم وجود نقص معلوم غير معالج. أرقام770/333/246/98 snapshots لمراحل مختلفة، فلا تخلطها.

سجل الخطة القديم محفوظ في RESTORATION_PLAN.json وRESTORATION_PLAN_AR.md وsessions/20261115-graphics-restoration. تضاف إليه لقطة التسليم ولا يمحى لتسوية الأرقام تاريخياً. النتيجة الحالية NOT_COMPLETE؛ لا هدف استعادة مكتمل ولا XAPK جديد ضمن عملية الحفظ.
''')
put('FINDINGS_AND_LIMITS_AR.md','''
# النتائج والاكتشافات وحدودها

| المجال | الدليل المتاح | ما لا يثبته |
|---|---|---|
| جرد المواد | آخر SAME-EXPORT مقبول43929698985:688/786 Custom non-Dummy،98Dummy/37GUID،29213 التزام Material/YAML/meta | ليست نسبة اكتمال اللعبة أو قبول بكسلات أو runtime keywords |
| دمج مسار Native | 6c071a414 أضاف10دفعات مع ترتيب post9/post13/post23 و82owner أصلية جديدة وSHA ديناميكية لملفات Native | Native المعدل لم ينفذ هنا، وفجوة GT selectors في مرشحات الدفعات ما زالت قائمة |
| NEXT23b |44783011957/artifact14654640691:134/134 ترجمة و2312routed stages و2312entrypoints و20085CB offsets و7516varyings،19خاصية و4Pass | مصدر ShaderLab خاص، ليس قبول Unity/engine keywords/GUID/هاتف |
| FFT Utilities | الأصل7Pass،7VSFS،12برنامج،خاصيتان؛12roundtrips و14entrypoints محلياً | Unity DXC44781701884 فشل؛ HLSLcc ليس مقبولاً داخلUnity بعد |
| تحكم FFT | SHA DXC f8575ebd855cff193c9fdb506b5f2b2d427d4c583eb9c5c7af0d6ff39c948b23؛ HLSLcc4d6e4815130daca16fdec13b4572f19c24c978e99787ba6f57658e4578759a69 | فقط إزالة7pragmas use_dxc؛ لا تعديل عيّنات أو casts ولا دمج لعبة |
| Coordinate FFT |6إحداثيات float4 في SPIR-V الأصلي المترجم،6float2 في roundtrip،صفرinteger في كليهما | لا تبرير لتحويل int تخميني لحل خطأ DXC |
| النار | pointer أصلي SAME-EXPORT وTexture2D غير exportable يمكن تصنيفه دون اختلاق GUID | لا صورة ثالثة مصدرة مثبتة ولا مقارنة alpha GPU؛ ارتباطParticle108 بالنار الظاهرة نفسه غير مثبت بالكامل |
| الجهاز20نوفمبر | CL pinned8db59a4،968pass roots:484Foam و484FFT Utilities؛0kernel roots؛ScudoOOM أثناءAdreno Vulkan renderpass | انعدام kernel errors في جلسة واحدة ليس إثبات compute كامل؛ سبب التخصيص أو ربطOOM بخطأpasses غير مثبت |
| تجربة Unity الاصطناعية |45760877767 نجاح120بكسلاً/5حالات،llvmpipeLLVM15،maxerror0،ضوابط texture/tint/alpha | لا game pixels ولاAndroid ولا قبول مواد اللعبة |
| دفعات3/4/5 | تاريخياً240بكسلاً لكل دفعة3/4،و15اختبار تعداد للدفعة5 بحسب RESTORE المنشور | أرشيفاتها الأصلية غير متاحة هنا؛ لا إعادة تحقق جديدة ولا ادعاء نشرها |

## فجوة keywords الإنتاجية

الملف evidence/ten-group-runtime-keyword-audit.json يوثق كل مجموعة وسطر compose. الدالة compose تبني عند engine_keywords=False سلسلة multi_compile بأسماء GT_ORIGINAL_921_Pn_Vn. اختيار تلك الأسماء يولّد جميع برامج الترجمة، لكنه لا يربطها بالأسماء التي تضبطها اللعبة. غياب token الخاص يختار default route0. generic model installer مع counts_override يقبل engine_keywords_verified=False؛ وبقية مثبتي NEXT لا يشترطون دليلاً إيجابياً للكلمات الأصلية. لذلك لا يصح تحويل جرد non-Dummy إلى ادعاء مطابقة تشغيلية.

## مسودات منشورة للحفظ لا للاعتماد

NEXT23b workflow/C# probe و--next23b verifier يحاولون تسجيل engine routes الأصلية، ومقارنة SHA ومرحلتي Vulkan، ورفض GT-selector fallback. لم ينفذ هذا المسار حتى التسليم. يلزم مراجعة environment UNITY_LICENSE ومتاحية الأسرار قبل التشغيل؛ خلاف workflow FFT، مسودة NEXT23b الحالية لا تضبط job environment. فحص bundle الحالي يطابق الكلمات بتقاطع universe manifest ولا يرفض كل كلمة إضافية محتملة؛ كما يأتي ربط passType بالأصل من مسار composer، وليس إثبات مصدر مستقل من verifier. هذه حدود مراجعة يجب حسمها قبل اعتماد runtime parity.

FFT installer الجديد يتحقق من SHA owners وowner/PathID وtrace class48 وGUID وmeta وإيصالات source/Unity/bundle وربط المرشح، مع backup خارجي وcommitments لكل ملفات المشروع وrollback. اجتياز اختباره الاصطناعي لا يعني أنه ركب على تصدير حقيقي؛ لا استدعاء له في workflow الإنتاجية الآن.

## اختبارات قديمة لا تُسوّى إلى أخضر

فحص740 ملفاً منعزلاً تاريخياً أعطى712pass و28fail. واحد من الإخفاقات كان fixture تاريخية تقارن مجموعة شروط قديمة بـFFT الجديد، وصُحح؛27باقية أُعيد إنتاجها على الأساس f5115a4. السجلات وأسماء الفشل في tests/historical-results.json وhistorical-baseline-results.json. بعض الإخفاقات نقص modules/cryptography أو تعارض import وبعضها assertions قديمة؛ لا يعني ذلك أن suite كاملة خضراء. فشل discovery العام بسبب اسم اختبار مكرر بين scripts وtests محفوظ أيضاً.
''')
put('TOOLS_AND_REPRODUCTION_AR.md','''
# الأدوات والتجهيز وإعادة التشغيل

## الأدوات داخل المستودع

| الوظيفة | المسارات |
|---|---|
| مصدر NEXT23b وتركيبه | scripts/gt_next23b_private_stage_translation.py،gt_next23b_source_topology_census.py |
| route/layout/property/CB | gt_original_921_all_variants.py،gt_original_921_keyword_routes.py،gt_original_921_shaderlab.py،gt_original_921_cb_hlsl.py،t3_particle108_source_propstate.py |
| Vulkan bundle | gt_verify_921_shader_bundle.py،gt_decode_smolv.cpp |
| مصدر وتحكم FFT Utilities | gt_fft_utilities_restore.py؛ CLI --compiler-control dxc أوhlslcc؛ defaultDXC محفوظ |
| تثبيت FFT | gt_install_fft_utilities_original.py؛ يتطلب source-receipt وunity-receipt وbundle-receipt مستقلة،original وproject وtrace وcandidate وbackup وout |
| C# المعزول | android-port/Experiments/GT/Editor/FFTUtilitiesShaderValidation.cs وNext23bShaderValidation.cs |
| مصدر ZIP2 | gt_stage_serialized_owners.py،gt_zip2_export_resources.py،w1_stage_zip2_owners.py |
| مصفوفات/لون/alpha | gt_repair_array_flipbook_importers.py،b44_verify_material_colors.py،gt_particle108_export_alpha_diagnostic.py |
| تجارب مؤلفة اصطناعياً | gt_synthetic_material_alpha.py وtools/synthetic_material_alpha/ |
| أدوات التأليف التاريخية | tools/gt_handoff/20261126/run-tests-isolated.py وport_post23_native.py؛ ليستا أوامر تطبق عميانياً |

المسارات غير المسبوقة في الجدول تحت scripts/. ملفات الاختبار المطابقة تحت tests/. workflows تحت .github/workflows/raft-gt-fft-utilities-source.yml وraft-gt-next23b-original-shader-unity.yml وraft-gt-next23b-private-stage-translation.yml وraft-gt-synthetic-material-alpha.yml. Native فيraft-unity-editor-android-import.yml؛ لا تعدّل request JSON لأجل الاستعادة أو الحفظ.

## بيئة قابلة لإعادة التجهيز

Python المستعمل محلياً3.12.3،PyYAML6.0.3،Pillow13.0.0،Unity2021.3.45f2. بقية freeze التاريخي وبصمات حزم arm64 والأرشيف الرسميUnityPy1.23.0 فيtoolchain/. هذه إصدارات تاريخية، لا ادعاء أن apt اليوم يعيد البايتات نفسها.

للفحوص المصدرية الاصطناعية:

```bash
python3 -m venv work/gt-handoff-venv
work/gt-handoff-venv/bin/python -m pip install -r clients/GT/sessions/20261126-complete-handoff/toolchain/source-free-requirements.txt
PYTHONPATH=tests work/gt-handoff-venv/bin/python -B -m unittest test_gt_next23b_unity_gate test_gt_next23b_private_stage_translation test_gt_original_next23b_source_pass_modes test_gt_next23b_source_property_flags test_gt_fft_utilities_restore test_gt_fft_utilities_unity_contract test_gt_fft_utilities_bundle test_gt_install_fft_utilities_original test_gt_original_921_bundle -v
```

لإعادة الفحص الواسع، شغّل كل test_*.py في subprocess مستقل كما فعل runner التاريخي، مع repo/output/python محدثة. لا تجمع discovery كله وتفترض أن خطأ الاسم المكرر دليل تغيير إنتاجي جديد. قد تحتاج اعتمادات إضافية؛ freeze محفوظ وليس وعداً باجتياز740اختباراً في بيئة نظيفة.

داخل Ubuntu24.04 تستعمل workflows vkd3d-compiler وspirv-tools وspirv-cross وglslang-tools؛ فحوص spirv-val تستهدفvulkan1.1. source مؤقت فقط بعد التحققSHA. مصدرsmol-v مثبت عند6303e979b59153ee7007fd14e06d3fed8687b64c؛ راجع curl والمسارات في workflows، ولا تغيره بصمت.

محلياً استُخرجت debs arm64 إلىwork/debs/root، واستُعمل PATH نحوusr/bin وLD_LIBRARY_PATH نحوusr/lib/aarch64-linux-gnu. فشل pip install UnityPy بسببغيابaarch64-linux-gnu-gcc؛ لم يكن ذلك فشل فك المصدر. الحل المستعمل: الاعتمادات فيvenv وPYTHONPATH إلى شجرة مصدرUnityPy1.23.0 المطابقة للأرشيف الرسمي؛ sha256396e2bf8dea49b2bfd6309f5c790b2a5838613be037094bb55e6076c4852a890. مصدر التنزيل وبصمات جميعdebs فيversions-and-checksums.json. لا تنسخ binaries لعمارة مختلفة ولا تتجاهل التحقق.

## إعادة توليد النواتج الخاصة

المرشحات HLSL/ShaderLab وDXBC وSPIR-V والأصول المصدرة لا تُنشر هنا. لكل مرشح وصفة مصدر فيscript/workflow، وإيصال آمن وبصمة مرشح حين كانت متاحة. أعد توليده فيscratch منفصل من ZIP2 المصرح والمثبت15964ea8 فقط، دونGitLFS ودونتعديلالأصل، ثم افحصSHA والحزمة الفعلية. الوصول إلىlicense/keys يتم بالإعدادات الموجودة خارجGit؛ لا تحفظها في الحزمة.

الـworkflows الجديدة يمكن أن تعمل علىpush للمسارات المحددة. commit التسليم يحمل[skip ci] ولا يعد نجاحCI. قبل إعادة تفعيلها في جلسة تنفيذ راجعإذنالمالكالحالي والأسرار والـconcurrency وحالةأيjobقائم؛ لا تعيد تشغيلشل سابق لمجردتأخرالملاحظة.
''')
put('TESTS_AND_RESULTS_AR.md','''
# الاختبارات والعمليات المحفوظة

## نتائج تاريخية أصلية

- tests/historical-results.json: كل740 ملف اختبار معexitcode والمدة؛712نجح و28فشل آنذاك.
- tests/historical-baseline-results.json:27ملفاً فاشلاً أعيدت علىbaselinef5115a4؛جميعهافشلتعلىذلكالأساسأيضاً.
- tests/historical-test-logs.zip: السجلات المتاحة كاملة،بمافيها baseline وRED/GREEN وdiscovery وpipfailure. أسماءmembers وSHA256 لكلواحد فيhistorical-test-logs-manifest.json. الأرشيفلايدعيأنكلمافيهتشغيلجديد؛التاريخوالنطاقمحفوظان.
- ضبطpassعددFFT: fft-seven-red.log يثبت2مقابل7قبلالإصلاح. لا يعني ذلكإصلاحعرضالماء؛الفاحصالآنيلزم7أصلية.
- فحصFoamوثّقمسارRaft_Dataالمكررواختباراتالمسار؛إصلاحهاواختباراتهابالمستودع.
- الإيصالاتالمحليةFFTتحفظ12/12و14entrypointsوSHAالمرشحومقارنةنوعالإحداثيات؛هذهليستUnity.

## فحص التسليم الحالي

الملفcurrent-focused-tests.txt هو الخرج الفعلي،وcurrent-focused-test-command.json يثبتالأمروالبيئةوالأساسوالـexitcode. يتناولعقودالمسوداتوالبواباتوالتجربةالاصطناعيةوبعضالانحدارات؛لايشغلUnityولايعيداستخراجأصللعبةولايقيسهاتفاً. النتيجةالنهائيةتقرأمنالسجلالفعلي،ولايفترضعددمنرسالةمحادثة.

## إيصالات CI الدائمة

كلevidence/actions/<run>/artifact-provenance.json يسجلartifactID وZIPSHA وmembersSHA. راجعREADMEوالملفاتالأصليةداخلنفسالمجلد. قيمmockالواردةفياختباراتPythonلايُحتفظبهاكإيصالاتتنفيذ؛الـraw.unity.jsonالمحفوظمن45760877767قراءاتتجربةمؤلفةاصطناعياًفقط.

## المراجعات

مراجعتانمستقلتانللحفظجردتاالتعديلاتوالأدلةوراجعتانطاقفحوصNEXT23b/FFT والمثبت.أكدتاأنملفRESTOREهوالتداخلالوحيدمعرأسGitHubالأحدثوأنworkflowpushقديشغلUnity؛استخدم[skip ci].الملاحظاتالمفتوحةلـkeyword universe وpassType وenvironmentفيFINDINGS_AND_LIMITS_AR.md. المراجعةليستUnityrunولاقبولاًللعبة.
''')
put('REFERENCES_AR.md','''
# المراجع الثابتة والأهداف السابقة

## مداخل المشروع

- clients/GT/OWNER_DIRECTIVE_RESTORE_FIRST_AR.md:الاستعادةأولاًوبواباتG0–G6؛الأنيميشنمؤجلبحسبتوجيهالمالكالأحدث.
- clients/GT/RESTORATION_PLAN.json وRESTORATION_PLAN_AR.md:الخطةوالسجل؛حقولتاريخيةلاتساويقبولاًحالياً.
- clients/GT/sessions/20261115-graphics-restoration/:الخطةوالفحوصوملاحظاتالعملالسابقة.
- clients/GT/METHOD_AR.md:المعايرةوأدواتالمختبروحدودتعميمها.
- docs/ZIP2_SOURCE_PROVIDER.md وscripts/gt_stage_serialized_owners.py:المصدرالمثبتوجمعالأجزاءوالتحقق.
- clients/GT/evidence/20261117_gt_post23_same_export_and_next6_cb_order_progress.json:آخر688/98/37ورفضNEXT6.
- clients/GT/evidence/20261120_gt_native_post23_and_next23b_integration.json و20261120_gt_fft_utilities_original_topology.json و20261120_gt_current_device_graphics_receipt.json و20261121_gt_next23b_source_composition_verified.json.

## تشغيلات يجب عدم خلطها

| التشغيل | المعنى |
|---|---|
|[43929698985](https://github.com/alwansan/raf/actions/runs/43929698985)|SAME-EXPORT688/786و98Dummy/37GUID،لاpixel/runtimeproof|
|[44779897149](https://github.com/alwansan/raf/actions/runs/44779897149)|NEXT23b134stage source-only|
|[44781063594](https://github.com/alwansan/raf/actions/runs/44781063594)|2312routesنجحتثمفشلpropertyflags|
|[44783011957](https://github.com/alwansan/raf/actions/runs/44783011957)|NEXT23bcompositionخاصكامل،لاUnity|
|[44781701884](https://github.com/alwansan/raf/actions/runs/44781701884)|FFTsourceنجح،UnityDXCفشلerrors1|
|[44783011963](https://github.com/alwansan/raf/actions/runs/44783011963)|NEXT6لايزالمرفوضاً|
|[44053092399](https://github.com/alwansan/raf/actions/runs/44053092399)|بناءNativeقديمناجح،ليسقبولبصريات|
|[45759923748](https://github.com/alwansan/raf/actions/runs/45759923748)|أولتجربةاصطناعيةفشلت|
|[45760345978](https://github.com/alwansan/raf/actions/runs/45760345978)|تجربةاصطناعيةفشلتقبلقبولpixels|
|[45760877767](https://github.com/alwansan/raf/actions/runs/45760877767)|UnityVulkanاصطناعي120pixelsPASSفقط|

المصدرZIP2:[15964ea8](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385).مصدرCLالمحلل:[8db59a4](https://github.com/alwansan/CL/tree/8db59a417be025dd8194f202a6dd29aaa132d300)،جلسةLogRaft-20261120-194258-229.صور12/13نوفمبرتثبتالمشكلةالتاريخيةولاتثبتحالمرشحجديد.

## المراجع الخارجية للأدوات

- [UnityCsReference2021.3ShaderProperties](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Shaders/ShaderProperties.cs):PerRendererData2،NoScaleOffset4،HDR16؛الخصائصالأصليةحُفظتلااختُلقت.
- [UnityPy1.23.0](https://pypi.org/project/UnityPy/1.23.0/):رابطsdistوبصمتهفيtoolchain/versions-and-checksums.json.
- [smol-vالمثبت](https://github.com/aras-p/smol-v/tree/6303e979b59153ee7007fd14e06d3fed8687b64c).
- [AssetRipperالمثبتتاريخياً](https://github.com/AssetRipper/AssetRipper/tree/036098ab525a3f9f693dc101edeb21faad4d32d8).
- [مختبرالرسومللقراءةفقط](https://github.com/alwansan/raf/blob/f933c4429803583d1ed5fa26e46bb0d3227f2027/prompt/graphics-lab/RESTORE_AR.md)،و[طريقةM00–M05](https://github.com/alwansan/raf/blob/1ca06009684047ef8156a939d4d2931326ad2cc7/gfxlab/PHASE_ONE_METHOD_HANDOFF_AR.md).المختبرمتشعبولايدمجتلقائياً،ولايُنسخقبولمعايرتهإلىكلاللعبة.

## تاريخ العمليات

caf77cf10:تشخيصالناروبوابةFFT؛6c071a414:دمجمسارpost23؛c066f2997:تركيبNEXT23b؛ef321ee90:مصدرFFTومحاولةUnity؛7e9925fdb:خصائصNEXT23b؛f3c8a2cda:آخرRESTOREعنالتجارب26نوفمبرقبلالتسليم.تحتhistory/نسخالمذكراتالكاملةبمافيهاأرقامتشغيلاتأقدموقراراتوإخفاقات؛لاينبغيحذفهاولااعتباركلنصقديمتعليماًحالياً.
''')
# readable standalone copy message
restore='''# GT — رسالة الاستعادة الشاملة | 26 نوفمبر 2026

أنا أتابع استعادة بصريات Raft Android في المستودع `alwansan/raf`، وفرع الكتابة الوحيد `feature/android-native-port`. هذه الرسالة تُنسخ إلى جلسة جديدة؛ التفاصيل والاختبارات والأدوات محفوظة في المستودع ولا تتطلب ذاكرة هذه المحادثة.

## ابدأ من هنا

1. راجع رأس الفرع وActions الفعلية قبل أي تعديل، واقرأ `AGENTS.md` مع أحدث طلب للمالك؛ النصوص التاريخية ليست تفويضاً جديداً.
2. اقرأ [حزمة التسليم الكاملة](sessions/20261126-complete-handoff/README_AR.md)، ثم [الخطة](sessions/20261126-complete-handoff/PLAN_AND_GOALS_AR.md)، [النتائج والقيود](sessions/20261126-complete-handoff/FINDINGS_AND_LIMITS_AR.md)، [الأدوات والتجهيز](sessions/20261126-complete-handoff/TOOLS_AND_REPRODUCTION_AR.md)، [الاختبارات](sessions/20261126-complete-handoff/TESTS_AND_RESULTS_AR.md)، [المراجع](sessions/20261126-complete-handoff/REFERENCES_AR.md) و[فهرس البصمات](sessions/20261126-complete-handoff/MANIFEST.json).
3. ثم راجع `state.json` و`RESTORATION_PLAN.json` و`RESTORATION_PLAN_AR.md` و`OWNER_DIRECTIVE_RESTORE_FIRST_AR.md` و`sessions/20261115-graphics-restoration/`. الأرقام داخل الحقول القديمة snapshots؛ لقطة التسليم والنتيجة ذات المصدر الأحدث هما المرجع.

## الهدف الكامل وأولوية المالك

استعادة ودمج المجسمات والخامات والتكستشرات والمِيب والألوان والصور والشيدرات وpasses/variants وMaterial Properties/TexEnv/Keywords وCB/samplers والظلال والماء وFoam وDepth وFFT والنار والجسيمات وPostFX وموارد الواجهات. الأولوية للمجسمات البيضاء ومربعات النار السوداء. الأنيميشن والحركات مؤجلة. ادمج كل دفعة صحيحة واحفظ دليلها؛ لا تستبدل الأصل بـDummy أو تقريب ثم تعلن الاكتمال.

الاستعادة والدمج أولاً، ثم XAPK تجريبي شامل للتوافق بعد إغلاق G0–G6. لا تنتظر بناءً يتجاوز عشر دقائق بدلاً من المالك؛ أعطه الرابط والحالة الفعلية واتركه يبلغ الاكتمال. لا تطلب هاتفاً أو تطلق XAPK لمجرد أن اختبار مصدر نجح. هدف الاستعادة موقوف مؤقتاً حتى أمر المالك بالاستئناف؛ طلب26نوفمبر الحالي كان حفظ ورفع كل العمل، وليس تشغيل تجارب ثقيلة. commit التسليم يحمل `[skip ci]` لمنعها؛ التخطي ليس نجاح CI.

## آخر حالة متحققة، دون تضخيم

- آخر SAME-EXPORT فعلي مقبول [43929698985](https://github.com/alwansan/raf/actions/runs/43929698985): **688/786 مستند Custom Material غير Dummy، و98 Dummy على37Shader GUID أصلية**، مع29213 Material/YAML/meta محمية. ليست نسبة اكتمال بصريات اللعبة، ولا مطابقة runtime أو Adreno. لا تزِد هذا العدد من source-only أو من مسودة غير منفذة.
- `6c071a414` دمج مسار دفعات NEXT30/23/18/17/15/11/10p33/10p31/7p11/7p33 في Native، مع ترتيب post9/post13/post23 ومصدر82owner مستقلة؛ الأصل W1 يحوي14owner فقط. Native المعدل لم يُبنَ هنا. **فجوة مهمة:** مصادر الدفعات العشر تستخدم `compose(engine_keywords=False)` وGT compile-selector خاصاً؛ كلمات اللعبة الأصلية لا تختار بقية المسارات ويقع الاختيار الافتراضي علىroute0. يوجد جرد ملف/سطر لكل مجموعة في `evidence/ten-group-runtime-keyword-audit.json` داخل حزمة التسليم. لا تعتبر غيابDummy وحده مطابقة تشغيلية.
- NEXT23b المصدر الكامل [44783011957](https://github.com/alwansan/raf/actions/runs/44783011957)،artifact14654640691:134/134برنامج،4Pass،1156route `[512,4,128,512]`،2312routed stages و2312entrypoints،20085CB offset matches و7516varyings. **هذا تركيب ShaderLab خاص، وليس Unity/engine keyword/GUID/device قبولاً.** حفظنا إيصالActions نفسه دائماً داخل الحزمة.
- خصائص NEXT23b الأصلية19، وأعلام0/2/4/16 محفوظة؛ أضيف دعم ضيق لـPerRendererData وNoScaleOffset وHDR دون تغيير قيم أو حدودRange أو تليين العقود السابقة. مسودة `raft-gt-next23b-original-shader-unity.yml` و`Next23bShaderValidation.cs` و`--next23b` verifier تحاول استعمال كلمات المصدر الأصلية وحزمة Vulkan مفكوكة. **لم تُشغل**؛ راجع حدودها في FINDINGS، ومنها environment/keyword-universe/passType provenance، قبل التنفيذ.
- FFT Utilities الأصلي **7Pass/7VSFS/12برنامج/خاصيتان**؛12roundtrips و14entrypoints نجحت محلياً. UnityDXC [44781701884](https://github.com/alwansan/raf/actions/runs/44781701884) فشل:passCount7،registeredKeywordVariants1،errors1،privateBundleCompiledfalse؛SPIR-V coordinate فيgt_fs_main. SVC الصحيح يسجلvariantNormal واحدة تغطي7Pass، وليس7entries مصطنعة.
- فحص أنواع FFT أثبت6sample coordinates كلهاfloat، وصفرinteger؛ لا تضعcasts تخمينية. التحكم المحلي HLSLcc يزيل7pragmas DXC فقط وجسمHLSL مطابق. SHA DXC `f8575ebd855cff193c9fdb506b5f2b2d427d4c583eb9c5c7af0d6ff39c948b23`،وHLSLcc `4d6e4815130daca16fdec13b4572f19c24c978e99787ba6f57658e4578759a69`. **UnityHLSLcc غير منفذ/مقبول.** workflow FFT المعدل والمثبت الجديد محفوظان؛ المثبت يتطلب source/Unity/decodedbundle receipts وowner/PathID→trace→GUID وmeta/commitments/rollback، ولا يوجد تثبيت فعلي أو wiring إنتاجي له بعد.
- NEXT6 ما زال مرفوضاً؛ لا تثبت lane semantics لقراءة padding الأصلية. لا تستبدلها أصفاراً ولا تحذف أعضاء الأصل أو تعطلspirv-val.
- CL pinned`8db59a4`،جلسة20261120-194258-229:968water pass roots =484Foam/Global و484FFT Utilities تطلبPass1 منشيدرذيPassواحدة؛0kernel roots بهذهالجلسة فقط؛3OBB GUID وcursor1؛ScudoOOM أثناءAdreno Vulkan renderpass. علاقةOOM بالـpasses أو صاحبالتخصيص غير مثبتة. ربطpatch112 بالبناء44053092399 استدلال،لاAPK SHA proof. التحليل والأرقاموالمراجعفيevidence/20261120_gt_current_device_graphics_receipt.json؛لاترفعrawdevice capturesلمجردتكرارالأرقام.
- Texture2D غيرexportable فيParticle108 لهpointerأصلي متطابق، لكنهليسدليلاًعلىصورةثالثةمصدرةأوalphaGPU؛لاتخترعلهGUIDخارجيأوتنسبهقطعاًإلىالنارالظاهرة.

## أحدث دليل اصطناعي منشور وحدوده

دخلت تحديثات GitHub حتى `f3c8a2cdacf04fdbfbced5f87a1407da223e3a15` قبل حزمة التسليم. شملت `gt_synthetic_material_alpha.py` واختباراته وshader/probe مؤلفين اصطناعياً. [45760877767](https://github.com/alwansan/raf/actions/runs/45760877767) نجح فيUnityVulkan/llvmpipe LLVM15:5حالات،120بكسلاً،max_error0. الإيصال الخام الاصطناعي والمدقق محفوظان بالحزمة. الفشلان45759923748 و45760345978 محفوظان أيضاً. **لا game pixels ولاAndroid ولا قبول نار اللعبة.**

الدفعتان المحليتان3/4 تذكران تاريخياً240بكسلاً لكلدفعة،والدفعة5تذكر15اختبارتعدادspace0. **أرشيفاتها ومصادرها غيرموجودة هنا**؛الأسماءوالبصماتفي `inventory/KNOWN_MISSING_LOCAL_ARTIFACTS.json`. ماحُفظهوالوصفالتاريخيالأصلي،لاادعاءرفعbytesلمتتوفر. القارئالمنشورRESOURCE لايلتقطregister(...,space0)؛المرشحالمحليالمذكورليسإصلاحاًإنتاجياًموجوداًبالمستودع،واختبارالتعدادالمستنسخليسstage_parameter_recordsكاملة.

## الاختبارات والأدوات المحفوظة

حزمةالتسليمتحفظنتائج740ملفاختبارتاريخياً:712pass و28fail؛واحدfixtureتاريخيةصُحح،و27أعيدفشلهاعلىbaselinef5115a4. كل774سجل متاح مؤرشفبأسماءوبصمات؛لاتنسبهإلىHEADالحاليولا تقلsuiteخضراء. الفحصالمركّزيومالتسليمفي`tests/current-focused-tests.txt` وأمرهفيJSONالمجاور؛نطاقهsource-free contracts فقط. فشلdiscoveryباسمtestمكرروفشلpipUnityPy بسببcompiler مفقودموثقان،وحلPYTHONPATHلمصدرUnityPy1.23مذكور.

الأدواتفيscripts/tests/android-port/.github،وأدواتالتأليفالتاريخيةفيtools/gt_handoff/20261126. إصداراتPython3.12.3 وUnity2021.3.45f2 وUnityPy1.23.0 وPillow13 وPyYAML6.0.3 وdebsarm64 وبصماتهاومصادرهافيtoolchain. ليستبيئاتSDKمخفيةمطلوبةمنذاكرةالجلسة. النواتجالخاصةيعادإنتاجهامنالمصدرالمصرحوالمثبتبالـscripts؛لاrawgamebytesأومفاتيحأوlicenseفيGit.

## الخطوة التالية عند أمر الاستئناف

راجع الرأس والحالة الفعلية أولاً؛ ثم أصلح وأثبت runtime keywords للدفعات، وراجع/نفذ NEXT23b Unity gate، وصحح FFT compiler control مع حزمة مفكوكة حقيقية ثم تثبيتSAME-EXPORT، وتابعNEXT6 و98Dummy وربطالماءوالناروبقيةG0–G6. راجعالنواقصالمحليةspace0قبلالادعاءباكتمالسلسلةالتعداد→الأسماء→البكسلات. لاتدمجفرعالمختبرالمتشعبدونمراجعة؛مرجعهالمثبتf933c4429803583d1ed5fa26e46bb0d3227f2027للقراءةفقط،وCLللقراءةفقط. لاكتابةعلىmain/zip2ولاLFSولاإلغاءjobsأومهاممجدولةبلاطلب.

**الخلاصةالحالية:الاستعادةالكاملةغيرمنجزة،الهدفمحفوظ،لاXAPKجديدطُلبضمنهذاالتسليم.** السجلالقديمكاملاًفيhistory/؛ اقرأهدليلاًتاريخياًمعنطاقهومصدره،لاتعليمةأعلىمنطلبالمالكالأحدث.
'''
(repo/'clients/GT/RESTORE_AR.md').write_text(restore)
# Canonical indexes retain their history with an explicit new entry point.
for path in ['clients/GT/README.md','clients/GT/START_AR.md','clients/GT/MEMORY.md','clients/GT/SUMMARY_AR.md','clients/GT/RESTORATION_PLAN_AR.md']:
 p=repo/path;target='sessions/20261126-complete-handoff/README_AR.md'
 note=f'> **نقطة التسليم الشاملة — 26 نوفمبر 2026:** ابدأ من [رسالة الاستعادة](RESTORE_AR.md) و[حزمة الأدوات والنتائج والخطة]({target}). السجل أدناه تاريخي؛ الاستعادة الكاملة وruntime keywords وUnity/GUID/device ما زالت غير مكتملة. طلب هذه الجلسة هو الحفظ والنشر فقط.\n\n'
 p.write_text(note+p.read_text())
for path in ['README.md','prompt/STATUS.md']:
 p=repo/path;p.write_text('> **GT — تسليم26نوفمبر2026:** [رسالة الاستعادة الشاملة](%s) · [الأدوات والاختبارات والنتائج والخطة](%s). الاستعادة الكاملة غير منجزة؛ هذا حفظ للعمل دونXAPKجديد.\n\n'%(('clients/GT/RESTORE_AR.md' if path=='README.md' else '../clients/GT/RESTORE_AR.md'),('clients/GT/sessions/20261126-complete-handoff/README_AR.md' if path=='README.md' else '../clients/GT/sessions/20261126-complete-handoff/README_AR.md'))+p.read_text())
p=repo/'clients/GT/state.json';d=json.loads(p.read_text());d['current_handoff']={'date':'2026-11-26','reviewed_remote_head':'f3c8a2cdacf04fdbfbced5f87a1407da223e3a15','purpose':'preserve all available work; restoration goal remains paused until resume','restore':'clients/GT/RESTORE_AR.md','index':'clients/GT/sessions/20261126-complete-handoff/README_AR.md','manifest':'clients/GT/sessions/20261126-complete-handoff/MANIFEST.json','missing_local_artifacts':'clients/GT/sessions/20261126-complete-handoff/inventory/KNOWN_MISSING_LOCAL_ARTIFACTS.json','restoration_complete':False,'historical_same_export_materials':{'non_dummy':688,'total_custom':786,'dummy':98,'original_guid_targets_remaining':37,'run':43929698985,'runtime_keyword_parity_proven':False},'NEXT23b_private_composition_verified_run':44783011957,'NEXT23b_Unity_engine_routes_proven':False,'FFT_HLSLcc_Unity_bundle_proven':False,'synthetic_Unity_pixel_run':45760877767,'synthetic_pixels':120,'production_pixels_proven':False,'new_XAPK_requested':False,'CI_suppressed_for_preservation_commit':True};p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
p=repo/'clients/GT/RESTORATION_PLAN.json';d=json.loads(p.read_text());d['current_handoff']=json.loads((repo/'clients/GT/state.json').read_text())['current_handoff'];d['updated_date']='2026-11-26';d['historical_rows_notice']='Existing workstream schema/counters preserve earlier stage snapshots; current_handoff and linked session are authoritative for latest limitations. No success inferred from changed update date.';p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
# Historical tools require deliberate adaptation, not blind execution.
p=repo/'tools/gt_handoff/20261126/README_AR.md';p.write_text('''# أدوات التأليف التاريخية المحفوظة\n\n`run-tests-isolated.py` هو ملف التشغيل التاريخي كما استُعمل، وفيه مسارات مطلقة؛ عدّل repo/output/python في نسخةscratch قبل إعادة استخدامه. سجلاته ونتائجه الأصلية فيclients/GT/sessions/20261126-complete-handoff/tests/.\n\n`port_post23_native.py` أداة تأليف نقلت دفعات مقبولة إلىworkflowNative؛ **نُفذت بالفعل ولا تُشغّل مرة ثانية علىHEADالحالي** لأنها مبنية علىanchors وترتيبقديم. اقرأهاكتاريخعمليةومصدرأفكار،وقارنdiffقبلإعادةأيحركة.\n\nلايشغلcommitالتسليمCI؛تعليماتالتجهيزوالفحصالمحمولةفي[دليلالأدوات](../../../clients/GT/sessions/20261126-complete-handoff/TOOLS_AND_REPRODUCTION_AR.md).\n''')
