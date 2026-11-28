# GT — الذاكرة الحية (28 نوفمبر 2026)
[RESTORATION_PLAN_AR.md](RESTORATION_PLAN_AR.md) · [RESTORE_AR.md](RESTORE_AR.md) · [الذاكرة التاريخية الكاملة](MEMORY_HISTORY_20261128.md) · [ledger](ledger/README.md)

G1–G3: narrow source repair CI 46129648557/job 140931781926 failed at import (tools.gt_shader_fanout omitted), no test executed. Corrected sparse checkout with prior config and fanout dependencies; new authored source-only tests pending. Plan Guard 46129648507 and lint 46129648512 success. New distinct exact selected source ABI lane: rejoin same-instance original graph, compare exact Mesh fields and Material values/TexEnv slots, use one-byte type2 candidate without shader replacement and wrong GUID/fileID/type controls; bind the explicit original Shader48 pair to its per-variant parameter blobs, named CB offsets, resource/sampler registers, DXBC semantics and Vulkan varying locations; join used named texture declarations to exact typed material slots and report whether selected array participates and mesh channel availability. No standalone array readback replay, Unity or player. After source ABI result, isolate actual draw with original shader and Dummy/wrong-reference GPU controls; pivot to independent fire/water if blocked. All G0–G6 open; no production/XAPK/device proof.

المرشح source-only؛ لا إثبات لرسم الشيدر الأصلي أو الإغلاق. اقرأ سجل الذاكرة الكامل قبل إعادة عمل تاريخي؛ الروابط النسبية محفوظة في نسخة التاريخ بنفس المجلد.

## تحقق تنظيم الخطة
[Plan Guard 46129561453](https://github.com/alwansan/raf/actions/runs/46129561453/job/140931533182) و[lint 46129561451](https://github.com/alwansan/raf/actions/runs/46129561451) نجحا على `c9b239b4`؛ 11 اختباراً وفحص روابط الاستعادة. 12 workstream و6 milestones، 770 Dummy عند لقطة postvendor التاريخية، صفر workstream متحقق هاتفياً. لا تغيّر ذلك إلى ادعاء اكتمال. اختبار المصدر الخاص بمرشح المرجع منفصل، دون Unity أو ZIP2 أو بناء لاعب.

## الدفعة الجديدة — ABI للمسار الأصلي
فشل [اختبار المصدر](https://github.com/alwansan/raf/actions/runs/46129648557/job/140931781926) قبل التنفيذ بسبب sparse-checkout؛ تم تصحيح الاعتماد. أضيف مسار source ABI مستقل دون Unity أو بناء لاعب؛ يجب التحقق من نتيجته ثم تنفيذ الرسم الأصلي. لا تعتبر مطابقة أسماء أو مواقع registers وحدها قبولاً للبكسلات.
