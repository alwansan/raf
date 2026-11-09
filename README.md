# Raft Android — Graphics Root-Cause Lab (GFX-LAB)

فرع مختبر **مستقل مشتق مباشرة من main** عند `9b89f62772c2c61f6269fd2249f8560af1522892`. ليس فرع عمل اللعبة النهائي، ولا يحتوي نسخة Raft/ZIP2 الكاملة.

## افتح هذه الروابط أولاً
- [التحقيق الجذري للألوان والشيدرات والإضاءة والنار والماء](docs/ROOT_CAUSE_REVIEW_AR.md)
- [خطة التجارب المتدرجة](docs/EXPERIMENT_ROADMAP_AR.md)
- [رسالة الاستعادة لأي دردشة جديدة](prompt/graphics-lab/RESTORE_AR.md)
- [بروتوكول العمل والتوثيق](prompt/graphics-lab/PROTOCOL_AR.md)
- [الذاكرة الدائمة](memory/MEMORY.md) و[الحالة](memory/STATE.json) و[الجلسات](memory/sessions/)
- [أدلة التجارب](experiments/)

## فصل المهام
فريق T1–T5 ما زال يعمل في [feature/android-native-port](https://github.com/alwansan/raf/tree/feature/android-native-port). لا نعدل ملفاتهم أو شيدرات اللعبة أو Git LFS من هذا الفرع. يستعمل GFX-LAB الأدلة المثبتة لدراسة الأسباب والحصول على إصلاح ضيّق قابل للتحقق، ثم يسلم النتائج للعامل المختص.

لا يعني نجاح exporter أو CI أو mini GLES اختبار بكسلات لعبة Raft على Android. حالة `RENDER-002/WATER-001` مفتوحة، ولا إصدار APK/OBB/XAPK جديد بلا إثبات تكافؤ وتسلسل قبول مستقل.

**لاستعادة الجلسة الجديدة:** أرسل رابط [RESTORE_AR.md](prompt/graphics-lab/RESTORE_AR.md) واطلب من GFX-LAB قراءة أحدث `memory/sessions` وActions ومتابعة التجربة التالية في هذا الفرع فقط.
