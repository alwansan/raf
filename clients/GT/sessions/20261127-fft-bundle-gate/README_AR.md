## GT — G4 مرشح بوابة FFT المغلقة | 27 نوفمبر 2026

رأس البدء a6b97f5ab6ab2640f5fce24cfc368346d986f6e6 مطابق للرأس الحي، [مرجع المالك المثبت](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md). [Replay45936590347](https://github.com/alwansan/raf/actions/runs/45936590347) ناجح، ليس قبول البوابة. البيئة الجديدة بلا checkout سابق ولا git network ولا Unity/spirv-val محلي؛ لا ملفات محلية حذفت، ولا إمكانية تدقيق غير المنشور من الجلسة القديمة.

مرشح scripts/gt_fft_bundle_gate.py يفصل أسماء Stereo الأربعة وflags صفر عن فهارس legacy/global/local الفعلية، يرفض أي اسم مجهول أو lane نشط قبل فلترة المراحل، ويشترط سبعة Pass Normal وVS/FS وspirv-val لكل وحدة مفكوكة وSHA/bytes. tools/synthetic_material_alpha/fft_bundle_gate_probe.py يقيد المدخلات بالأرشيفين المؤلفين المثبتين، يربط source/receipt/bundle، ويختبر مجهول/flags/active lanes/غياب المرحلة/تغيير نفس الحجم وحقن wrong coordinate في البرامج الفعلية. **مرشح ينتظر CI المعزول، لا نجاح جديد.** لم يتغير gate/installer الأصلي، ولا إثبات مصدر أصلي مأذون أو إصلاح خطأ FFT التاريخي.

عند Continue: تحقق من HEAD وActions ثم شغّل CPU-only على الأرشيفين دون Unity جديد، احفظ الإيصال والضوابط. إذا فشل أصلح السبب دون تليين العقد. A3 مشروط بمصدر مأذون؛ بعدها أقرب G4/G5 منتج. G0–G6 مفتوحة؛ 688/786 و98 Dummy/37GUID تاريخية. لا ZIP2 أو أصول أصلية أو XAPK أو هاتف؛ CL/المختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل، أولوية الأبيض والنار.

