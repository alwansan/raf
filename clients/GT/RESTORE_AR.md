> **استئناف GT — 28 نوفمبر 2026:** اقرأ [قرار المالك](OWNER_DIRECTIVE_RESTORE_FIRST_AR.md)، [الخطة](RESTORATION_PLAN_AR.md)، [RESTORATION_PLAN.json](RESTORATION_PLAN.json)، [state.json](state.json)، [الذاكرة](MEMORY.md) و[سجل الاستعادة السابق](RESTORE_HISTORY_20261128.md). مرجع علي المثبت: [1a78eb276](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md).

## آخر نتيجة متحققة
[Actual 46128563088](https://github.com/alwansan/raf/actions/runs/46128563088/job/140928500873) و[lint 46128563099](https://github.com/alwansan/raf/actions/runs/46128563099) ناجحان؛ [Plan Guard 46128563095](https://github.com/alwansan/raf/actions/runs/46128563095) فشل بسبب حجم الملفات قبل الاختبارات. [إيصال آمن](sessions/20261128-top-native-bc3-array/actual-46128563088.json).

G1–G3: Actual ABI 46130201775/job 140933443625 failed after exact same-export graph, Mesh 10/10 and 8 color/43 float matches. Prestaging proved 4 non-null/2 null slots; source code compared all 6 source/export names to the 4 non-null-only private plan names and would reject, and indexed null targets incorrectly. Corrected explicit non-null plan validation and get(prop) for the 2 null slots; all 6 still require original PPtr/UV checks. Added authored 6-slot regression with extra-null/missing-nonnull/missing-export/unprepared negative controls; more precise private-safe failure phases. Source controls 46130201606 passed 9/9; Plan Guard 46130201658 and lint 46130201615 passed. New source ABI run must reconcile exact reference candidate, parameter blobs, CB offsets, sampler binding and selected array use plus mesh vertex channels; don't repeat standalone Unity array readbacks. If an ABI-specific blocker remains, classify it and advance an independent fire/water path. No original draw, device, production or XAPK; G0–G6 remain open.

## الخطة والحالة
[ledger](ledger/README.md) يحفظ السجلات التاريخية. القراءة الكاملة عبر `scripts.gt_restoration_plan_check._read`؛ الحقول النشطة مباشرة. السجل السابق محفوظ في نفس المجلد مع روابطه النسبية. تحقق من HEAD وActions قبل كل دفعة.

## الحدود
مرشح الإصلاح خاص بمرجع native class187، بلا تغيير للشيدر الأصلي أو GUID/fileID/UV. لا دمج إنتاجي ولا ادعاء رسم أصل أو إصلاح أبيض. لا XAPK قبل الاستعادة الكاملة؛ CL والمختبر للقراءة فقط وBLACK والأنيميشن مؤجلان.

## تحقق تنظيم الخطة
[Plan Guard 46129561453](https://github.com/alwansan/raf/actions/runs/46129561453/job/140931533182) و[lint 46129561451](https://github.com/alwansan/raf/actions/runs/46129561451) نجحا على `c9b239b4`؛ 11 اختباراً وفحص روابط الاستعادة. 12 workstream و6 milestones، 770 Dummy عند لقطة postvendor التاريخية، صفر workstream متحقق هاتفياً. لا تغيّر ذلك إلى ادعاء اكتمال. اختبار المصدر الخاص بمرشح المرجع منفصل، دون Unity أو ZIP2 أو بناء لاعب.

## الدفعة الجديدة — ABI للمسار الأصلي
فشل [اختبار المصدر](https://github.com/alwansan/raf/actions/runs/46129648557/job/140931781926) قبل التنفيذ بسبب sparse-checkout؛ تم تصحيح الاعتماد. أضيف مسار source ABI مستقل دون Unity أو بناء لاعب؛ يجب التحقق من نتيجته ثم تنفيذ الرسم الأصلي. لا تعتبر مطابقة أسماء أو مواقع registers وحدها قبولاً للبكسلات.

**تنفيذ ABI:** [46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) · [اختبار المرجع](https://github.com/alwansan/raf/actions/runs/46130201606/job/140933442964) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46130201658) · [lint](https://github.com/alwansan/raf/actions/runs/46130201615). تحقق من حالات التشغيل الحية.

## تصحيح مخطط TexEnv — 28 نوفمبر
[Actual ABI 46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) توقف بعد 10/10 Mesh و8/43 قيم الخامة. [الإيصال](sessions/20261128-top-native-bc3-array/actual-46130201775.json). الخطة الخاصة تجهيزها 4 non-null و2 null؛ الكود السابق خلط القائمتين. الإصلاح يبقي التحقق الفعلي من PPtr وUV لكل الستة، ويختبر غياب/زيادة/عدم تجهيز الموارد دون تخفيف التحقق. الاختبار السابق 9/9 وPlan Guard/Lint ناجحان. لا ادعاء لرسم الشيدر الأصلي.
