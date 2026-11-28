> **استئناف GT — 28 نوفمبر 2026:** اقرأ [قرار المالك](OWNER_DIRECTIVE_RESTORE_FIRST_AR.md)، [الخطة](RESTORATION_PLAN_AR.md)، [RESTORATION_PLAN.json](RESTORATION_PLAN.json)، [state.json](state.json)، [الذاكرة](MEMORY.md) و[سجل الاستعادة السابق](RESTORE_HISTORY_20261128.md). مرجع علي المثبت: [1a78eb276](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md).

## آخر نتيجة متحققة
[Actual 46128563088](https://github.com/alwansan/raf/actions/runs/46128563088/job/140928500873) و[lint 46128563099](https://github.com/alwansan/raf/actions/runs/46128563099) ناجحان؛ [Plan Guard 46128563095](https://github.com/alwansan/raf/actions/runs/46128563095) فشل بسبب حجم الملفات قبل الاختبارات. [إيصال آمن](sessions/20261128-top-native-bc3-array/actual-46128563088.json).

G1–G3: narrow source repair CI 46129648557/job 140931781926 failed at import (tools.gt_shader_fanout omitted), no test executed. Corrected sparse checkout with prior config and fanout dependencies; new authored source-only tests pending. Plan Guard 46129648507 and lint 46129648512 success. New distinct exact selected source ABI lane: rejoin same-instance original graph, compare exact Mesh fields and Material values/TexEnv slots, use one-byte type2 candidate without shader replacement and wrong GUID/fileID/type controls; bind the explicit original Shader48 pair to its per-variant parameter blobs, named CB offsets, resource/sampler registers, DXBC semantics and Vulkan varying locations; join used named texture declarations to exact typed material slots and report whether selected array participates and mesh channel availability. No standalone array readback replay, Unity or player. After source ABI result, isolate actual draw with original shader and Dummy/wrong-reference GPU controls; pivot to independent fire/water if blocked. All G0–G6 open; no production/XAPK/device proof. Execution fb2f43bae92fa320e5dc5721de3c5ee89169a295; repair controls 46130201606/job 140933442964 completed/success; source ABI 46130201775/job 140933443625 in_progress/pending; Plan Guard 46130201658 in_progress/pending; lint 46130201615 completed/success. Inspect actual logs before advancing; no claim of passing the new authored tests or ABI until verified.

## الخطة والحالة
[ledger](ledger/README.md) يحفظ السجلات التاريخية. القراءة الكاملة عبر `scripts.gt_restoration_plan_check._read`؛ الحقول النشطة مباشرة. السجل السابق محفوظ في نفس المجلد مع روابطه النسبية. تحقق من HEAD وActions قبل كل دفعة.

## الحدود
مرشح الإصلاح خاص بمرجع native class187، بلا تغيير للشيدر الأصلي أو GUID/fileID/UV. لا دمج إنتاجي ولا ادعاء رسم أصل أو إصلاح أبيض. لا XAPK قبل الاستعادة الكاملة؛ CL والمختبر للقراءة فقط وBLACK والأنيميشن مؤجلان.

## تحقق تنظيم الخطة
[Plan Guard 46129561453](https://github.com/alwansan/raf/actions/runs/46129561453/job/140931533182) و[lint 46129561451](https://github.com/alwansan/raf/actions/runs/46129561451) نجحا على `c9b239b4`؛ 11 اختباراً وفحص روابط الاستعادة. 12 workstream و6 milestones، 770 Dummy عند لقطة postvendor التاريخية، صفر workstream متحقق هاتفياً. لا تغيّر ذلك إلى ادعاء اكتمال. اختبار المصدر الخاص بمرشح المرجع منفصل، دون Unity أو ZIP2 أو بناء لاعب.

## الدفعة الجديدة — ABI للمسار الأصلي
فشل [اختبار المصدر](https://github.com/alwansan/raf/actions/runs/46129648557/job/140931781926) قبل التنفيذ بسبب sparse-checkout؛ تم تصحيح الاعتماد. أضيف مسار source ABI مستقل دون Unity أو بناء لاعب؛ يجب التحقق من نتيجته ثم تنفيذ الرسم الأصلي. لا تعتبر مطابقة أسماء أو مواقع registers وحدها قبولاً للبكسلات.

**تنفيذ ABI:** [46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) · [اختبار المرجع](https://github.com/alwansan/raf/actions/runs/46130201606/job/140933442964) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46130201658) · [lint](https://github.com/alwansan/raf/actions/runs/46130201615). تحقق من حالات التشغيل الحية.
