# خطة استكمال استعادة رسوم Raft Android

## GT — آخر تحقق للمرحلة الحية (16 نوفمبر)

- SAME EXPORT NEXT17 [43917381834](https://github.com/alwansan/raf/actions/runs/43917381834) **SUCCESS**، 628/786 Custom Material غير Dummy و158 Dummy/43 Shader GUID، 0 broken، 29,213 material/meta/YAML SHA untouched؛ لا Pixel/device parity. [artifact](https://github.com/alwansan/raf/actions/runs/43917381834/artifacts/14256010749).
- NEXT15 القديم [43918007004](https://github.com/alwansan/raf/actions/runs/43918007004) FAILED بسبب wrong inherited NEXT17 translator؛ المصحح [43920541904](https://github.com/alwansan/raf/actions/runs/43920541904) IN PROGRESS. NEXT11 المصحح [43920553298](https://github.com/alwansan/raf/actions/runs/43920553298) IN PROGRESS.
- NEXT10p33 أحدث PENDING هو [43926288406](https://github.com/alwansan/raf/actions/runs/43926288406)، والقديم pending 43922026302 CANCELLED بسبب replacement؛ NEXT10p31 [43922253136](https://github.com/alwansan/raf/actions/runs/43922253136) IN PROGRESS. NEXT7p11 [43925468867](https://github.com/alwansan/raf/actions/runs/43925468867) وNEXT7p33 [43925787952](https://github.com/alwansan/raf/actions/runs/43925787952) IN PROGRESS؛ أحدث نسخ pending 43926307167 و43926312944. الاختبارات الثابتة نجحت لكن لا تُحسب كـSAME EXPORT.
- أهداف post18 حتى post23 المشروطة فقط 643/143/42 → 654/132/41 → 664/122/40 → 674/112/39 → 681/105/38 → 688/98/37. يجب انتظار تقارير postinstall الحقيقية قبل إعلان التقدم.


## خطة متابعة دفعة 7-material الأصلية — GT — 16 نوفمبر

1. افتح نتائج SAME-EXPORT بالترتيب: NEXT15 43920541904 ثم NEXT11 43920553298 ثم NEXT10p33 43922026302 ثم NEXT10p31 43922253136 ثم NEXT7p11 43925468867 وNEXT7p33 43925787952. *التشغيلات التي تستخدم SHA قديم قبل الإصلاح لا تُقبل.*
2. NEXT7p11 source 22 original D3D11/11 VSFS [4,5,2]/3 Pass/Range4؛ يطلب post21 فعلي 674/112/39 واثنين 7-material، وبعد تثبيت GUID أصلي يطلب post22 681/105/38. NEXT7p33 source 58 D3D11/33 VSFS [8,13,8,4]/4 Pass/Range0؛ يطلب post22 فعلي وواحد 7-material فقط ثم post23 688/98/37. كل عدادات post22/23 **gates conditional** حتى SUCCESS و29,213 protected SHA.
3. [43925234660](https://github.com/alwansan/raf/actions/runs/43925234660) static source/installer و[43925851391](https://github.com/alwansan/raf/actions/runs/43925851391) static final-stage wiring ناجحان. الدليل `clients/GT/evidence/20261116_gt_next7pair_original_guid_pipeline_progress.json`. ثم بقي 37 Shader GUID فقط إذا ثبت نجاح الدفعات الست؛ لا تعده واقعاً الآن.
4. بعد تصحيح ما يفشل، استعد الباقي من shader targets والموارد الأصلية Water/FFT/kernel6/Foam/Depth/Fire/PostFX/G0–G6 والمجسمات. الأنيميشن مؤجل، XAPK GT مؤجل حتى الاستعادة الشاملة.


## خطة GT — إعادة التشغيل الصحيح لـNEXT15/NEXT11 ثم 10p33/10p31 (16 نوفمبر)

- **المرجع المثبت الوحيد حالياً** SAME EXPORT post17 [43787809110](https://github.com/alwansan/raf/actions/runs/43787809110): **628/786 Custom Material non-Dummy و158 Dummy/43 GUID**؛ 29,213 protected original SHA unchanged، 0 broken.
- يجب فحص التشغيلات المصححة، لا القديمة: NEXT15 [43920541904](https://github.com/alwansan/raf/actions/runs/43920541904)، NEXT11 [43920553298](https://github.com/alwansan/raf/actions/runs/43920553298). إصلاح المترجم الموروث NEXT17 تم عند f1625a72 و8f567bec.
- NEXT10p33 [43922026302](https://github.com/alwansan/raf/actions/runs/43922026302) يستلزم أولاً post19 الحقيقي 654 non-Dummy/132 Dummy/41 targets، ثم original 58 D3D11/33 VSFS/4 Pass مع GUID أصلي و29,213 SHA؛ post20 المشروط 664/122/40. NEXT10p31 [43922253136](https://github.com/alwansan/raf/actions/runs/43922253136) يستلزم post20 ثم original 55 D3D11/31 VSFS [8,13,8,2] ومجموعة واحدة 10-Material؛ post21 المشروط 674/112/39. **كل الأعداد المستقبلية gates وليست إنجازات حتى SUCCESS والـsafe report.**
- إذا فشل أي مسار: استخرج أول step فاشلة من logs، حدّد السبب، أصلح فرع feature/android-native-port فقط، واطلق Workflow مصححاً يحافظ على SHA/GUID/Meta. بعد الشيدرات أكمل Spectrum/Foam/Depth/FFT/kernel6 وFire alpha ومطابقة الموارد والرسوم G0–G6. لا XAPK من GT الآن.
- Evidence: `clients/GT/evidence/20261116_gt_next10pair_original_guid_pipeline_progress.json`. CI static wiring [43922343892](https://github.com/alwansan/raf/actions/runs/43922343892) SUCCESS.


- **Parallel next11 real same-export verification:** [43918847740](https://github.com/alwansan/raf/actions/runs/43918847740) IN PROGRESS from workflow raft-gt-next11-original-full-export.yml commit e8ca45d0; requires actual next15 643/143/42 before original NEXT11 GUID install, then full post19 SHA recensus. **654/132/41 remains future gate ONLY**.

## GT next engineering batch — real post17 and next15 (16 Nov 2026)

- Latest accepted **[43787809110](https://github.com/alwansan/raf/actions/runs/43787809110) SUCCESS** same-export NEXT17: **628/786 non-Dummy Custom Materials**, **158 Dummy/43 original Shader GUID targets**; 29,213 Material/YAML/meta protected original SHA unchanged, zero broken references, no APK/XAPK. NEXT18 prior real [43787527334](https://github.com/alwansan/raf/actions/runs/43787527334) accepted 611/786, 175/44.
- New original SHA-bound NEXT15 full workflow .github/workflows/raft-gt-next15-original-full-export.yml commit 26000122, running [43918007004](https://github.com/alwansan/raf/actions/runs/43918007004). Require genuine post17 158/43, 58 SHA-source D3D11 programs, Unity Vulkan 4 Pass/33 VSFS, authentic same-export GUID and all 29,213 original SHA. **Post18 643 non-Dummy/143 Dummy/42 targets is a conditional gate, NOT established.**
- Next: check actual run outcome and repair only verified failing step; then original NEXT11, 10p33/31, 7p11/33; finish all remaining 43 original Shader targets with full recensus. Separately close water Spectrum/Foam/Depth/FFT/kernel6, Fire Alpha, texture/mesh/shadow PostFX G0–G6. Android pixels and XAPK only after resource restoration per owner directive.
- Three report-field corrections commits 44083b60/1668151a/a8f8de32; static CI [43917400073](https://github.com/alwansan/raf/actions/runs/43917400073) success. Evidence: clients/GT/evidence/20261116_gt_post17_real_guid_next15_full_export_progress.json.


آخر تحديث 15 تشرين الثاني 2026، توقيت بغداد. الخطة تغطي استعادة الرسوم قبل اختبار الهاتف.

| المرحلة | ما أُنجز | المطلوب لإغلاقها |
| --- | --- | --- |
| المجسمات | مطابقة هندسة 4,708 Mesh مع المصدر في التصدير الكامل | تحقق من الاستيراد وربط المجسم الصحيح بالمشاهد وظهوره في اللعبة. تابع اختفاء اللون الأبيض من جهة المواد والشيدرات المرتبطة |
| الخامات والألوان | 4,903 قيمة لون أصلية عبر 1,536 مادة، 9 مصفوفات و28 رابط مواد، 416 رابط تكستشر خارجي | أعد التحقق في مشروع Unity الكامل بعد كل خطوات الدمج. راجع أي فرق بألوان المشهد أو إعدادات التكستشر من واقع الاختبارات |
| الشيدرات الظاهرة | استعادة ثمانية شيدرات مجسمات ونباتات، ودمج Particle108 وSmoke34 وCandle16 وParticleShader في مسار إعادة البناء | أكمل BillboardFade، ثم استخدم جرد المواد الكامل لتحديد وترتيب الشيدرات الأصلية المتبقية، وكرر الاستعادة والترجمة والتثبيت على نفس الـGUID. أعد جرد المواد بعد كل دفعة |
| الماء | Depth Copy وSpectrum وFFT لها مسارات استعادة، وFFT الأصلي بـ20 نواة ثبت في فحص التصدير الكامل | تحقق من المراجع والتشغيل وإخراج الماء والرغوة، ومن اختلاف Vulkan وOpenGLES إذا كان كلاهما مساراً فعلياً للمشروع. راجع حالة Foam وإعدادات الـRT والـdispatch من المصدر |
| القبول قبل الحزمة | فحوص التصدير الكامل وحزم Unity المعزولة متوفرة | نفّذ إعادة بناء واستيراد فعليين للمشروع الكامل مع الاستعادات، وراجع التقارير لكل الشيدرات والمواد. افحص النار والشمعة والدخان على مستوى shader/texture/alpha وربط المكونات |
| اختبار الهاتف | توجد لوقات وصور CL تصلح خط أساس | بعد اكتمال الاستعادة اطلق أو نسّق بناء XAPK حسب توجيه المالك، وسلّمه رقم التشغيل مباشرة إذا طال. عند توفره، اختبر ظهور الألوان والمجسمات، شفافية النار والدخان، والماء، ثم طابق لوقات وصور الجهاز وعالج المتبقي |

## تسلسل العمل

1. طابق الفرع البعيد مع المحلي وتحقق من إدماج BillboardFade في الفرع وحالة فحص Unity. انظر [تفاصيل العمل](03-WORK_NOTES_AR.md).
2. اكتمل فحص BillboardFade المعزول في Unity Vulkan على تشغيل 43723487222 (9 مسارات، ForwardBase/ForwardAdd [4,5]، أخطاء ترجمة صفر). أضيفت بوابة تحقق صارمة وتثبيت GUID الأصلي إلى مسار الإنتاج في d2d00b9810de1724248f95601d8f91a86e757654. ما يزال تحقق تنفيذ إعادة البناء الكامل وربط المواد بعد التثبيت مفتوحاً؛ لا تخلط نجاح الحزمة المعزولة بنجاح المشروع النهائي.
3. اربط هاشات الجرد الكامل بأسماء شيدرات ZIP2 على الرنر. احسب تعريف الشيدر والمواد المرتبطة به بعد تركيب الاستعادات الحالية. الأعداد المتبقية غير المعروفة في العينة القديمة قد تتجاوز BillboardFade بالأثر.
4. شغّل فحص الدمج الكامل بلا حزمة لعبة لمعرفة الانخفاض الفعلي بعد كل التثبيتات، ثم أكمل الشيدرات الباقية حسب التأثير. لا تعتمد على نتيجة فحص وجهة ملف وحدها لإثبات التثبيت.
5. قارن حزم أندرويد مع المصدر، وبعدها انتقل إلى XAPK التجريبي بالترتيب أعلاه. الأنيميشنات خارج أولوية هذه المرحلة، مع حفظ نتائج الـrig التاريخية.

### خطة متابعة 16 تشرين الثاني 2026

- النجاح المثبت: 9 شيدرات أصلية في تصدير ZIP2 الكامل [43759856414](https://github.com/alwansan/raf/actions/runs/43759856414)، 453 من 786 مادة Custom مستعادة، 333 Dummy متبقية، مع ثبات 29213 ملف Material/meta. هذا ليس اكتمال الرسوم كلها.
- جرد جميع مصادر Shader48 [43766412259](https://github.com/alwansan/raf/actions/runs/43766412259): 82 مالكاً موثقاً SHA، 165 Shader48 في 14 مالكاً، 163 اسماً؛ ترتبط 330 مادة Dummy بأسماء أصلية فريدة و3 مواد باسم مكرر بين 3 شيدرات أصلية. صفر أسماء Dummy غير موجودة في المصدر. لا يثبت تطابق GUID أو أصالة برنامج Android من مجرد الاسم.
- تشغيل دمج 13 شيدراً [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277) يركب Particle108/Particle20/Smoke34/Candle16 بعد التسعة ويعيد جرد مواد Dummy. النتيجة غير نهائية حتى ختم SUCCESS.
- فحص [43766959343](https://github.com/alwansan/raf/actions/runs/43766959343) يقيس SubShader/Pass/D3D11 keyword variants للأهداف الـ12 الأعلى كثافة؛ استخدم نتائج التوبولوجيا لبداية دفعات استعادة برامجها الأصلية، لا Dummy شكلياً، مع الحفاظ على source owner + GUID.
- فحص Alpha [43766815679](https://github.com/alwansan/raf/actions/runs/43766815679) يميّز مشكلة parsing لمادة Unity من خطأ الربط بمصدر Texture2D؛ لا تدّع إصلاح النار قبل مسار صور ألفا والاختبار المرئي.
- الأولوية لاستعادة كل الموارد والشيدرات والمجسمات والخامات والماء والنار، وتأجيل XAPK والأنيميشن حسب تعليمات المالك.

### الحالة المحدثة — نجاح 13 أصل Shader48 والتخطيط للمتبقي

- التشغيل 43764506277 انتهى SUCCESS في نفس AssetRipper ZIP2 export: 9 model shaders + 4 original particle shaders. CUSTOM Material من أصل 786: 540 ببرنامج غير Dummy (68.7%)، والباقي 246 Dummy مرتبطة بـ47 شيدر مستخدم. 750 built-in، 1536 Material بالمجموع، 0 Shader broken. 29213 ملف Material/meta/YAML محمي مطابق للبايتات. انظر clients/GT/evidence/20261116_gt_thirteen_original_shader_same_export_acceptance.json.
- التشغيل 43768013634 انتهى SUCCESS وأثبت استعادة 55/55 برنامج D3D11 لشيدر يربط 30 مادة أصلية وتحويلها إلى Vulkan1.1/HLSL، و31 keyword pairs/62 stage compilations، ثم 70 parameter records و1007 CB offsets و364 texture/sampler mappings و232 varying records و4-pass ShaderLab/62 entrypoints. لا يثبت Unity import بعد.
- بدأ اختبار Unity Android Vulkan للشيدر ذي 30 مادة بالـ31 routes والـ4 Passes، التشغيل 43768744473. لا XAPK. الإخراج المطلوب safe receipt يثبت original candidate SHA/passCount/routes/errors ثم verify Vulkan bundle.
- أطلقت إعادة ترتيب الـ82 مالكاً وفق العدد الفعلي بعد 13 شيدراً: 246 Dummy/47 GUID، التشغيل 43768958865. لا تعتمد الـ333 الماضية بعد اكتمال 13، فهي مرجع لحالة التسعة فقط.
- تقرير Alpha الحقيقي 43767741576 أظهر خمسة Material21 أصلية و10 TexEnv: 9 exported external Texture2D refs صحيحة (type3 fileID 2800000) ومؤشر واحد type0 محلي/fileID آخر. لا تستبدل GUID ولا تعتبر الصور الأصلية تالفة. شغّل تقرير تصنيف لاحق 43767766873 قبل تقرير مرئي.
- أولوية المالك: استعادة جميع الموارد والشيدرات أولاً، شيدرات الماء والنار والظلال والخامات والمجسمات؛ لا XAPK ولا ترحيل الأنيميشن الآن.


### أحدث خطة متابعة – 16 نوفمبر 2026 (RESTORE_AR هو المرجع الرئيسي)
- بعد [43764506277](https://github.com/alwansan/raf/actions/runs/43764506277) SUCCESS: 540 من 786 مادة مخصصة أصبحت non-Dummy، و246 مادة Dummy ما تزال مرتبطة بـ47 Shader. هذا 68.7% من **المواد المخصصة فقط** وليس كل الموارد. من أصل 1536 Material توجد 750 built-in، وصفر links broken، و29213 ملفات Material/meta/YAML بلا تغيير.
- [43768958865](https://github.com/alwansan/raf/actions/runs/43768958865) SUCCESS: مصدر 243 من 246 مادة Dummy فريد بالاسم؛ 3 ملتبسة وثلاثة مصادر Shader48 لها الاسم ذاته؛ 0 خارج أصل 82 ملف ZIP2 الموثق. الاسم وحده لا يحدد GUID المصدر.
- [43769218778](https://github.com/alwansan/raf/actions/runs/43769218778) SUCCESS: شيدر next30 أصلي 55/55 برنامج D3D11 مترجم إلى Vulkan1.1، 4 Passes، 31 مسار VS/FS [8,13,8,2] داخل Unity Android Bundle الحقيقي. [43769866165](https://github.com/alwansan/raf/actions/runs/43769866165) SUCCESS لاختبارات المثبّت؛ التثبيت الفعلي بالـGUID الأصلي ما زال مطلوباً.
- التالي: تنفيذ same-export next30 GUID-proven installer وجرد مواد Dummy من جديد، مع مواصلة إصلاح Fire Alpha type0 TexEnv وFFT/Water/Compute والمجسمات والألوان. لا XAPK حتى كل الموارد مستعادة.
- **التزام مستمر:** تحديث RESTORE_AR.md في كل جلسة وبعد كل دفعة موثقة، إلى جانب 01/02/03 وتقرير الأدلة؛ افحص دائماً HEAD الحالي ولا تدّع عمل خلفية تلقائي.

### CI جديد بعد تحديث RESTORE_AR — 16 نوفمبر 2026
- بدأ [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176) في full ZIP2 same-export بعد التسعة وأربعة Particle لإعادة بناء وترجمة وتثبيت next30 Shader48 مع الحفاظ على GUID الأصلي والتحقق من 31 VS/FS Vulkan routes. يراجع 29213 Material/meta/YAML محمي، ويعيد حساب المواد الحقيقية. **العدد المستهدف فقط**: 570 non-Dummy / 216 Dummy / 46 shader references؛ **آخر قيمة مثبتة لا تزال** 540 non-Dummy / 246 Dummy / 47 shader references، إلى أن تنتهي CI بنجاح. لا APK/XAPK. يجب فحص نتائج run وتحديث clients/GT/RESTORE_AR.md و01/02/03 مجدداً فور ظهور دليل جديد.

### تقدم 23 مادة – 16 نوفمبر
- بدأ [43773953670](https://github.com/alwansan/raf/actions/runs/43773953670) فحص source-only الأصلي لاستعادة شيدر يربط 23 مادة Custom Dummy، فيه 4 Pass / 33 زوج VS/FS / 8 VS orphans / 58 برنامج D3D11 أصلي، مع تمييزه عن شيدر آخر له 23 مادة لكنه يحتوي 1156 variants ولا يجوز اختزاله. بوابة الجرد كل الـ82 owner من ZIP2 SHA. لم يثبت Unity أو GUID بعد، ولن ينشئ XAPK. افحص النتيجة عند العودة ثم حدّث RESTORE_AR.md أولاً والخطة/الاختبارات/الدليل. العدد المثبت يبقى 246 Dummy حتى قبول نفس التصدير في [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176).

### أحدث نتائج 16 نوفمبر — next23 original source PASSED، Unity Vulkan مفتوح
- [43774524669](https://github.com/alwansan/raf/actions/runs/43774524669) SUCCESS: شيدر 23 Material أصلي، 58/58 D3D11→Vulkan/HLSL، 33 VS/FS + 8 orphan VS، 66 routed stage compilations، 74 parameter records، 1192 CB offsets و552 Texture/Sampler mappings و236 varyings، 17 property بينها 3 Range وDefault واحد خارج bounds حفظ كما هو. فحص Source فقط، لا GUID.
- [43774787696](https://github.com/alwansan/raf/actions/runs/43774787696) بدأ private Unity Android Vulkan bundle للتحقق من 4 Pass و33 VS/FS routes بالـSMOL-V. لم تقبل نتيجته حتى الآن. بعد PASS يتوجب تثبيت original Shader48 عبر نفس source→export GUID في التصدير الأصلي وفحص مواد Dummy.
- [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176) next30 في full export لا يزال بلا نتيجة نهائية. آخر أرقام يقينية: **540/786 non-Dummy، 246 Dummy، 47 Shader targets**؛ لا XAPK. ملف المصدر الرئيسي الحي: clients/GT/RESTORE_AR.md؛ حدّثه في كل دفعة.

## تحديث مثبت — 16 نوفمبر 2026 / GT بعد NEXT30

- مرحلة `P04/P05`: [43773151176](https://github.com/alwansan/raf/actions/runs/43773151176) **SUCCESS** نفس التصدير، NEXT30 مثبت بـGUID الحقيقي، 31-route Unity Vulkan؛ الجرد بعد 14: **570/786 non-Dummy custom، 216 Dummy / 46 Shader targets**. سلامة 29213 ملف YAML/meta مؤكدة، 0 broken؛ Artifact ID 14186801044. لا تقيس 72.5% كنسبة كل الرسوم.
- المهمة التالية `NEXT23`: [43774524669](https://github.com/alwansan/raf/actions/runs/43774524669) يثبت 58 مرحلة مصدر، [43774787696](https://github.com/alwansan/raf/actions/runs/43774787696) **SUCCESS** Unity Vulkan 33 route [8,13,8,4] في مشروع معزول. المطلوب: مثبت مصدر SHA + owner/PathID→export trace + جرد post14 216/46 + جرد post15 فعلي وحماية 29213 ملف؛ لا تُسجل 193 افتراضياً.
- `P08` FireAlpha: [43773481136](https://github.com/alwansan/raf/actions/runs/43773481136) و[43773517218](https://github.com/alwansan/raf/actions/runs/43773517218) فشل اختبار real؛ [43773517246](https://github.com/alwansan/raf/actions/runs/43773517246) اختبار صناعي ناجح فقط؛ local PPtr type0 ما زال مفتوحاً.
- `G0-G6` **غير مغلقة**: أكمل الجرد/النار/الماء FFT وKernel6 وTexture GUID/Mips/PostFX/TMP وباقي 216 مادة Dummy، ولا XAPK حتى إغلاق موارد الاستعادة.

## دفعة تنفيذ NEXT23 وFireAlpha — 16 نوفمبر 2026

- تأكدت نتيجة [43777739448](https://github.com/alwansan/raf/actions/runs/43777739448) **SUCCESS**؛ job `133007783009` نجح في فحص `py_compile` واختبارات `test_gt_install_next23_original_shader48.py` و`test_gt_install_next30_original_shader48.py`. هذا **دليل اختبارات صناعية فقط** وليس تثبيتاً على GUID في التصدير الكامل؛ آخر رقم فعلي **216 Dummy / 46 Shader targets**.


- فحص مبكر مستقل جديد للمثبت `raft-gt-next23-installer-static-gate.yml`: [43777739448](https://github.com/alwansan/raf/actions/runs/43777739448)، وليس اختبار Full-Export أو Vulkan نفسه.\n\n

- كود الاستعادة: `scripts/gt_install_next23_original_shader48.py`، اختبار `tests/test_gt_install_next23_original_shader48.py`، وربط `raft-gt-original-export-smoke.yml` على commit [5d44b41](https://github.com/alwansan/raf/commit/5d44b41fb3f94556122ca073f74061e0cf9e687b) ثم اختبار مبكر في [ae503180](https://github.com/alwansan/raf/commit/ae503180c3238fcb359dd89e684be8353abc2b02). [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) قيد التنفيذ من snapshot أولي؛ [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) أحدث snapshot بحماية الاختبار وكان pending عند التوثيق. لا تقبل post15 إلا بجرد صادر **حقيقي** وMaterial/meta SHA.
- الناتج المستهدف في **CI فقط**: 593 non-Dummy و193 Dummy و45 targets؛ الأعداد المثبتة حالياً: **570 non-Dummy و216 Dummy و46 targets**، تغطية 72.5% من مواد Custom فقط. حارس strict 29,213 ملفات unchanged، صفر broken؛ لا XAPK.
- كود FireAlpha يميز direct trace لكل Texture2D وبين 2 external material GUID وlocal type0 مجهول؛ لا اختلاق GUID للمحلي. Static [43777398225](https://github.com/alwansan/raf/actions/runs/43777398225) SUCCESS، real [43777398215](https://github.com/alwansan/raf/actions/runs/43777398215) قيد التنفيذ و[43777415610](https://github.com/alwansan/raf/actions/runs/43777415610) pending. المطلوب نتيجة real ثم التحقق من Alpha وImporter وأصل الـtype0.
- ممر العمل التالي: عند فشل CI حدد أول failing step ثم أصلح أصالة المصدر أو الربط، واحفظ السجل، وواصل Shader48 الباقية وماء FFT/Spectrum/Foam/Depth/Kernel6. لا تغلق G0–G6.

## مرحلة GT الجديدة — 16 نوفمبر / نتائج FireAlpha الواقعية وLocal type0

- [43777398215](https://github.com/alwansan/raf/actions/runs/43777398215) **SUCCESS real same-export**: 3 original SHA Texture2D، 5 Materials/10 TexEnv، 2 external TextureImporter images alpha decoded (1 opaque و1 شفافة جزئياً/كلياً)، و1 original local type0 غير مثبت؛ AlphaSource/Mipmap metadata للاثنتين مفقود، لا استنتاج أن النار صارت صحيحة.
- إضافة `classify_original_local_texture_trace` (commit `caa2a26`) للتحقق من نوع وfileID وGUID المرجع المحلي مباشرةً مقابل `Texture2D28` source owner/PathID داخل نفس export trace، دون تغيير الـGUID أو الصورة. المصدر/unit [43778269494](https://github.com/alwansan/raf/actions/runs/43778269494) **SUCCESS**، real [43778269514](https://github.com/alwansan/raf/actions/runs/43778269514) **pending** وقت آخر تحقق.
- NEXT23 full ZIP2 [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) in_progress و[43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) pending؛ الأعداد المثبتة **570/786 non-Dummy، 216 Dummy / 46 targets**. يجب قراءة post15 audit + حفظ SHA لـ29213 قبل تحسين الرقم.
- استعادة كل موارد الماء وFFT/kernel6 والرسوم والمجسمات والظلال G0-G6، بدون XAPK والأنيميشن مؤجل.

## دفعة مصدر Shader48 التالية — 16 نوفمبر 2026

- **[43779089456](https://github.com/alwansan/raf/actions/runs/43779089456) SUCCESS**: 82 مصدر SHA أصلي و165 Shader48، موصول بجرد post14 الحقيقي **216 Dummy** على 46 targets. أعلى 16 وزن Material: [23,23,18,17,15,11,10,10,7,7,6,5,5,5,4,4]. شيدر 23 المرتبط بـ1156 route/134 برنامج D3D11 غير شيدر NEXT23 الذي يملك 33 route/58 برنامج؛ NEXT18 يمتلك 4 Pass/33 route/58 برنامج، NEXT17 يمتلك 3 Pass/23 route/43 برنامج؛ دليل مصدر فقط، لا Unity ولا GUID.
- طورت `scripts/gt_translate_next_remaining_18_shader48.py` و`tests/test_gt_translate_next_remaining_18_shader48.py` لفحص SHA واختيار اسم مصدر فريد لثماني عشرة مادة ضمن post14 216/46، ثم ترجمة 58 برنامج D3D11 إلى Vulkan11 HLSL ومراجعة 33 keyword pairs و66 compiled source entrypoints. بدأت [43779460803](https://github.com/alwansan/raf/actions/runs/43779460803) **SOURCE-only**؛ لا تقبل نجاحة حتى يختم CI، وبعدها يلزم Unity Vulkan منفصل وsame-export original GUID.
- FireAlpha [43777398215](https://github.com/alwansan/raf/actions/runs/43777398215) real partial SUCCESS: 2 PNG الخارجية alpha-decoded وlocal type0 الثالثة غير مثبتة. أضفت top-mip source read-only decoder لـSHA الأصلي: static [43778717524](https://github.com/alwansan/raf/actions/runs/43778717524) PASS؛ real [43778717548](https://github.com/alwansan/raf/actions/runs/43778717548) in progress. لا صورة هاتف. بعض real runs المتكررة أُلغيت وهي pending لصالح أحدث واحدة، فلا تستنتج FAIL للمصدر من status CANCELLED.
- NEXT23 full [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) in progress، [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) pending؛ last accepted **570/786 non-Dummy و216 Dummy / 46**. يجب audit post15 الحقيقي قبل أي تحديث للعداد. الماء/FFT/kernel6 والظلال/الـPostFX وG0-G6 مفتوحة، لا XAPK.

## دفعة جديدة: FireAlpha original local trace/source pixels وNEXT18 Range — 16 نوفمبر

- FireAlpha [43778717548](https://github.com/alwansan/raf/actions/runs/43778717548) **SUCCESS real**: original `local type0` ظهر كـTexture2D28 في same-export trace بهوية PPtr مطابقة، وفُكّت صورة top mip الأصلية وفيها Alpha شفاف/جزئي؛ الصور الخارجية 2 Alpha decoded، والثالثة ليست مثبتة كصورة خارجية، ولا يوجد original↔exported pixel equality أو GPU/Adreno visual proof. Artifact 14187855918.
- NEXT18 [43779460803](https://github.com/alwansan/raf/actions/runs/43779460803) FAILED عند `restore_authentic_source_property_contract` بسبب شرط Range (3/1) من Next23. لكن SOURCE 58/58 D3D11→Vulkan roundtrip و66 compiled stages و33 routes/8 orphan VS نجحت. أصلحت strict Range حسب بيانات SHA الأصلية لا العدد المنسوخ من شيدر آخر، فحوص [43779759999](https://github.com/alwansan/raf/actions/runs/43779759999) و[43779784096](https://github.com/alwansan/raf/actions/runs/43779784096) لم تنتهِ عند التوثيق. لا Unity/Shader GUID بعد.
- NEXT23 [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) يتقدم في isolated Unity داخل same-export workflow، [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) pending. العدد المثبت post14 **570/786 non-Dummy، 216 Dummy / 46**، G0–G6 مفتوحة وXAPK ممنوع.
- NEXT بعد المصدر الصحيح: Next18 isolated Unity bundle ثم original GUID install بعد قبول post15 الحي، مع مواصلة Spectrum/Foam/Depth/FFT/Kernel6.

## GT — NEXT18 source accepted / NEXT17 source and Unity batch — 16 نوفمبر

- SOURCE NEXT18 [43779759999](https://github.com/alwansan/raf/actions/runs/43779759999) **SUCCESS**: 58/58 DXBC→Vulkan/HLSL، 33 VSFS keyword routes/[8,13,8,4]، ShaderLab 4pass composed، 66 entrypoints compiled، 15 خصائص منها 7 Range أصلية و0 out-of-range؛ 74 parameter records، 1024 CB offsets، 338 sampler/texture mapping، 228 varyings. لا Unity/GUID حتى إنهاء CI.
- isolated Unity NEXT18 [43780123319](https://github.com/alwansan/raf/actions/runs/43780123319) FAILED قبل jobs بسبب split newline في YAML `printf`؛ أصلحته في commit `a8d7b001`، [43780219002](https://github.com/alwansan/raf/actions/runs/43780219002) ينفّذ Unity Android Vulkan الآن.
- SOURCE NEXT17 بدأ [43780491219](https://github.com/alwansan/raf/actions/runs/43780491219): 17 Material، 3 Pass، 23 VSFS و8 orphan VS، 43 original D3D11، 46 target source compile entrypoints؛ مترجم/اختبار/workflow جديد مستقل، لا قبول برنامج أو Unity حتى PASS.
- NEXT23 full [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) مستمر، [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) pending. آخر MATERIAL count **216 Dummy/46** و570/786 Custom غير Dummy. Fire source local alpha exact trace [43778717548](https://github.com/alwansan/raf/actions/runs/43778717548) SUCCESS لكن external image لـlocal غير مثبت وAdreno visual مفتوح. لا XAPK.

## NEXT18 Unity accepted / NEXT17 CI rewire — 16 نوفمبر 2026

- [43780219002](https://github.com/alwansan/raf/actions/runs/43780219002) **SUCCESS**: original next18 source 58/58 D3D11/HLSL/Vulkan + isolated Unity 2021.3.45f2 Android Vulkan 4 Pass، 33 VSFS [8,13,8,4] serialized AssetBundle (0 shader errors، SHA matched). Artifact 14188102481. NEXT18 *ليس مثبتاً على GUID الأصلي* ولم يحسب ضمن 216 Dummy؛ بعد NEXT23 same-export acceptance، جهّز installer لمصدر NEXT18 بعد post15 verified.
- [43780491219](https://github.com/alwansan/raf/actions/runs/43780491219) **FAILED tooling**: workflow NEXT17 استدعى source NEXT18 وtest NEXT18 خطأ، وفي source NEXT17 guard 58 بدل 43. أصلحته `bd9c59d` و`c855514`، وإعادة الاختبار [43780876983](https://github.com/alwansan/raf/actions/runs/43780876983) قيد التنفيذ. متطلبات NEXT17 SOURCE: 17 Material، 3 Pass، 23 VSFS، 43 genuine D3D11، exact SHA. لا تخترع نتيجة.
- لا تغيّر العدد المثبت `570/786 non-Dummy Custom, 216 Dummy/46 targets` حتى نجاح same-export post15 بعد NEXT23. ماء FFT/kernel6/foam/depth/ظلال/نار/G0-G6 مفتوحة. بدون XAPK.

## GT 16 نوفمبر — تجهيز next18 same-export installer وعودة next17

- [43780219002](https://github.com/alwansan/raf/actions/runs/43780219002) NEXT18 Unity 2021 Android Vulkan SUCCESS، original 58/58 SOURCE و33 serialized VSFS routes [8,13,8,4], 0 errors. أعددت installer original-GUID next18 (script `scripts/gt_install_next18_original_shader48.py`) مع source identity SHA and exact receipt؛ [43781139286](https://github.com/alwansan/raf/actions/runs/43781139286) **SUCCESS static synthetic only**. لا يُسمح بتثبيته قبل جرد post15 real بعد NEXT23 (593 non-Dummy، 193 Dummy/45 targets شروط متوقعة فقط).
- [43777150940](https://github.com/alwansan/raf/actions/runs/43777150940) **FAILED** synthetic old fixture بعد مراحل Unity الثقيلة؛ أعيد التشغيل بتصحيح test fixture على [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) وهو in_progress full ZIP2 export. لا تحسب NEXT23 حتى full post15 GUID/meta audit.
- [43780876983](https://github.com/alwansan/raf/actions/runs/43780876983) NEXT17 **FAILED** synthetic no-17-target assertion data mistake؛ fixture corrected adbbe8b9، source CI [43781304391](https://github.com/alwansan/raf/actions/runs/43781304391) يترجم الآن SHA-original 43 D3D11/3Pass/23 VSFS.
- NEXT: read CI outcomes، accept real code only؛ water/FFT/kernel6 and fire original/export visual parity outstanding. no XAPK.

## GT — NEXT17 source success and Unity CI started, 16 نوفمبر

- [43781304391](https://github.com/alwansan/raf/actions/runs/43781304391) **SUCCESS SOURCE**: one SHA-verified original Shader48 associated 17 Custom Dummy Material documents; 43/43 D3D11 genuine program stages Vulkan1.1 HLSL validated, 3 passes 23 VS/FS routes [8,13,2], 8 orphan VS, 46 shader stage entrypoints, 15 source ShaderLab properties / 6 Range, 901 CB offsets/338 TextureSampler bindings/176 varyings. Artifact 14188333139. Not Unity/same-export/Adreno proof.
- New isolated UNITY Android Vulkan validator `android-port/Experiments/GT/Editor/Next17ShaderValidation.cs` + `raft-gt-next17-original-shader-unity.yml`, source-authentic `--next17` 3-Pass Vulkan serialized verifier. Initial [43781774987](https://github.com/alwansan/raf/actions/runs/43781774987) FAILED at quality guard due transcription 686 vs authentic 786 custom, fixed commit 01cb0801, replacement [43781873039](https://github.com/alwansan/raf/actions/runs/43781873039) running. Confirm unity stage before acceptance; then only same-export GUID after baseline.
- NEXT23 same-export [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) in progress; NEXT18 original Unity [43780219002](https://github.com/alwansan/raf/actions/runs/43780219002) SUCCESS but not GUID installed. Counts remain 570/786 Custom non-Dummy, 216 Dummy/46 GUID targets, 29213 YAML/meta unchanged. No XAPK.

## GT — تحقق NEXT17 Unity وNEXT15/11 SOURCE — 16 نوفمبر

- [43782074242](https://github.com/alwansan/raf/actions/runs/43782074242) **SUCCESS Unity**: next17 3 Pass ForwardBase/ForwardAdd/ShadowCaster، 23 registered routes [8,13,2] VSFS فعلياً في Vulkan serialized bundle و0 Unity errors، SHA candidate matched. Artifact 14189140548. لا تثبيت same-export GUID.
- [43782323454](https://github.com/alwansan/raf/actions/runs/43782323454) **SUCCESS SOURCE next15**: 58/58 original D3D11→Vulkan11، 33 routes [8,13,8,4]، 66 compiled stages؛ 23 original properties/12 Range، 1607 CB offsets؛ artifact 14188699030. [43782328731](https://github.com/alwansan/raf/actions/runs/43782328731) **SUCCESS SOURCE next11**: 58/58 programs، 33 routes، 9 properties/0 Range، 828 CB offsets؛ artifact 14187964353. لا GUID أو هاتف proof.
- بدأت Unity isolated [43782657334](https://github.com/alwansan/raf/actions/runs/43782657334) NEXT15 و[43782661831](https://github.com/alwansan/raf/actions/runs/43782661831) NEXT11، عند نهاية الاختبارات اطلب serialized VSFS وSHA و0 compiler errors. إذا نجحا، جهّز installer strictly guarded based on real same-export material state.
- NEXT23 [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) full ZIP2 exporter لا يزال مطلوباً لإثبات post15، بعده NEXT18/17/15/11 SOURCE+UNITY إلى original Shader GUID على دفعات مع recount Material. آخر رقم **570/786 non-Dummy، 216 Dummy/46 targets**، 29213 meta/YAML preserved، G0–G6 مفتوحة، no XAPK.

## GT — دفعة تثبيت أدلة NEXT15/NEXT11 واستعداد دمج GUID الأصلي، 16 نوفمبر

- NEXT15 [43782657334](https://github.com/alwansan/raf/actions/runs/43782657334) **SUCCESS SOURCE+ISOLATED UNITY** مع مصدر [43782323454](https://github.com/alwansan/raf/actions/runs/43782323454): Unity Android Vulkan 4 Pass، 33 VSFS routes [8,13,8,4]، 0 compiler errors، source SHA256 27064d720e10037a2697426081d6030d234018f42bb53a0e643d5a22435cd7b8، Artifact 14189580629.
- NEXT11 [43782661831](https://github.com/alwansan/raf/actions/runs/43782661831) **SUCCESS SOURCE+ISOLATED UNITY** مع مصدر [43782328731](https://github.com/alwansan/raf/actions/runs/43782328731): 4 Pass و33 routes و0 errors، SHA256 5732a11c9f3125709396ba3b6324940411adacddcc7ba1a0953d7183b797ee0b، Artifact 14189086879. NEXT18/17 سبق تأكيد SOURCE+UNITY؛ هذه **مجموعة 61 مستند Material مرشح، ولم تُدمج**.
- شُيّدت أدوات تثبيت strict original Shader GUID لـNEXT17/15/11؛ [43784558673](https://github.com/alwansan/raf/actions/runs/43784558673) SUCCESS لـ9/9 اختبارات أمان صناعية (SHA وروابط Material source+same-export، حفظ .meta ورفض تغيير أي Shader ليس Dummy، جودة Material census). الأرقام المرحلية الافتراضية المحتملة، **ليست نتائج**: قبل NEXT18=193 Dummy/45 targets؛ قبل NEXT17=175/44؛ قبل NEXT15=158/43؛ قبل NEXT11=143/42. راجعها مع كل تصدير حقيقي، ولا تجاوز أبداً أي اختلاف.
- NEXT23 [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) لا يزال full real export/Unity قيد التنفيذ؛ لا تعطل تشغيله أو تستعمل Snapshot مختلف. **الجرد الحي المؤكد هو 570/786 Custom non-Dummy و216 Dummy/46 GUID، 29213 meta/YAML unchanged**؛ M4/G0–G6 مفتوحة. خطة العمل: قبول/fix NEXT23، تثبيت original GUID بالترتيب الموثق وإعادة recensus، ثم العودة إلى Water Spectrum/Foam/Depth وFFT/kernel6 وFire image/device parity. No XAPK/animation yet.

## GT — 16 نوفمبر: NEXT23 same-export genuine PASS وNEXT18 real export launch

- **[43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) SUCCESS** من المصدر الأصلي ZIP2 الكامل: تم تثبيت NEXT23 على GUID التصدير الحقيقي، وأصبح الجرد المثبت **593/786 Custom Material non-Dummy و193 Dummy/45 Shader GUID targets**، 0 broken، **29213 ملف Material/meta/YAML SHA intact**. هذه تغطية Custom Materials بنسبة 75.45% فقط وليست كل رسوميات Raft أو جهاز Adreno.
- SOURCE+ISOLATED UNITY مكتملة لستة Shader48 أصلية مرشحة غير مثبتة: NEXT18 43779759999/43780219002، NEXT17 43781304391/43782074242، NEXT15 43782323454/43782657334، NEXT11 43782328731/43782661831، NEXT10p33 43785114809/43785362318 (58/33)، NEXT10p31 43785119657/43785367029 (55/31). NEXT10p33/31 لهما اسمان وPathIDs أصلية مختلفة حتى لو يرتبط كلاهما بـ10 Materials؛ لا تدمجهما.
- أضفت/شغّلت full pipeline `.github/workflows/raft-gt-next18-original-full-export.yml` [43786161961](https://github.com/alwansan/raf/actions/runs/43786161961): نفس ZIP2 source، 15 Shader GUID مستعادة، ثم NEXT18 original GUID، audit post16 **611 non-Dummy، 175 Dummy/44 targets = شرط متوقع فقط لا يقبل بلا CI**. لا APK. اختبارات Source-free لبقية installers [43784558673](https://github.com/alwansan/raf/actions/runs/43784558673) 9/9 PASS، NEXT10 pair [43785949219](https://github.com/alwansan/raf/actions/runs/43785949219) 6/6 PASS.
- NEXT: اقرأ نتيجة 43786161961؛ إن نجح أجرِ original GUID installs للمرشحين بالترتيب وmaterial SHA recensus بعد كل واحد؛ بعدها ماء Spectrum/Foam/Depth/FFT/kernel6 وFire texture blend/Adreno pixel parity وG0–G6. لا XAPK حتى اكتمال الموارد، الأنيميشن مؤجل.

## GT — تحديث 16 نوفمبر: فصل SOURCE عن تثبيت NEXT18 وفتح NEXT17 real full export

- جرد Material الحقيقي بعد NEXT23 [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111): **593/786 Custom non-Dummy, 193 Dummy/45 target GUID, 29,213 original Material/meta/YAML SHA preserved**, 0 broken. Source/isolated Unity for six other Shader48 targets accepted, but **original export installs pending**.
- Discovered **NEXT18 original source translator explicitly checks post14 216 Dummy/46**, even when future original GUID installer checks **post15 193 Dummy/45**. Fixed workflow source `--quality` only (commit `75088aec1379c6baa90276ee0bffc570b30b06d4`), without changing installer gate or original SHA. Old [43786161961](https://github.com/alwansan/raf/actions/runs/43786161961) remains in progress on old SHA and may fail source; corrected [43787527334](https://github.com/alwansan/raf/actions/runs/43787527334) pending. Never claim 611/175/44 before completed real audit.
- Staged NEW `.github/workflows/raft-gt-next17-original-full-export.yml` commit `0cfea84897c2bb0f179ae69dfed5c64c8bacf2c3`, run [43787809110](https://github.com/alwansan/raf/actions/runs/43787809110) active. The workflow replays full ZIP2, all previous native GUID restorations, validates NEXT18 post16 real `611 non-Dummy/175 Dummy/44`, then next17 source 43/43 genuine D3D11 and 3Pass/23 VSFS [8,13,2], isolated Unity Android Vulkan, GUID owner/PathID same export, final post17 audit `628 non-Dummy/158 Dummy/43` as *expected strict condition only*, all 29,213 YAML/meta SHA unchanged. NO APK.
- Next check all three CI jobs for actual outcomes; fix first failure only (e.g. old source quality vs new expected), preserve branch/ZIP2. Then continue NEXT15/11/10p33/10p31 sequential same-export with proof. Water FFT/kernel6, Foam/Depth, Fire original texture alpha, Shadows, G0-G6 remain unfinished; animation deferred, XAPK after complete restoration.

## GT — NEXT7p11/NEXT7p33 real SHA source restorations and Unity trials, 16 نوفمبر

- [43788590820](https://github.com/alwansan/raf/actions/runs/43788590820) NEXT7p33 **SUCCESS SOURCE** original 7-Material Shader48, (4 Pass,33 VSFS/8 orphan VS/58 original D3D11), all 58 Vulkan1.1 valid, 66 source stage compiles, 9 source properties/0 Range, [8,13,8,4] real routes; artifact 14190883438. Unity [43789192895](https://github.com/alwansan/raf/actions/runs/43789192895) running, no acceptance until serialized bundle pass.
- NEXT7p11 from 82 SHA owners (3Pass,11 VSFS,2 orphan VS/22 D3D11) first CI [43788585885](https://github.com/alwansan/raf/actions/runs/43788585885) failed compose due generic allowlist not recognizing [4,5,2] and second [43789088799](https://github.com/alwansan/raf/actions/runs/43789088799) completed source but failed inherited 31-VSFS workflow assertion. Added **source-derived original m_State.m_Tags LightMode** proof and no heuristic fallback in gt_original_921_shaderlab.py commit 180b5ee7, fixed workflow assertion 3f585052. [43789264382](https://github.com/alwansan/raf/actions/runs/43789264382) **SUCCESS SOURCE** real original 22/22 D3D11, [4,5,2]/3pass ShaderLab/22 entries, 12 original properties/4 Range; artifact 14190954229. Unity [43789424745](https://github.com/alwansan/raf/actions/runs/43789424745) running with strict --next7p11 serialized Vulkan profile.
- Material same-export baseline STILL verified [43777283111](https://github.com/alwansan/raf/actions/runs/43777283111) **593/786 Custom non-Dummy, 193 Dummy/45 targets**, 29213 YAML/meta unchanged. Source-only 7-Material candidates are not installed. NEXT18 old 43786161961 / corrected 43787527334 / NEXT17 full 43787809110 pending final audit. Continue Unity first, then next ORIGINAL same-export installs; water FFT/kernel6/Fire/Depth/Foam G0–G6, animation deferred, NO XAPK.

## GT — isolated Unity PASS for both authentic seven-material Shader48 — 16 نوفمبر

- NEXT7p11 source [43789264382](https://github.com/alwansan/raf/actions/runs/43789264382) **SUCCESS** 22/22 original D3D11/3 Pass/11 VSFS [4,5,2] 2 orphan VS, 12 properties/4 Range. After source-owned m_State.m_Tags LightMode bridge 180b5ee7 and fixed stale CI assert 3f585052, isolated Unity [43789424745](https://github.com/alwansan/raf/actions/runs/43789424745) **SUCCESS** 2021.3.45f2 Android Vulkan 3 Pass, 11 routes, 0 shader errors, independently serialized VS/FS [4,5,2] candidate SHA e780a47b69fd7ed438d9f56b2ec5d44ef765fad44aa36643e71288d70567d4e3; artifact 14192041314.
- NEXT7p33 source [43788590820](https://github.com/alwansan/raf/actions/runs/43788590820) **SUCCESS** 58/58 D3D11, 4 Pass 33 VSFS [8,13,8,4], 9 properties/0 Range, and isolated Unity [43789192895](https://github.com/alwansan/raf/actions/runs/43789192895) **SUCCESS**, zero shader errors, serialized [8,13,8,4], candidate SHA b1f226826ea1c5fb3c805a13f0d03524d0ac34a581697d86f5a4084649301032; artifact 14191093809.
- **8 distinct SHA-original Shader48 groups 18/17/15/11/10p33/10p31/7p11/7p33 (95 Custom Material documents) are SOURCE+ISOLATED UNITY verified, NOT original GUID installed**. Next real material census must come from original full-export 43786161961 old, 43787527334 fixed, 43787809110 next17: currently accepted post15 **593 Custom non-Dummy /193 Dummy/45 GUID targets**, 29,213 source meta/YAML intact. Continue same-instance integration and source water FFT/kernel6/fire first. G0-G6 open; no XAPK.
