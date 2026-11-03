# حادثة CI الثانية: مشت التحقق من مصدر الهوية المسجل — 2026-11-03T19:45Z

- **المؤلف:** W2 (`raft-20261103T152008Z-92502b76`)
- **الفشل:** [41682133693](https://github.com/alwansan/raf/actions/runs/41682133693) completed/failure على `8e0c9dc`، خطوة «Enumerate+aggregate» — `resources.assetsIdentity mismatch`: local payload = `87493249…` الصحيح؛ registered = sha256 لنص الـpointer (`e7e7b3f…`).
- **السبب الحقيقي:** دالة التحقق أخذت «الكائن المسجل» من ملف الـworktree. هناك، بعد `git lfs pull`، ملف resources.assets مهترئ (pay ب 874…) فانقل وفرع الكشف: `tracked-regular-blob` على المحتوى المحلي، ثم قدّنته بـ`git show HEAD:` الذي أرجع نص الـpointer (المُلتزم دائماً) فحسبت sha256لنص pointer بدل الـoid.
- **التصرف fail-closed صحيحًا:** الحادثة أثبتت أن gate الهوية يفشل محكماً على أي خلق؛ الكشف كان التصنيف الخاطئ للمصدر لا عتبة حراسياً.
- **الإصلاح ( Patched commit في نفس push):** الكائن المسجل يُقرأ دائماً من `git show HEAD:path` للفرعين (pointer أو blob)؛ لا اعتبار لحالة تهيئة الـworktree. الاختبارات بنّيت معها helper git حقيقي (commit ثم تعديل worktree) واختبرت الأربع حالات (pointer match بعد التهيئة، mismatch، regular match/mismatch) — 9/9.
- **النتيجة غير مصابة:** التشغيل المحلي كان يعمل مع ملفات LFS غير مهترئة، فاستخدم فرع pointer-oid بطريقه الصحيح؛ الأرقام aggregate نفسها بلا تغيير.
