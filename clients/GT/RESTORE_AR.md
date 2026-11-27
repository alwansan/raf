# GT — استئناف RAFT بتوجيه المالك | 27 نوفمبر 2026

**توجيه 27 نوفمبر الأحدث يرفع وقف RAFT السابق ويجيز نشر التعديلات المختبرة المسموح بها وأدواتها وأدلتها على `feature/android-native-port` وحده.** لا كتابة على المختبر أو CL أو BLACK. الأنيميشن مؤجل، ولا أصل غير مصرح أو مفاتيح أو تراخيص أو LFS أو CI يجلبها. XAPK النهائي فقط بعد إغلاق G0–G6 ودمجها والتحقق من الناتج.

## آخر دفعة: منع السقوط الصامت إلى route0 في عقد NEXT23b

- رأس الاستئناف الفعلي `1a78eb2764d39550f59e2948ae5ed89033c8ab73`؛ اقرأ رأس commit الحامل لهذا السجل كرأس نشر الدفعة. [تسليم 26 نوفمبر المثبت](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md) هو مرجع تاريخي للبايتات السابقة. بقي المختبر عند f933c4429803583d1ed5fa26e46bb0d3227f2027. راجعت Actions؛ آخر نجاح Unity 45760877767 الاصطناعي، ولا تشغيل فعلي جديد في الدفعة.
- [جلسة التنفيذ والأدلة](sessions/20261127-runtime-keyword-contract/README_AR.md) و[evidence.json](sessions/20261127-runtime-keyword-contract/evidence.json). أضيف `scripts/gt_runtime_keyword_contract.py` وربط في composer وفاحص NEXT23b: فرع صارم 4Pass/1156 لا يستبدل unmapped set بـprograms[0]؛ يقبل independent-toggle lattice كاملاً فقط، وإلا يتوقف. فاحص الصفوف يطابق كامل مجموعة الكلمات ويرفض الزيادات والتعارض والنطاق غير المثبت. بقي legacy diagnostic والـ10 مجموعات الخاصة دون تحويل إنتاجي.
- 14 اختباراً ناجحاً، و1156 اختيار marker اصطناعي حقيقي في GNU cpp؛ 5 منها لاختبار دوال المصدر الفعلية المعزولة ببدائل اختبار للتحويل وفك الحزمة. اختبارا بوابة قديمة نجحا بعد إصلاح fixture، وفحص نص workflow/probe نجح بقراءة المصدر. إعادة 14/14 في مجلد نظيف مع شرائح دوال مطابقة SHA256 وملفات مطابقة Git blob. لا clone كامل أو تحقق كامل MANIFEST القديم بسبب غياب checkout واتصال GitHub المباشر؛ حفظت الأصول المحلية المتاحة أولاً. ليس Unity أو SPIR-V أو runtime لعبة أو بكسلات.
- عُثر على أرشيف الدفعة الخامسة السابق: [النسخة التاريخية المحفوظة](sessions/20261127-runtime-keyword-contract/recovered-batch5-local-20261126.zip)، SHA256 a7b0a80c25c753f6e081f9307c804575399d833e5deec5ff338ef4ceee5222a6. لا تُحسب اختباراته الـ15 كاختبارات جديدة. أرشيفا 3/4 ما زالا مفقودين. MANIFEST التسليم السابق صالح للتدقيق على رأسه الثابت وليس لفرض بصمات قديمة على ملفات التطوير.
- commit بعلامة [skip ci] لتجنب مشغل الأصل الثقيل الذي يطابق ملفات الدفعة؛ لا نجاح CI جديد ولا استعادة لعبة مثبتة. بقيت 688/786 Custom و98 Dummy/37 GUID وفق آخر SAME-EXPORT تاريخي، وNEXT23b Unity وFFT HLSLcc وNEXT6 وبقية G0–G6 مفتوحة. لم يبدأ XAPK.

**عند المتابعة:** تحقق من الرأس وActions وبصمات الدفعة ثم أثبت scope/PassType وقائمة الكلمات لكل pass من مصدر مأذون مثبت مستقل، واختبرها بالعقد الصارم؛ لا تفترض أن الأعداد وحدها تثبت lattice. إذا sparse، اعزل grouping مثبتاً دون fallback. بعد ذلك Unity bundle gate مع ربط manifest SHA وVS/FS provenance ثم اختيار material runtime الحقيقي، وبعد الإثبات عمّم على الدفعات العشر. تابع الاستعادة والدمج لكل الرسوم حسب الخطة، لا اختبار هاتف جزئي ولا XAPK مبكر.

---

## سجل التسليم التاريخي 26 نوفمبر (النص أدناه محفوظ كاملاً؛ أي وقف سابق أو صلاحية أضيق تجاوزه طلب 27 نوفمبر)

# GT — رسالة الاستعادة الشاملة | 26 نوفمبر 2026

أنا أتابع استعادة بصريات Raft Android في المستودع `alwansan/raf`، وفرع الكتابة الوحيد `feature/android-native-port`. هذه الرسالة تُنسخ إلى جلسة جديدة؛ التفاصيل والاختبارات والأدوات محفوظة في المستودع ولا تتطلب ذاكرة هذه المحادثة.

## ابدأ من هنا

1. راجع رأس الفرع وActions الفعلية قبل أي تعديل، واقرأ `AGENTS.md` مع أحدث طلب للمالك؛ النصوص التاريخية ليست تفويضاً جديداً.
2. اقرأ [حزمة التسليم الكاملة](sessions/20261126-complete-handoff/README_AR.md)، ثم [الخطة](sessions/20261126-complete-handoff/PLAN_AND_GOALS_AR.md)، [النتائج والقيود](sessions/20261126-complete-handoff/FINDINGS_AND_LIMITS_AR.md)، [الأدوات والتجهيز](sessions/20261126-complete-handoff/TOOLS_AND_REPRODUCTION_AR.md)، [الاختبارات](sessions/20261126-complete-handoff/TESTS_AND_RESULTS_AR.md)، [المراجع](sessions/20261126-complete-handoff/REFERENCES_AR.md) و[فهرس البصمات](sessions/20261126-complete-handoff/MANIFEST.json).
3. ثم راجع `state.json` و`RESTORATION_PLAN.json` و`RESTORATION_PLAN_AR.md` و`OWNER_DIRECTIVE_RESTORE_FIRST_AR.md` و`sessions/20261115-graphics-restoration/`. الأرقام داخل الحقول القديمة snapshots؛ لقطة التسليم والنتيجة ذات المصدر الأحدث هما المرجع.

## الهدف الكامل وأولوية المالك

استعادة ودمج المجسمات والخامات والتكستشرات والمِيب والألوان والصور والشيدرات وpasses/variants وMaterial Properties/TexEnv/Keywords وCB/samplers والظلال والماء وFoam وDepth وFFT والنار والجسيمات وPostFX وموارد الواجهات. الأولوية للمجسمات البيضاء ومربعات النار السوداء. الأنيميشن والحركات مؤجلة. ادمج كل دفعة صحيحة واحفظ دليلها؛ لا تستبدل الأصل بـDummy أو تقريب ثم تعلن الاكتمال.

الاستعادة والدمج أولاً، ثم XAPK تجريبي شامل للتوافق بعد إغلاق G0–G6. لا تنتظر بناءً يتجاوز عشر دقائق بدلاً من المالك؛ أعطه الرابط والحالة الفعلية واتركه يبلغ الاكتمال. لا تطلب هاتفاً أو تطلق XAPK لمجرد أن اختبار مصدر نجح. هدف الاستعادة موقوف مؤقتاً حتى أمر المالك بالاستئناف؛ طلب 26 نوفمبر الحالي كان حفظ ورفع كل العمل، وليس تشغيل تجارب ثقيلة. commit التسليم يحمل `[skip ci]` لمنعها؛ التخطي ليس نجاح CI.

## آخر حالة متحققة، دون تضخيم

- آخر SAME-EXPORT فعلي مقبول [43929698985](https://github.com/alwansan/raf/actions/runs/43929698985): **688/786 مستند Custom Material غير Dummy، و98 Dummy على 37 Shader GUID أصلية**، مع 29213 Material/YAML/meta محمية. ليست نسبة اكتمال بصريات اللعبة، ولا مطابقة runtime أو Adreno. لا تزِد هذا العدد من source-only أو من مسودة غير منفذة.
- `6c071a414` دمج مسار دفعات NEXT30/23/18/17/15/11/10p33/10p31/7p11/7p33 في Native، مع ترتيب post9/post13/post23 ومصدر 82 owner مستقلة؛ الأصل W1 يحوي 14 owner فقط. Native المعدل لم يُبنَ هنا. **فجوة مهمة:** مصادر الدفعات العشر تستخدم `compose(engine_keywords=False)` وGT compile-selector خاصاً؛ كلمات اللعبة الأصلية لا تختار بقية المسارات ويقع الاختيار الافتراضي على route 0. يوجد جرد ملف/سطر لكل مجموعة في `evidence/ten-group-runtime-keyword-audit.json` داخل حزمة التسليم. لا تعتبر غياب Dummy وحده مطابقة تشغيلية.
- NEXT23b المصدر الكامل [44783011957](https://github.com/alwansan/raf/actions/runs/44783011957)، artifact 14654640691: 134/134 برنامج، 4 Pass، 1156 route `[512,4,128,512]`، 2312 routed stages و2312 entrypoints، 20085 CB offset matches و7516 varyings. **هذا تركيب ShaderLab خاص، وليس Unity/engine keyword/GUID/device قبولاً.** حفظنا إيصال Actions نفسه دائماً داخل الحزمة.
- خصائص NEXT23b الأصلية 19، وأعلام 0/2/4/16 محفوظة؛ أضيف دعم ضيق لـ PerRendererData وNoScaleOffset وHDR دون تغيير قيم أو حدود Range أو تليين العقود السابقة. مسودة `raft-gt-next23b-original-shader-unity.yml` و`Next23bShaderValidation.cs` و`--next23b` verifier تحاول استعمال كلمات المصدر الأصلية وحزمة Vulkan مفكوكة. **لم تُشغل**؛ راجع حدودها في FINDINGS، ومنها environment/keyword-universe/passType provenance، قبل التنفيذ.
- FFT Utilities الأصلي **7 Pass / 7 VSFS / 12 برنامج / خاصيتان**؛ 12 roundtrips و14 entrypoints نجحت محلياً. Unity DXC [44781701884](https://github.com/alwansan/raf/actions/runs/44781701884) فشل: passCount 7، registeredKeywordVariants 1، errors 1، privateBundleCompiled false؛ SPIR-V coordinate في gt_fs_main. SVC الصحيح يسجل variant Normal واحدة تغطي 7 Pass، وليس 7 entries مصطنعة.
- فحص أنواع FFT أثبت 6 sample coordinates كلها float، وصفر integer؛ لا تضع casts تخمينية. التحكم المحلي HLSLcc يزيل 7 pragmas DXC فقط وجسم HLSL مطابق. SHA DXC `f8575ebd855cff193c9fdb506b5f2b2d427d4c583eb9c5c7af0d6ff39c948b23`، وHLSLcc `4d6e4815130daca16fdec13b4572f19c24c978e99787ba6f57658e4578759a69`. **Unity HLSLcc غير منفذ/مقبول.** workflow FFT المعدل والمثبت الجديد محفوظان؛ المثبت يتطلب source/Unity/decodedbundle receipts وowner/PathID→trace→GUID وmeta/commitments/rollback، ولا يوجد تثبيت فعلي أو wiring إنتاجي له بعد.
- NEXT6 ما زال مرفوضاً؛ لا تثبت lane semantics لقراءة padding الأصلية. لا تستبدلها أصفاراً ولا تحذف أعضاء الأصل أو تعطل spirv-val.
- CL pinned `8db59a4`، جلسة 20261120-194258-229: 968 water pass roots = 484 Foam/Global و484 FFT Utilities تطلب Pass 1 من شيدر ذي Pass واحدة؛ 0 kernel roots بهذه الجلسة فقط؛ 3 OBB GUID وcursor 1؛ Scudo OOM أثناء Adreno Vulkan renderpass. علاقة OOM بالـ passes أو صاحب التخصيص غير مثبتة. ربط patch 112 بالبناء 44053092399 استدلال، لا APK SHA proof. التحليل والأرقام والمراجع في `evidence/20261120_gt_current_device_graphics_receipt.json`؛ لا ترفع raw device captures لمجرد تكرار الأرقام.
- Texture2D غير exportable في Particle108 له pointer أصلي متطابق، لكنه ليس دليلاً على صورة ثالثة مصدرة أو alpha GPU؛ لا تخترع له GUID خارجياً أو تنسبه قطعاً إلى النار الظاهرة.

## أحدث دليل اصطناعي منشور وحدوده

دخلت تحديثات GitHub حتى `f3c8a2cdacf04fdbfbced5f87a1407da223e3a15` قبل حزمة التسليم. شملت `gt_synthetic_material_alpha.py` واختباراته وshader/probe مؤلفين اصطناعياً. [45760877767](https://github.com/alwansan/raf/actions/runs/45760877767) نجح في Unity Vulkan/llvmpipe LLVM 15: 5 حالات، 120 بكسلاً، max_error 0. الإيصال الخام الاصطناعي والمدقق محفوظان بالحزمة. الفشلان 45759923748 و45760345978 محفوظان أيضاً. **لا game pixels ولا Android ولا قبول نار اللعبة.**

الدفعتان المحليتان 3/4 تذكران تاريخياً 240 بكسلاً لكل دفعة، والدفعة 5 تذكر 15 اختبار تعداد space0. **أرشيفاتها ومصادرها غير موجودة هنا**؛ الأسماء والبصمات في `inventory/KNOWN_MISSING_LOCAL_ARTIFACTS.json`. ما حُفظ هو الوصف التاريخي الأصلي، لا ادعاء رفع bytes لم تتوفر. القارئ المنشور RESOURCE لا يلتقط `register(...,space0)`؛ المرشح المحلي المذكور ليس إصلاحاً إنتاجياً موجوداً بالمستودع، واختبار التعداد المستنسخ ليس `stage_parameter_records` كاملة.

## الاختبارات والأدوات المحفوظة

حزمة التسليم تحفظ نتائج 740 ملف اختبار تاريخياً: 712 pass و28 fail؛ فشل واحد بسبب fixture تاريخية صُحح، و27 أُعيد فشلها على baseline `f5115a4`. كل 774 سجل متاح مؤرشف بأسماء وبصمات؛ لا تنسبه إلى HEAD الحالي ولا تقل suite خضراء. الفحص المركّز يوم التسليم في `tests/current-focused-tests.txt` وأمره في JSON المجاور؛ نطاقه source-free contracts فقط. فشل discovery باسم test مكرر وفشل pip UnityPy بسبب compiler مفقود موثقان، وحل PYTHONPATH لمصدر UnityPy 1.23 مذكور.

الأدوات في scripts/tests/android-port/.github، وأدوات التأليف التاريخية في `tools/gt_handoff/20261126`. إصدارات Python 3.12.3 وUnity 2021.3.45f2 وUnityPy 1.23.0 وPillow 13 وPyYAML 6.0.3 وdebs arm64 وبصماتها ومصادرها في toolchain. ليست بيئات SDK مخفية مطلوبة من ذاكرة الجلسة. النواتج الخاصة يعاد إنتاجها من المصدر المصرح والمثبت بالـ scripts؛ لا raw game bytes أو مفاتيح أو license في Git.

## الخطوة التالية عند أمر الاستئناف

راجع الرأس والحالة الفعلية أولاً؛ ثم أصلح وأثبت runtime keywords للدفعات، وراجع/نفذ NEXT23b Unity gate، وصحح FFT compiler control مع حزمة مفكوكة حقيقية ثم تثبيت SAME-EXPORT، وتابع NEXT6 و98 Dummy وربط الماء والنار وبقية G0–G6. راجع النواقص المحلية space0 قبل الادعاء باكتمال سلسلة التعداد→الأسماء→البكسلات. لا تدمج فرع المختبر المتشعب دون مراجعة؛ مرجعه المثبت `f933c4429803583d1ed5fa26e46bb0d3227f2027` للقراءة فقط، وCL للقراءة فقط. لا كتابة على main/zip2 ولا LFS ولا إلغاء jobs أو مهام مجدولة بلا طلب.

**الخلاصة الحالية: الاستعادة الكاملة غير منجزة، الهدف محفوظ، لا XAPK جديد طُلب ضمن هذا التسليم.** السجل القديم كاملاً في history/؛ اقرأه دليلاً تاريخياً مع نطاقه ومصدره، لا تعليمة أعلى من طلب المالك الأحدث.
