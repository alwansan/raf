# Raft 102 — اختبار FFT على Adreno

[CL رفع 15](https://github.com/alwansan/CL/tree/3c26bb5d0f4de2cbffd42197dae9ae1372721659/raft%20log) · [البناء 43299084397](https://github.com/alwansan/raf/actions/runs/43299084397).

سجلا اللعبة 517 و595 حدثاً. كلاهما installed_version_code=102 وOBB 2320406475 بايت؛ البصمة الكاملة على الهاتف لم تُقَس. المدقق أكد 16+16 محاولة مرصودة في site=0/pass=0، جميعها threw، ولا حدث Dispatch. أول استثناء في كل جلسة بعد حدث threw مباشرة: kernelIndex 6، الحد الأعلى 0. يثبت الفشل في أول SetTexture. العدد 32 حد التتبع المسجل وليس كل التكرارات.

LogRaft رصد 4576 خطأ kernel 6، 11512 Spectrum و17080 Foam. ظهرت أيضاً جذور Underwater 1/3 في الجلسة الثانية. لا دليل إصلاح بصري. الخطوة التالية تدقيق الأصل المرتبط فعلاً بمكوّن FFT ومحتوى استيراد ComputeShader على Vulkan مقابل برامج ZIP2؛ لا يفيد تغيير الرقم إلى 0 إذا أبلغ Unity عن صفر kernels. لا إعادة مطلوبة لاختبار 102.
