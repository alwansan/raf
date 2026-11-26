# الاختبارات والعمليات المحفوظة

## نتائج تاريخية أصلية

- tests/historical-results.json: كل 740 ملف اختبار مع exitcode والمدة؛712 نجح و 28 فشل آنذاك.
- tests/historical-baseline-results.json:27 ملفاً فاشلاً أعيدت على baselinef5115a4؛جميعهافشلتعلىذلكالأساسأيضاً.
- tests/historical-test-logs.zip: السجلات المتاحة كاملة،بمافيها baseline و RED/GREEN و discovery و pipfailure. أسماء members و SHA256 لكلواحد في historical-test-logs-manifest.json. الأرشيفلايدعيأنكلمافيهتشغيلجديد؛التاريخوالنطاقمحفوظان.
- ضبط pass عدد FFT: fft-seven-red.log يثبت 2 مقابل 7 قبلالإصلاح. لا يعني ذلكإصلاحعرضالماء؛الفاحصالآنيلزم 7 أصلية.
- فحص Foam وثّقمسار Raft_Data المكررواختباراتالمسار؛إصلاحهاواختباراتهابالمستودع.
- الإيصالاتالمحلية FFT تحفظ 12/12 و 14entrypoints و SHA المرشحومقارنةنوعالإحداثيات؛هذهليست Unity.

## فحص التسليم الحالي

الملف current-focused-tests.txt هو الخرج الفعلي،و current-focused-test-command.json يثبتالأمروالبيئةوالأساسوالـ exitcode. يتناولعقودالمسوداتوالبواباتوالتجربةالاصطناعيةوبعضالانحدارات؛لايشغل Unity ولايعيداستخراجأصللعبةولايقيسهاتفاً. النتيجةالنهائيةتقرأمنالسجلالفعلي،ولايفترضعددمنرسالةمحادثة.

## إيصالات CI الدائمة

كل evidence/actions/<run>/artifact-provenance.json يسجل artifactID و ZIPSHA و membersSHA. راجع README_AR.md للحزمة وملفات artifact-provenance.json والملفات الأصلية داخل مجلد كل تشغيل. قيم mock الواردةفياختبارات Python لايُحتفظبهاكإيصالاتتنفيذ؛الـ raw.unity.json المحفوظمن 45760877767 قراءاتتجربةمؤلفةاصطناعياًفقط.

## المراجعات

مراجعتانمستقلتانللحفظجردتاالتعديلاتوالأدلةوراجعتانطاقفحوص NEXT23b/FFT والمثبت.أكدتاأنملف RESTORE هوالتداخلالوحيدمعرأس GitHub الأحدثوأن workflowpush قديشغل Unity؛استخدم[skip ci].الملاحظاتالمفتوحةلـ keyword universe و passType و environment في FINDINGS_AND_LIMITS_AR.md. المراجعةليست Unityrun ولاقبولاًللعبة.

الفحص المركّز الحالي: **111 اختباراً نجح، exit0** في 26 نوفمبر 2026. السجل والأمر الفعلي محفوظان؛ لا يعني ذلك نجاح suite الكاملة أو Unity أو بكسلات اللعبة.
