# ملخص تقدم GT للمالك

**آخر تحديث: 12 نوفمبر 2026 — GT / chat / دفعتا الجرد الأولى والثانية.** تمت قراءة 82/82 حاوية Unity أصلية مطلوبة للجرد (40 `level` + 42 `.assets`) والتحقق من SHA256 لكل منها ثم استخراج هويات الأصول الرسومية. **هذه نتائج المصدر الأصلي، وليست بعد نسبة دمج داخل مشروع Unity Android أو إثبات عرض على الهاتف.**

> **قرار المالك 12 نوفمبر 2026 — ZIP2 فقط، من دون Git LFS:** يستعيد GT جميع الحمولات من [فرع `zip2`](https://github.com/alwansan/raf/tree/zip2) بعد تثبيت commit، وإعادة تجميع الأجزاء `part-00000`...، والتحقق من SHA256 والحجم الكامل قبل استخدامها. لا تستخدم أدوات جلب LFS ولا fallback عليها. المخرجات المؤقتة مفصولة عن شجرة المصدر وملفات .meta/GUID. هذا القرار محفوظ في [MEMORY.md](MEMORY.md)، و[RESTORE_AR.md](RESTORE_AR.md)، و[state.json](state.json).

**دفعة GT 3 — استعادة مزوّد الرسوميات ZIP2 بدون LFS:** نجحت [GitHub Actions 43117743780](https://github.com/alwansan/raf/actions/runs/43117743780) في إعادة تجميع ملف Stream ومشهد split من SHA ZIP2 المثبت، وإثبات تطابق SHA256 والحجم لمجموع **70,566,428 بايت** من ملفين. [Artifact إثبات المصدر 13899122924](https://github.com/alwansan/raf/actions/runs/43117743780/artifacts/13899122924). أداة اختيار واستعادة جميع الأنواع `scripts/gt_zip2_payloads.py` واختباراتها `tests/test_gt_zip2_payloads.py` جاهزة لاستعادة بقية .resS/.resource في المسار الخاص بـGT. نجاح استعادة الملف ليس نجاح Render/Android.

**دفعة GT 4 — حل روابط الـRenderer→Material الأصلية بالكامل:** نجح [GitHub Actions 43118214676](https://github.com/alwansan/raf/actions/runs/43118214676) (الاختبارات الاصطناعية وفحص المصدر) في قراءة مراجع الـMaterial من جميع 82 حاوية أصلية موثقة، وربطها بهوية `(container, path_id, Material)` الدقيقة. ثُبّتت **195,174 خانة مادة**، منها **194,293 مرجعاً غير فارغ وصل إلى كائن Material صحيح** و**881 null أصلياً**؛ لا يوجد مرجع غير فارغ معلّق أو يشير إلى صنف خاطئ. **1,351 Material فريدة مشار إليها** من أصل **1,556 Material object**، ولا يعني الفرق أن باقي المواد غير مستخدمة بطرق أخرى. [دليل المطابقة 13899108653](https://github.com/alwansan/raf/actions/runs/43118214676/artifacts/13899108653) و[سجل GT](evidence/20261112_original_material_link_graph.json). **لم تُثبت بعد مطابقة الـGUID وMaterial pointer بين المصدر وExportedProject، ولا العرض على الهاتف.**

**دفعة GT 5 — روابط Mesh/Texture التي تحدد الألوان والمجسمات:** نجح [GitHub Actions 43120209212](https://github.com/alwansan/raf/actions/runs/43120209212) في اختبار `scripts/gt_original_mesh_texture_graph.py` على **82/82 حاوية ZIP2 أصلية موثقة**؛ [Artifact 13900107915](https://github.com/alwansan/raf/actions/runs/43120209212/artifacts/13900107915) و[الدليل](evidence/20261112_original_mesh_texture_graph.json). **كل 4,583 مرجع Texture غير فارغ في 10,246 خانة Material قد وصل إلى صنف Texture أصلي صحيح**، مقابل **5,663 خانة فارغة أصلاً**. الأهداف المختلفة المشار إليها **3,373 Texture**، وUV scale/offset موجودة وصحيحة البنية في **10,246/10,246** موضع. **روابط Mesh:** 176,708 خانة `m_Mesh` (MeshFilter + SkinnedMeshRenderer)، منها **176,006 مرجعاً لمجسم أصلي من الملفات الـ82**، **474 مرجعاً خارجياً إلى موارد Unity المدمجة**، **228 null أصلياً**؛ **4,328 Mesh أصلية فريدة** مشار إليها مباشرةً. لم يكتشف الفحص أي نقص هدف أو صنف خاطئ؛ 474 مورد Unity المدمج تتطلب تحقق GUID/export مستقلاً ولا تعني أخطاء Asset. **هذه سلامة topology داخل المصدر، لا تحقق Material/Texture/Mesh داخل APK أو Unity Export.**

## GT — الاستعادة العملية الكاملة لموارد الرسوميات ودخول مسار بناء Raft

**ليست مراجعة ملفات فقط:** تمت إعادة تجميع **134/134 ملفاً أصلياً مطلوباً لمدخل تصدير الرسوميات من ZIP2، 7,532,909,297 بايت** إلى `Raft_Data` مؤقت فعلي، وفحص **SHA256 والحجم لكل أصل**، عبر [GitHub Actions 43124662931 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43124662931) ([Artifact 13902706287](https://github.com/alwansan/raf/actions/runs/43124662931/artifacts/13902706287)). تشمل 82 Unity serialized owners، و48 stream، وموارد Unity builtin الاثنين، و`globalgamemanagers` و`boot.config`. أداة `scripts/gt_zip2_export_resources.py` تدعم original plain/split وcache آمن وترفض المخالفات. أُثبتت جميع **4,050 Texture2D**: 3,948 Texture streams يمكن قراءة امتداداتها ضمن مصادر أصلية **5,932,309,293 بايت**، و102 inline/empty موجودة في الأصل. وكذلك مرت متطلبات Mesh stream metadata و9 ComputeShader objects عبر source scanner. [أدلة الاستعادة الكاملة](evidence/20261112_full_zip2_graphics_restoration.json).

قبل الدفعة الكاملة، نفّذت أدلة فعلية مستقلة: [43122665358 — PASS](https://github.com/alwansan/raf/actions/runs/43122665358) أعاد 5 أصول بحجم 656.6 MB، و[43123035437 — PASS](https://github.com/alwansan/raf/actions/runs/43123035437) أعاد 1.895 GB من `sharedassets0` وبياناته، وثبت الوصول إلى 557 Mesh stream و1,116 Texture stream. **هذه دفعات متداخلة ضمن الـ134؛ لا تُجمع أحجامها مع 7.533GB.**

**دمج برمجي في native build وليس ملف PDF أو خطة فقط:** `.github/workflows/raft-unity-editor-android-import.yml` يشغل مُستعيد ZIP2 الأصلي على مدخل `$RUNNER_TEMP/input/Raft_Data` الرسمي، يثبت الملفات مرتين، ثم يستعملها لإدخال AssetRipper وتدقيق الـTexture/Mesh/Compute وإحضار Mesh ranges من ملفات المصدر المحلية، بدل اعتماد LFS downloader السابق. نجاح الحارس [43125034578](https://github.com/alwansan/raf/actions/runs/43125034578). وأعيد أصل `MasterBank.bank` الصوتي **101,600,960 بايت** من ZIP2 ببصمة صحيحة في [43125353255 — PASS](https://github.com/alwansan/raf/actions/runs/43125353255)، مع إرسال الأصل المؤكد إلى أداة FMOD T5 الحالية دون Git LFS.

**تصدير AssetRipper الحقيقي تم بنجاح:** [43125542125 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43125542125) استعمل 134 ZIP2 original files + 151 managed source، وانتج **40 ملف Scene `.unity`، 1,536 `.mat`، 4,003 صور Texture، 8,372 `.asset`، و18,368 `.meta`**. اجتاز استيراد السكربتات `decompiled_script_export=true`, `unknown_backend_fallback=false`, `mono_structure_layout_mismatch_lines=0`. [Artifact 13902689523](https://github.com/alwansan/raf/actions/runs/43125542125/artifacts/13902689523). **العائق الحقيقي:** `verify_exported_material_texture_links` أعاد exit 2 على ExportedProject رغم success العام (الخطوة continue-on-error). إعادة تشغيل [43126735391](https://github.com/alwansan/raf/actions/runs/43126735391) مهيأة لتسجيل رمز المشكلة الآمن؛ واختبار GT التالي يضيف private Texture source→Export GUID trace ومطابقة B05 UV/slot مع المصدر وT3 shader program-quality، دون تغيير .meta. لا يُثبت نجاح التصدير صحة Pass/Vulkan/GLES/GPU والهاتف بعد؛ لا يوجد GT XAPK جديد، وقرار البناء الرسمي عند T5 وفق التصويت.

**المرحلة التالية دخلت استعادة ربط المواد الأصلية فعلياً:** أثبتت [43126735391](https://github.com/alwansan/raf/actions/runs/43126735391) أن العائق الأول في أداة `verify_exported_material_texture_links` هو **`empty_or_unrecognized_texenv`**: يصدّر AssetRipper خاصية `m_TexEnvs` كـYAML mapping، بينما B46 كان يفترض صيغة list فقط. أُصلح قارئ `scripts/verify_exported_material_texture_links.py` ليدعم الاثنين و`{}` مع رفض PPtr الضار، ونجح [43128041580](https://github.com/alwansan/raf/actions/runs/43128041580) بالاختبارات. وأثبت [43127697656 PASS](https://github.com/alwansan/raf/actions/runs/43127697656) **مطابقة دقيقة واقعية** لملفات Material وTexture GUID/UV لمصدر `sharedassets6.assets` من أصل ZIP2 إلى نفس جلسة AssetRipper بواسطة B05 مع `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE=1` (خاص GT فقط). أُضيفت أداة `scripts/gt_full_original_export_texenvs.py` لفحص **1,556 مادة أصلية من 82 حاوية**؛ [43128570586 synthetic PASS](https://github.com/alwansan/raf/actions/runs/43128570586)، [التحقق الواقعي 43128711194](https://github.com/alwansan/raf/actions/runs/43128711194) قيد القراءة.

**بداية مسار Shader الحقيقي:** فحص `t3_audit_exported_material_programs` على تصدير AssetRipper **الخام قبل مصلحات Shader** في [43127697656](https://github.com/alwansan/raf/actions/runs/43127697656) وجد **786 من 1536 مادة** تشير إلى Shader Dummy مميز، و**750 مادة builtin**، و**140 Shader file كلها تحمل علامة Dummy**؛ 64 هدف Shader فريد مستخدم ضمن 786 مادة. هذه إشارة لعائق Stage Restore Pass وليست قياساً لما بعد T1/T3، فلا تعلن فشل Vulkan/Android من RAW وحده.

## GT — نقل مواد Raft من المصدر إلى ExportedProject والاستعادة الأصلية لصفائف Texture2DArray

**انتهى الاختبار الكامل لمطابقة مواد المصدر قبل تحويل Android**: [CI 43132978685](https://github.com/alwansan/raf/actions/runs/43132978685) أثبت أن **1,536 مادة AssetRipper مصدّرة** احتفظت بـ**10,216 Texture property/UV slots** مقارنة بـ1,556 مادة Original في 82 container؛ منها **4,151 رابط داخلي Texture GUID متطابق تماماً** و**0 اختلاف UV** و**0 null→bound / bound→null** و**0 wrong internal target**. بقيت 416 رابط original external لم يثبت target match الخاص به؛ لا تعلن تحقق الهوية الكاملة. **28 استخداماً لمراجع ذات fileID غير Texture2D ليست مفقودة:** [43135341260](https://github.com/alwansan/raf/actions/runs/43135341260) ربطت المصدر ClassID187 بتسعة Texture2DArray مصدّرة بــ fileID18700000 وTextureImporter.textureShape=4.

**استعادة فعلية، وليس جرداً فقط:** من نسخ original ZIP2 المتحقق منها، [43136988092 PASS](https://github.com/alwansan/raf/actions/runs/43136988092) أعطى 9 Array بأبعاد 1024×1024 و11 mip؛ 50 طبقة BC3 bytes أصلية من أصل 52 طبقة منطقية، بحجم **69,906,400 بايت**، ومورد واحد 2-layer لم يخزن في أصل PC أي stream أو inline pixels. الأداة `scripts/gt_recover_original_array_layers.py` تجهز 8 raw compressed original arrays الحقيقية بالبايت إلى runner-private staging من ملفات .resS ذات SHA256 مثبتة، وتعمل قبل Unity Editor import، وترفض تصنيع البايتات المفقودة. اختبارات فساد المصدر والـGUID والـmips والأحجام [43138283249 PASS](https://github.com/alwansan/raf/actions/runs/43138283249). **الفحص الكامل الجديد** [43138326757](https://github.com/alwansan/raf/actions/runs/43138326757) كان جارياً حين كتب هذا التحديث؛ قبول الـ69.9MB على مسار الإنتاج لم يثبت بعد. **الخطوة المتبقية لإنهاء الـ9 Array:** التحقق من ترتيب طبقات BC3 ومراحل mip ثم إنشاء Unity Texture2DArray أصلي قابل للتحميل بنفس GUID وفي صيغة Adreno مدعومة، دون إنشاء بيانات للمورد الأصلي الفارغ. لا يوجد اختبار هاتف لهذه النقطة بعد.

**ترميم Shader vendor مع الحفاظ على أصل GUID:** أربعة Restorers TMP/PostFX histogram compute/Volumetric نُفّذت في [43135341260](https://github.com/alwansan/raf/actions/runs/43135341260)، لكنها اكتشفت نقل .meta أصلي واحد و3 ملفات جديدة؛ هذه عملية `EyeHistogram.asset→EyeHistogram.compute` المقصودة لا تعني فساد GUID. عدّل GT حارس `gt_test_vendor_shader_restoration` ليتطلب private backup مطابق بالأصل، GUID نفسه في .compute، 2 kernel، وعدم تغيير باقي الـ18,368 ملفات meta؛ synthetic [43138199883 PASS](https://github.com/alwansan/raf/actions/runs/43138199883). لا تُعلن خفض 786 Raw Dummy حتى يكتمل اختبار post-restorer الحقيقي.

## نقطة التثبيت والأدلة

- **مرجع ZIP2 الموثق:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385`؛ البيان الأصلي 366 ملفاً وحجم 7,789,295,609 بايت.
- **خط أساس فرع Android:** `cd96edc1ce0059b5737c017b707a8f79cb4da29d`؛ شجرة `Raft`: `f1c69f63f0ca76d090733f25d4dfaa9d82fa0387`.
- **مطابقة Git البنيوية:** 366/366 مساراً موجوداً، 344 ملفاً plain لها Git Blob SHA متطابق، 18 LFS pointer لها الأصل SHA256 والحجم المثبتان، و4 ملفات split تتطابق بالحجم فقط (بصمة محتواها لم تتحقق من هذه المطابقة البنيوية). [دليل البنية](evidence/20261112_original_container_identity.json).
- **مشاهد اللعبة الأربعون:** [GitHub Actions 43113418656 — PASS](https://github.com/alwansan/raf/actions/runs/43113418656) · [نتيجة أول نجاح 43113017547](https://github.com/alwansan/raf/actions/runs/43113017547).
- **جرد جميع مالكي الأصول المسلسلة الـ82:** [GitHub Actions 43114648901 — PASS](https://github.com/alwansan/raf/actions/runs/43114648901) · [Artifact 13897064222](https://github.com/alwansan/raf/actions/runs/43114648901/artifacts/13897064222). **819,595,355 بايت** من 82 حاوية أصلية موثقة بـSHA256، منها 5 حاويات احتاجت إعادة تجميع split. جرى استخلاص عدادات Mesh/Texture2D/Cubemap/Shader/Compute، وفحص كل 4,708 Mesh descriptor وكل 4,050 Texture2D format/color header بلا أخطاء فكّ معلنة. [دليل الدفعة](evidence/20261112_82_serialized_original_owners.json).
- **مواد وشيدرات المصدر:** أدوات W3 الموجودة أظهرت 1,556 Material و165 Shader objects، و77 هوية Shader مستهدفة بالمراجع و75 اسماً مختلفاً مشاراً إليه، مع 16 مرجعاً إلى engine transports. هذا جرد مرجعي وليس مرور Vulkan/GLES للـPass أو shader فعلي في Unity Android.

## الأعداد المثبتة من أصل ملفات Unity الـ82

| الفئة | العدد الأصلي | معنى العدد وحدوده |
|---|---:|---|
| جميع كائنات Unity المسلسلة | **1,209,137** | هوية `(container, path_id, type)`، لا يُقصد بها كائنات مرسومة |
| **Mesh** | **4,708** | أصل Mesh فريد بالهوية داخل 82 مالكاً، لا استعمالات Renderer |
| **Material** | **1,556** | كائنات مواد فريدة بالهوية |
| **Texture2D** | **4,050** | تم فكّ نوع الصيغة وColor Space لكل Texture2D |
| **Cubemap** | **30** | كائنات مكعبة فريدة |
| **Texture2DArray** | **9** | كائنات مصفوفات صور |
| **Shader** | **165** | كائنات Shader، وليس 165 Pass أو variant |
| **ComputeShader** | **9** | كائنات Compute، عدد kernels والتحويل/التشغيل لم يُثبت بعد |
| MeshRenderer | **176,432** | Components، لا Mesh فريدة |
| MeshFilter | **176,345** | Components |
| SkinnedMeshRenderer | **363** | Components |
| ParticleSystemRenderer | **2,141** | Components |
| Light / ReflectionProbe | **228 / 4** | Components |
| Material Slots في **40 مشهداً** | **191,845** | استعمالات Renderer فقط، لا Material فريدة |
| منها مراجع مادة خارجية | **191,116** | أهداف خارجية تتطلب حل هوية وربط export |
| منها Material null | **729** | مواضع صريحة بلا مادة |

**ملاحظة التغطية:** الـ82 تشمل 40 مشهداً و42 ملفاً من نوع `.assets` (بما فيها `resources.assets` و`globalgamemanagers.assets`). يوجد كذلك الملف `globalgamemanagers` غير المنتهي بـ`.assets`، والموارد المتدفقة `.resS` ومزودات `Resources`؛ لا يُحسب أنها فُحصت كأصل مستقل في جدول الـ82، ولا يعني عدّ رؤوس Texture/Mesh فحص البكسلات أو بيانات Stream الفعلية.

## حالة الاستعادة والدمج — لا تخلط بيانات الأصل مع بيانات الـAPK

| الفئة | الإجمالي المعروف من حاويات المصدر الـ82 | مستعاد داخل Export ومتحقق من عرض الأصل | مدمج في مشروع Android ومثبت | مثبت في بناء Android/هاتف |
|---|---:|---|---|---|
| Mesh أصلية | 4,708 | قيد المطابقة | غير محسوم | غير محسوم |
| Material أصلية | 1,556 | قيد المطابقة | غير محسوم | غير محسوم |
| Texture2D | 4,050 | رؤوسها مثبتة، بيانات الألوان/البكسلات قيد المطابقة | غير محسوم | غير محسوم |
| Cubemap / Texture2DArray | 30 / 9 | قيد المطابقة | غير محسوم | غير محسوم |
| Shader objects | 165 | رسوميات مرجع GFX-LAB ست عينات لا تثبت كل اللعبة | غير محسوم | غير محسوم |
| Pass / variants | غير محسوم | يحتاج تفكيك/ترجمة واختبار | غير محسوم | غير محسوم |
| ComputeShader objects | 9 | kernels والتشغيل الأصلي قيد التحقق | غير محسوم | غير محسوم |
| الظلال والمؤثرات | يحتاج ربط حالات الرسم والتأثيرات | قيد المقارنة | غير محسوم | غير محسوم |
| 40-scene Renderer→Material slots | 191,845 | فُحصت الروابط الأصلية فقط | غير محسوم | غير محسوم |

**نسبة جرد الحاويات المستهدفة: 82/82 = 100%.** نسبة استعادة الأصول في مشروع Android **لا يمكن تحديدها من هذا الفحص**. لا يُعاد تفسير 100% كدمج أو عرض سليم، ولا يُحسب 0 للمدمج لمجرد أن GT لم يثبت بعد الدمج السابق.

## الدفعات والاختبارات

1. **الدفعة 1 — source/scene inventory:** عزل وفحص 40 مشهداً مع Material slot PPtrs؛ فشل أول اختبار 43112757300 بسبب حد B03 على كل 100k كائن؛ عُزل التحليل إلى Renderer وMaterial، فنجح 43113017547 ثم 43113418656. صُححت كذلك تسمية مجاميع `distinct` عند تجميعها عبر المشاهد.
2. **الدفعة 2 — serialized owners:** إعادة تجميع 82 حاوية أصلية والتحقق من SHA256 دون تنزيل 7.79GB أو نقل أصول اللعبة إلى المستودع، وإعادة استخدام W2/W3 لجرد Material→Shader وTexture header؛ نجح 43114154912 ثم 43114648901 مع فحص كامل Mesh/Texture/Compute metadata.
3. **الدفعة التالية — التكامل الحقيقي:** مطابقة أصل 4,708 Mesh و1,556 Material و4,050 Texture و165 Shader و9 Compute مع الـAssetRipper Export الفعلي في `$RUNNER_TEMP/project/ExportedProject` ومسار `Raft Unity`، والتحقق من `.meta`/GUID وmaterial slots وsubmesh indices وUV/Normals/Tangents وtexture streams وshader bindings/pass/shadows. اختر عائلة ذات أثر كبير بعد المطابقة، ثبت استيرادها واختبارها في Unity، وبعدها فقط انقل إلى عمود «مدمج» مع SHA ودليل APK إن وُجد.

### أدوات إعادة الإنتاج

- [جرد المشاهد](../../scripts/gt_scene_graphics_inventory.py) · [اختباراته](../../tests/test_gt_scene_graphics_inventory.py)
- [إعادة تجميع 82 حاوية](../../scripts/gt_stage_serialized_owners.py) · [اختباراتها](../../tests/test_gt_stage_serialized_owners.py)
- [جرد كل الكائنات الرسومية ومعلوماتها](../../scripts/gt_serialized_graphics_counts.py) · [اختباراته](../../tests/test_gt_serialized_graphics_counts.py)
- [CI المشاهد](../../.github/workflows/raft-gt-scene-graphics-inventory.yml) · [CI الحاويات والمواد والشيدرات](../../.github/workflows/raft-gt-serialized-graphics-owners.yml)

حافظ على نتائج المختبر الأصلية (6 Mesh و7 Material slots) كاختبار ارتداد، ولا تعتبر نجاحها تعميماً أو إثبات Vulkan/Android الفعلي.
