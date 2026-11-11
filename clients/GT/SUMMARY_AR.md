# ملخص تقدم GT للمالك

**آخر تحديث: 12 نوفمبر 2026 — GT / chat / دفعتا الجرد الأولى والثانية.** تمت قراءة 82/82 حاوية Unity أصلية مطلوبة للجرد (40 `level` + 42 `.assets`) والتحقق من SHA256 لكل منها ثم استخراج هويات الأصول الرسومية. **هذه نتائج المصدر الأصلي، وليست بعد نسبة دمج داخل مشروع Unity Android أو إثبات عرض على الهاتف.**

> **قرار المالك 12 نوفمبر 2026 — ZIP2 فقط، من دون Git LFS:** يستعيد GT جميع الحمولات من [فرع `zip2`](https://github.com/alwansan/raf/tree/zip2) بعد تثبيت commit، وإعادة تجميع الأجزاء `part-00000`...، والتحقق من SHA256 والحجم الكامل قبل استخدامها. لا تستخدم أدوات جلب LFS ولا fallback عليها. المخرجات المؤقتة مفصولة عن شجرة المصدر وملفات .meta/GUID. هذا القرار محفوظ في [MEMORY.md](MEMORY.md)، و[RESTORE_AR.md](RESTORE_AR.md)، و[state.json](state.json).

**دفعة GT 3 — استعادة مزوّد الرسوميات ZIP2 بدون LFS:** نجحت [GitHub Actions 43117743780](https://github.com/alwansan/raf/actions/runs/43117743780) في إعادة تجميع ملف Stream ومشهد split من SHA ZIP2 المثبت، وإثبات تطابق SHA256 والحجم لمجموع **70,566,428 بايت** من ملفين. [Artifact إثبات المصدر 13899122924](https://github.com/alwansan/raf/actions/runs/43117743780/artifacts/13899122924). أداة اختيار واستعادة جميع الأنواع `scripts/gt_zip2_payloads.py` واختباراتها `tests/test_gt_zip2_payloads.py` جاهزة لاستعادة بقية .resS/.resource في المسار الخاص بـGT. نجاح استعادة الملف ليس نجاح Render/Android.

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
