# Raft Android — مراجعة اختبار 12 نوفمبر 2026

[جلسة CL المثبتة](https://github.com/alwansan/CL/tree/cffd3f7be2d0c47649da9b28eae17c36d031f0e8/raft%20log/lf/LogRaft-20261112-183147-926). طوبقت مع سبعة سجلات JSONL للتطبيق في رفع CL نفسه. Adreno 730 Vulkan على Android 15. سجل التطبيق أبلغ عن installed_version_code=100، ولا يوجد SHA للـAPK أو OBB في السجل يربطه قطعياً بتشغيل CI.

| المسار | نتيجة الاختبار |
|---|---|
| Spectrum | 19,191 خطأ في عداد Logcat، مع طلب pass 3/4/5 من مادة لها pass واحد |
| Foam Global | 23,038 خطأ، مع طلب pass 1 من مادة لها pass واحد |
| FFT | 7,263 خطأ، كلها index 6. stack يحدد Dx11FFT.ComputeFFT ورسالة Unity تعطي حدّاً أعلى صفر |
| Underwater/Base IME | سجل التطبيق أظهر DrawMesh يرفض index 1 و3. عائق مستقل عن عداد Blit؛ المطلوب أن يدعم الـSubShader الفعلي أربع تمريرات على الأقل مع حالات الرسم الأصلية |
| Subsurface Blur | صفر في تصنيف أخطاء pass في جلسة LogRaft؛ تطابق بكسلات البلور لم يُقَس |
| OBB والصوت | قراءة أول بايت من Unity ZIP ووجود 5/5 مسارات bank. MasterBank.bank حمّل 533 حدثاً. سجل Logcat يحوي خطأي تحميل GUID؛ اجتياز probe لا يثبت كل الأصول |
| العالم | وصل نداء تحميل العالم وتكرر إسناد الاكتمال الأصلي مرتين في سجل التطبيق. ظهرت أحداث SaveGame/SaveWorld؛ لا استنتاج عن ثبات الحفظ من أسماء الأحداث وحدها |
| المؤشر | 4,668 تحذير RGBA32؛ مسار مستقل عن الماء |

فحص سجلات التطبيق لم يجد أحداث `t1_original_fft_dispatch.before` أو terminal. توجد آثار خطأ Dx11FFT في الجلسات السبع، لكن عدم وجود الحدث لا يحسم هل الاستثناء وقع قبل Dispatch أثناء SetTexture أو أن النسخة لا تتضمن الخطاف. المطلوب ربط SHA الحزمة القادمة ثم رصد عمليات الربط قبل Dispatch، ومطابقة Spectrum/Foam/Underwater مع الأصل. لا تغيير لفهرس kernel ولا تحويل GFX160 الاصطناعي إلى إصلاح للعبة.

[43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) تشغيل مستقل وصل إلى Unity Editor عند المراجعة. يبقى اختبار الحزمة الجديدة على الهاتف معلقاً.
