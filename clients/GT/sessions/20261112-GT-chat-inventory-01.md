# GT / CHAT — جرد المصدر والمشاهد ثم بدء إعادة تجميع الحاويات

- **session_id**: `GT-20261112-0144-CHAT-01`
- **origin**: `chat`
- **agent**: `GT`
- **write_branch**: `feature/android-native-port`
- **source pin**: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- **project baseline**: `cd96edc1ce0059b5737c017b707a8f79cb4da29d`
- **scope**: جرد الأصالة، حاويات المصدر، Mesh/Renderer/Material الأصلية، والانتقال إلى مواد وشيدرات الحاويات الخارجية. لا تعديل أعمال T1–T5 ولا طلب Full XAPK.

## نتائج مؤكدة

1. بيان ZIP2: 366 ملفاً أصلياً بحجم 7,789,295,609 بايت. مطابقة كاملة لـ366 اسماً مع `Raft` في فرع Android؛ 344 plain ذات SHA Git blob متطابق، 18 مؤشراً LFS ذات SHA256/حجم أصلي متطابق، 4 split محفوظة بالحجم المعلن لكن دون حساب SHA256 للحمولة في هذه الدورة. التفاصيل في [الدليل البنيوي](../evidence/20261112_original_container_identity.json).
2. جرد `level0..level39`: عرّف وفحص 40/40 مشاهد من ZIP2 بعد فحص SHA256 أصلي لكل مشهد. 1,146,721 كائناً متسلسلاً و662 Mesh محلياً و176,189 Renderer و191,845 Material Slots منها 191,116 externals و729 null و27 Cubemap. **هذه ليست عدادات اللعبة كلها أو أعداد الدمج في Android.**
3. تشغيل [43112757300](https://github.com/alwansan/raf/actions/runs/43112757300) فشل: حد `analyze_scene` التاريخي 100k node كان مطبّقاً خطأً على كل كائنات المشهد، لا نطاق الـRenderer/Material. أُصلح بفلترة الرسم إلى Renderer+Material مع إبقاء عدّ جميع كائنات المصدر، ونجح [43113017547](https://github.com/alwansan/raf/actions/runs/43113017547). اختبار الرجوع [43113418656](https://github.com/alwansan/raf/actions/runs/43113418656) نجح بعد تصحيح اسم مجاميع `distinct` الخاصة بكل مشهد.
4. أنشئت أداة إعادة تجميع 82 حاوية Unity أصلية (`40 level` و`42 .assets`، بإجمالي 819,595,355 بايت، منها 5 split). التحقق بالـSHA256 إلزامي قبل أي قراءة، والحاويات تُنسخ إلى مرحلة عزل مؤقتة فقط؛ لا تنشر ملفات اللعبة في Artifacts. الاختبارات الاصطناعية للأداة نجحت في [43114154912](https://github.com/alwansan/raf/actions/runs/43114154912)، مع تشغيل الأصل الفعلي في تلك الدورة؛ راجع نتيجتها قبل نسبة نجاح الفحص.

## قرارات / قيود

- الملف `Raft` في الفرع أصل بيانات للـBuild، وليس Unity project مصدّراً بمشهد/Material/Shader+GUID متحقق على Android؛ لا تنقل الأعداد البنيوية إلى عمود مدمج أو مثبت في APK.
- معدلات استعمال Material تُعدّ على مستوى Slot، لا على مستوى Material فريدة. مؤشرات `m_FileID>0` غير محلولة إلى هوية Material حقيقية قبل قراءة الـ42 حاوية `.assets`.
- أنظمة shader/pass/Compute، ربط المجسمات والـUV/Normal/Tangent، والـShadowMap على هاتف Android ما زالت تحتاج دليل تكامل مستقل. معايرة GFX-LAB 6 Mesh و7 Slots منجزة سابقاً؛ ليست حصيلة GT للعبة.
- استخدم الأدوات القائمة `probe_w3_full_material_shader_inventory.py` و`probe_w2_fullgame_texture_colors.py` بعد Stage الموثق بدل بناء محللات مكررة. لا تطلق Unity/full APK ولا تغيّر أصوات T-team أو request files.
- احفظ جميع إصلاحات وأصول T1–T5 وملفات .meta/GUID ولا تستبدل فرع Raft بجذر ZIP2.

## النقطة التالية

1. افحص [43114154912](https://github.com/alwansan/raf/actions/runs/43114154912) وأول خطأ حقيقي أو عدد Material/Shader/Texture المثبت من أصالة جميع الـ82 owner. أصلح المشاكل في مسار GT أو أعد استخدام أدوات W2/W3 مع حدودها الأصلية.
2. أنشئ جدول هوية كائنات المصدر `(owner,pathID,type)` وجدول الاستعمالات `Renderer/slot` منفصلاً، وحل links `Material->Shader/Texture` إلى owners معتمدة.
3. قارِن مع مشروع Unity المصدّر بأدلة .meta/GUID وMaterial/Shader/mesh، اختر دفعة إصلاح صغيرة للدمج وأجرِ اختباراً أرخص من Full APK أولاً، ثم حدّث SUMMARY وstate والذاكرة وجلسة أخرى عند الإنجاز.
