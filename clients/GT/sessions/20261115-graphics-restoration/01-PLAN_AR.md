# خطة استكمال استعادة رسوم Raft Android

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
