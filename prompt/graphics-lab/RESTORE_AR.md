# رسالة الاستعادة — Graphics Root-Cause Lab

**هوية العمل: GFX-LAB**، مرافق للمالك في تشخيص واختبار ألوان وشيدرات Raft Android، **منفصل عن T1–T5**. Stay in Chat، ولا تشترط Work أو Codex أو تغيير الدردشة.

المستودع: https://github.com/alwansan/raf
فرع الكتابة الوحيد لهذا الدور: `experiment/android-graphics-rootcause`
أُنشئ مباشرة من `main@9b89f62772c2c61f6269fd2249f8560af1522892` وليس من فرع الفريق.

## الاستعادة بالترتيب
1. تحقق من HEAD في فرعنا، واقرأ **كلّ** `AGENTS.md` و`prompt/graphics-lab/PROTOCOL_AR.md` و`memory/MEMORY.md` و`memory/STATE.json` و`docs/ROOT_CAUSE_REVIEW_AR.md` و`docs/EXPERIMENT_ROADMAP_AR.md`.
2. اقرأ **كل ملفات الجلسات الأحدث ذات الصلة** من `memory/sessions/` ونتائج `experiments/`؛ قد تكون نتائج أحدث من STATE. لا تختزل الاستعادة إلى آخر ملف بالاسم وحده.
3. تحقق من الفرع العامل `feature/android-native-port` ومن أحدث Actions ذات العلاقة RENDER-002 وWATER-001 وT3/T2/T1؛ اقرأ آخر أدلة CL للهاتف ونسخة APK/OBB المقابلة قبل أي مقارنة. لا تنقل HEAD الفريق أو أصوله إلى فرعنا.
4. أنشئ `session_id` فريداً و`origin=chat` وسجل `resumed_from` و`base_sha` و`scope` و`experiment_key` وأي مشاركة موارد؛ اختر تجربة صغيرة واحدة تفصل بين فرضيتين مع نتيجة قابلة للدحض.
5. نفذ قراءة/أداة/اختباراً مستقلاً فقط، مع مصدر آمن وأدلة ذات مرحلة محددة. لا تكرر تشغيل CI موجوداً ولا تتداخل مع تغييرات الفريق، ولا تعلن إصلاح المظهر أو الهاتف بناء على مصدر فقط.
6. سجل النتيجة والقيود والروابط وSHA والاختبار والخطوة التالية في جلسة مستقلة ثم حدّث STATE وMEMORY. إن لم تثبت الفرضية اكتب `inconclusive` أو `rejected` بدلاً من نجاح وهمي.

## صورة العمل عند الإنشاء
- أصل المشكلة الأكبر المثبت في تصدير حقيقي: `110/142` ملف ShaderLab يحمل Dummy، و`770/1536` وثيقة Material تشير إليه **بعد restorer وقبل Unity** ضمن CI42058825739؛ **لا يثبت** عدد الأجسام البيضاء على الجهاز.
- النسخة 89 أنتجت الهاتف صور يد/طوف بيضاء ومؤثر مربع؛ سجلاتها تحوي أخطاء تمريرات ماء/FFT، لكن الدخول والحفظ نجحا في اختبار المالك.
- المصدر الأصلي يحوي `1556` Material و`4050` Texture2D و`165` Shader، وملاحظة مصدر Linear وتقسيم sRGB/Linear؛ نتائج 41 Material و106 Texture2D محدودة أثبتت سلامة جوانب من القيم/النقل ولا تثبت بكسلات Android.
- الدخان Shader48/34 المصدر مرتبط بـ17 Renderer و34 Material slots؛ same-export ظل Dummy، وقد ثبتت إمكانية تحويل 4 مراحل DXBC إلى SPIR-V CPU فقط، مع فجوة Stage IO ودون Pixel test.
- المشروع الأساسي RENDER-002/WATER-001 OPEN، NOT_READY 0/3؛ لا APK جديد نتيجة عمل فرعنا.

**نص الاستعادة المختصر في دردشة جديدة:**
> استعد دور GFX-LAB من https://github.com/alwansan/raf/blob/experiment/android-graphics-rootcause/prompt/graphics-lab/RESTORE_AR.md، واقرأ بروتوكول الذاكرة وأحدث الجلسات وActions، وأكمل التجربة التالية في نفس الفرع فقط.
