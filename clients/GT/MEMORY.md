# GT — الذاكرة الحية (28 نوفمبر 2026)
[RESTORATION_PLAN_AR.md](RESTORATION_PLAN_AR.md) · [RESTORE_AR.md](RESTORE_AR.md) · [الذاكرة التاريخية الكاملة](MEMORY_HISTORY_20261128.md) · [ledger](ledger/README.md)

G1–G3: Actual ABI 46130918208/job 140935636020 reached exact 6/6 TexEnv, 10/10 Mesh, 8 color/43 float, one-byte reference candidate and 3/3 negative controls. Both source programs and 2 variant blobs linked, 55 named CB offsets, 12 CB declarations, 8 texture/7 sampler registers, 5 original vertex input semantics, 6 DXBC varying records and 4 Vulkan locations; resource rename preserves SPIR-V excluding debug for 2/2. Selected array is used in explicit route (one Texture2DArray, one sampler, no type mismatch); 4 exact typed texture bindings, 1 null material and 3 outside material. Actual failed only at packed Mesh dimension. Preserve raw channel byte and decode low nibble, require exact one-stream stride/byte extent and no overlap or gaps, with flagged/invalid/overlap controls. Add numeric Material and TexEnv ST name census and compile merged original two-entry HLSL candidate with strict Vulkan1.1 validation; no original shader installation/draw or runtime upload acceptance. Source controls 46130918152 10/10; guard 46130918182 and lint 46130918205 passed. Then actual Unity draw with source-bound resources, original shader and Dummy/wrong-reference controls; distinguish null/default and global bindings, no fabricated data. No XAPK/production/device proof; G0–G6 open.

المرشح source-only؛ لا إثبات لرسم الشيدر الأصلي أو الإغلاق. اقرأ سجل الذاكرة الكامل قبل إعادة عمل تاريخي؛ الروابط النسبية محفوظة في نسخة التاريخ بنفس المجلد.

## تحقق تنظيم الخطة
[Plan Guard 46129561453](https://github.com/alwansan/raf/actions/runs/46129561453/job/140931533182) و[lint 46129561451](https://github.com/alwansan/raf/actions/runs/46129561451) نجحا على `c9b239b4`؛ 11 اختباراً وفحص روابط الاستعادة. 12 workstream و6 milestones، 770 Dummy عند لقطة postvendor التاريخية، صفر workstream متحقق هاتفياً. لا تغيّر ذلك إلى ادعاء اكتمال. اختبار المصدر الخاص بمرشح المرجع منفصل، دون Unity أو ZIP2 أو بناء لاعب.

## الدفعة الجديدة — ABI للمسار الأصلي
فشل [اختبار المصدر](https://github.com/alwansan/raf/actions/runs/46129648557/job/140931781926) قبل التنفيذ بسبب sparse-checkout؛ تم تصحيح الاعتماد. أضيف مسار source ABI مستقل دون Unity أو بناء لاعب؛ يجب التحقق من نتيجته ثم تنفيذ الرسم الأصلي. لا تعتبر مطابقة أسماء أو مواقع registers وحدها قبولاً للبكسلات.

**تنفيذ ABI:** [46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) · [اختبار المرجع](https://github.com/alwansan/raf/actions/runs/46130201606/job/140933442964) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46130201658) · [lint](https://github.com/alwansan/raf/actions/runs/46130201615). تحقق من حالات التشغيل الحية.

## تصحيح مخطط TexEnv — 28 نوفمبر
[Actual ABI 46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) توقف بعد 10/10 Mesh و8/43 قيم الخامة. [الإيصال](sessions/20261128-top-native-bc3-array/actual-46130201775.json). الخطة الخاصة تجهيزها 4 non-null و2 null؛ الكود السابق خلط القائمتين. الإصلاح يبقي التحقق الفعلي من PPtr وUV لكل الستة، ويختبر غياب/زيادة/عدم تجهيز الموارد دون تخفيف التحقق. الاختبار السابق 9/9 وPlan Guard/Lint ناجحان. لا ادعاء لرسم الشيدر الأصلي.

**إعادة الاختبار:** [Actual ABI 46130918208](https://github.com/alwansan/raf/actions/runs/46130918208/job/140935636020) · [10/10 source controls 46130918152](https://github.com/alwansan/raf/actions/runs/46130918152/job/140935635357) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46130918182) · [Lint](https://github.com/alwansan/raf/actions/runs/46130918205). لا استعادة بصرية كاملة بعد.

## ربط ABI الأصلي — نتيجة فعلية
[46130918208](https://github.com/alwansan/raf/actions/runs/46130918208/job/140935636020) و[الإيصال](sessions/20261128-top-native-bc3-array/actual-46130918208.json): 55 موقع CB و8 texture و7 sampler و2 برنامج أصلي؛ ثبت استعمال BC3 في route المختار، و6/6 PPtr/UV و3/3 ضوابط. تعثر فقط تفسير dimension؛ نختبر low nibble مع الاحتفاظ بالبايت وفحص stride، ثم تجميع مرشح HLSL بمدخلين. لا ادعاء رسم أو نجاح Unity. 3 موارد خارج Material و1 null ما تزال بحاجة تحقق الربط الفعلي.
