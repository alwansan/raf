# GT — دورة ZIP2 فقط + تحقق Material Graph

- **session_id:** `GT-20261112-0215-CHAT-02`
- **origin:** `chat`
- **agent:** `GT`
- **repo/branch:** `alwansan/raf` / `feature/android-native-port`
- **source pinned:** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- **starting HEAD:** `d83334eabe1806384a517ee9e903ae6c453a5961`
- **scope:** قرار المالك بعدم استخدام LFS، تعميم مزوّد ZIP2 على ملفات الرسوميات الخارجية، وحل روابط Material عبر 82 حاوية.

## قرار المالك (مستمر ومثبت)

**GT لا يستخدم Git LFS إطلاقاً لاكتساب أصول اللعبة.** استخرج كل البيانات اللازمة من ZIP2 المثبّت للقراءة فقط. الملفات المقسمة `part-00000` وما بعدها تُجمّع بترتيبها بعد فحص الأجزاء، وتُثبت **SHA256 والحجم الأصلي** وفق `RAFT_FILE_MANIFEST.tsv` قبل استعمالها. الاستعادة في مساحة مؤقتة معزولة، بلا إعادة كتابة `feature/.../Raft` أو تغيير `.meta`، وبلا LFS fallback. `actions/checkout lfs:false` يوقف آلية smudge ولا يعني تنزيل LFS. القرار محفوظ في `MEMORY.md` و`state.json` و`RESTORE_AR.md`.

## الدفعة 3 — ZIP2 source payloads

- أُضيف `scripts/gt_zip2_payloads.py`؛ يستطيع استعادة أي ملف أصلي في manifest، لا يقتصر على الحاويات المسلسلة: `.resS` و`.resource` و`.assets` والملفات غير المتدفقة. يقبل طلب مسارات محددة/ميزانية صريحة، يتحقق من Git checkout SHA وGit blob SHA للبيان قبل الفحص، يرفض symlink/hardlink/out-of-root والملفات غير المطابقة والتكرارات، وينشر file بعد استكمال full SHA256/byte count.
- أُضيف `tests/test_gt_zip2_payloads.py` مع حالات plain/split/cache/corruption/traversal/missing parts/budget/source pin، وCI مستقل `.github/workflows/raft-gt-zip2-payloads.yml`.
- [Run 43117743780 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43117743780) [Artifact 13899122924](https://github.com/alwansan/raf/actions/runs/43117743780/artifacts/13899122924): أصلان `Raft_Data/level0.resS` و`Raft_Data/level30` (split) = **70,566,428 بايت**، SHA256 والحجم مطابقان، `git_lfs_used=false`. ليس تحقّق بيانات GPU أو import.

## الدفعة 4 — Material reference identity across all 82

- أُضيف `scripts/gt_original_material_link_graph.py` و`tests/test_gt_original_material_link_graph.py`، وأُضيف فحصهما إلى CI الموجود `raft-gt-serialized-graphics-owners.yml`.
- جميع 82/82 owner تُقرأ بعد SHA256 مطابق من ZIP2؛ تُحسب الهوية الأصلية للـMaterial كـ`(owner,path_id)` مع جدول استعمال مستقل للـRenderer والـMaterial slot. تُحل `m_FileID` من الجدول الأصلي للـexternals؛ لا تُخمّن أسماء المواد.
- [Run 43118214676 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43118214676) [Artifact 13899108653](https://github.com/alwansan/raf/actions/runs/43118214676/artifacts/13899108653): إجمالي **195,174 Material slot**، منها **194,293 غير فارغ** استهدف كائن `Material` أصلياً مثبتاً، **881 null**. مراجع خارجية 191,657 ومحلية 2,636، والمواد الفريدة المستخدمة مباشرة بواسطة Renderers **1,351** من أصل **1,556 Material**. تمت مطابقة عدد مواضع المواد في المشاهد الـ40 السابقة (**191,845**، منها **191,116 external** و**729 null**) بلا اختلاف.
- [نسخة آمنة من الدليل](../evidence/20261112_original_material_link_graph.json). لا تحتوي PPtrs الأصلية أو game raw bytes. **هذا إثبات روابط المصدر وليس Source→Export .meta/GUID، ولا قبول shader/GPU/Android.**

## قرارات السلامة والتنسيق

- لا تستبدل `Raft` في الفرع الحي بمحتوى ZIP2 أو تنسخ حمولة أصلية إلى commits. لا تعدّل build request أو native delivery workflow الخاص بـT5 ولا تبدأ full APK دون بروتوكول الفريق.
- أرقام GT من 82 حاوية مسلسلة؛ البيانات الخارجية `.resS` ذات حجم أكبر لا تثبت محتويات Texture/mesh streams بمجرد وجود header. الاختبار الجديد أثبت نقل ملفي Stream/scene فقط.
- أصول المعايرة الستة/السبعة باقية للمقارنة، لا تخلطها مع 4,708 Mesh و4,050 Texture2D و165 Shader و9 Compute الأصلية.
- **الدمج الفعلي في Unity Android لا يزال غير مثبت** في هذه الدورة. لا تعطِ نسبة مبالغاً بها.

## نقطة الاستئناف الدقيقة

1. افحص أحدث HEAD وأعمال T-team والحزم الجارية، ولا تتداخل مع native pipeline أو أصول الآخرين.
2. حل `Material→Texture2D/Cubemap` و`MeshFilter/SkinnedMeshRenderer→Mesh` بهويات أصلية، مع تجميع استعمالات مستقلة ثم match إلى ExportedProject الفعلي. لا تعتمد name-only.
3. استعد `.resS` الضرورية للدفعة المرئية فقط عبر `scripts/gt_zip2_payloads.py`، ثم افحص texture offsets/mips وMesh vertex/index/UV/normal/tangent مع SHA256 المصدر؛ استخدم أدوات الإصلاح الموجودة مع T3/W3.
4. اختر أول مجموعة رسومية عالية الاستعمال تحتاج إصلاحاً حقيقياً في export، نفّذ التعديل وحافظ على .meta/GUID والروابط، اختبرها في isolate/mini lab أو Unity بالمناسب دون duplicate heavy native، ثم حدّث `SUMMARY_AR.md` والذاكرة والحالة والدليل وروابط Action/commit.
