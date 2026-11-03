
> **Owner update 2026-11-04:** Prefer original game data from `zip2/Raft`, pinned15964ea8f246b6e076ce26b60931ee2e1a9a2385. Read `docs/ZIP2_SOURCE_PROVIDER.md` before acquisition. Reassemble split files and verify size/SHA; avoid new LFS pulls. Keep current Raft tree and existing fingerprints until consumers are migrated. Focus on water/shaders/colors/materials and original-data restoration. This updates source acquisition, not this role's build permissions.

# استكمال Raft في جلسة جديدة

انسخ محتوى [CONTINUE_RAFT_AR.md](CONTINUE_RAFT_AR.md) وأرسله في الجلسة الجديدة. هذا مسار دائم؛ لا تحتاج إلى طلب إعداد رسالة نقل كل مرة.

[STATUS.md](STATUS.md) يربط أحدث تسليم ونتائج مؤكدة والمتبقي. يجب على كل جلسة وكل مهمة إصلاح تحديثه بعد تقدم مهم وقبل إنهاء العمل، وتحديث رسالة الاستكمال إذا تغيرت التعليمات. يفرض `AGENTS.md` هذا السلوك على الجلسات المقبلة.

التوثيق لا يشغّل جلسة في الخلفية بذاته. المهمة المجدولة تنفّذ دورات وفق جدولها، بينما الجلسة الجديدة تبدأ بعد إرسال الرسالة. دائماً تُراجع HEAD وActions مباشرة لأن التوثيق قد تسبقه تعديلات متزامنة.


للعمل بعدة عملاء: [البرومبت الموحد](coordination/UNIFIED_PROMPT_AR.md)، [استعادة عميل بالاسم](coordination/RESTORE_CLIENT_AR.md)، [نظام التنسيق](coordination/README.md).
