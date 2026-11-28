> **استئناف GT — 28 نوفمبر 2026:** اقرأ [قرار المالك](OWNER_DIRECTIVE_RESTORE_FIRST_AR.md)، [الخطة](RESTORATION_PLAN_AR.md)، [RESTORATION_PLAN.json](RESTORATION_PLAN.json)، [state.json](state.json)، [الذاكرة](MEMORY.md) و[سجل الاستعادة السابق](RESTORE_HISTORY_20261128.md). مرجع علي المثبت: [1a78eb276](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md).

## آخر نتيجة متحققة
[Actual 46128563088](https://github.com/alwansan/raf/actions/runs/46128563088/job/140928500873) و[lint 46128563099](https://github.com/alwansan/raf/actions/runs/46128563099) ناجحان؛ [Plan Guard 46128563095](https://github.com/alwansan/raf/actions/runs/46128563095) فشل بسبب حجم الملفات قبل الاختبارات. [إيصال آمن](sessions/20261128-top-native-bc3-array/actual-46128563088.json).

G1–G3: Actual 46128563088/job 140928500873 success, lint 46128563099 success; selected native class187 type2 only resolves in isolated authored shader, original type3 and wrong GUID/fileID rejected; 22/22 BC3 ranges exact, 2,796,202 pre/post GPU coordinates exact, UNorm vs CPU 51,734 errors >1/255, sRGB GPU vs transfer of GPU UNorm zero >1/255 but not full equality. Narrow reference repair candidate preserves original shader, exact GUID/fileID, UV and every other byte; source-free controls pending CI. Next bind original Shader48 program/keywords/sampler ABI and exact selected Mesh+Material in isolated draw with Dummy and wrong-reference controls; do not repeat standalone array observation. If blocked, independent fire/water. G0–G6 open, no production/XAPK/device acceptance; Plan Guard migration pending new CI.

## الخطة والحالة
[ledger](ledger/README.md) يحفظ السجلات التاريخية. القراءة الكاملة عبر `scripts.gt_restoration_plan_check._read`؛ الحقول النشطة مباشرة. السجل السابق محفوظ في نفس المجلد مع روابطه النسبية. تحقق من HEAD وActions قبل كل دفعة.

## الحدود
مرشح الإصلاح خاص بمرجع native class187، بلا تغيير للشيدر الأصلي أو GUID/fileID/UV. لا دمج إنتاجي ولا ادعاء رسم أصل أو إصلاح أبيض. لا XAPK قبل الاستعادة الكاملة؛ CL والمختبر للقراءة فقط وBLACK والأنيميشن مؤجلان.
