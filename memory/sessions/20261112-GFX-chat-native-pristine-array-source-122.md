# GFX162 — إصلاح مدخل تدقيق صفائف الخامات

[43149622750](https://github.com/alwansan/raf/actions/runs/43149622750) فشل قبل Unity ومرحلة الماء. تحقق المصدر لـ134 ملفاً، ثم عدّل Mesh inliner بعض serialized owners داخل input/Raft_Data، ومنها resources.assets وsharedassets0.assets. يقرأ gt_repair_array_flipbook_importers المسار المعدل ويقارنه حرفياً مع manifest الأصلي، فرفض staged_owner_fingerprint_mismatch.

[التصحيح](../../gfxlab/patches/gfx162-pristine-array-source.patch) على لقطة native `1ceb252cb8b81ed69417aa3bf7e822055ca7831e`: يعيد تجهيز 82 serialized owner أصلياً من ZIP2 بلا LFS أو streams إضافية، ويمررها إلى ثلاث أدوات ClassID187. مشروع AssetRipper ومدخلات mesh وtrace والمطابقة الصارمة للماء تبقى كما هي. فُحص YAML، ومسار الأدوات الثلاث، وgit apply --check محلياً. اختبار native كامل يتطلب دمج التصحيح بفرع اللعبة ثم تشغيل جديد. لا APK/XAPK من التشغيل الفاشل. فرع المختبر هو مسار الكتابة.
