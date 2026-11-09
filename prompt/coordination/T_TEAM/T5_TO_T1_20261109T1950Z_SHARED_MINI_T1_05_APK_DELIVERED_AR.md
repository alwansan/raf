# T5 → T1 | تم تسليم مختبر T1-05 المحلي512 للإختبار على الهاتف
session_id: 20261109T1946Z-T5-chat-shared-mini512-73bc
origin: chat
date_utc: 2026-11-09T19:50:00Z
status: CI_APK_DELIVERED_AWAITING_OWNER_DEVICE

## نتيجة البناء
- طلب واحد SHARED فقط [3185e449](https://github.com/alwansan/raf/commit/3185e449dcefd27ab77b527f9d3b85d71104f497)، الأب المثبت source SHA 2d7c268248b505e4dd9ad1daa9491787df07665c، pack SHA256 9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6.
- [GitHub Actions 42686652150](https://github.com/alwansan/raf/actions/runs/42686652150) completed SUCCESS 19:48:28Z؛ #14، artifact 13705307079، اسم Raft-Team-Lab-3185e449dcefd27ab77b527f9d3b85d71104f497، ZIP SHA256 067c150204468dea9daf49f7a06b908a0c2833f272435dae6a12cc182a637626، expires 2026-11-23 19:48 UTC.
- APK المستخرج فعلياً: Raft-Team-Lab-debug.apk، 99622 bytes، SHA256 e145a50b8b2be0a9f3a37493fe5f0f243b65644b844706cf82192c91d4ea6c52، package com.alwansan.raft.lab.shared، versionCode14/versionName0.2.14-shared.
- تم التحقق من AndroidManifest الثنائي وشهادة v2 Debug SHA256 a60c8608f3c79a40a074e191f1696700dd6bbe160cb9343b971091b114709927 (مختلف عن 0.2.13)، وجود T1FftButterflyProbe وlocal_size_x=512 داخل DEX، وتطابق testpack الأصلي والمضمن byte-for-byte (30/30).
- أعطيت المالك APK مباشرًا كملف دردشة مرفق على sandbox:/mnt/data/Raft-Team-Lab-T1-05-v0.2.14.apk وملف pack الاختياري؛ لا تستخدم sandbox path كرابط عام داخل GitHub. GitHub artifact ZIP متاح من صفحة التشغيل؛ لم ينشر Release APK عام ولا توقيع stable.

## ما ينتظره T1
1. صاحب الهاتف يصدر logs القديمة، ثم uninstall تطبيق المختبر السابق فقط إذا اختلف التوقيع، ويثبت APK14؛ اللعبة الأصلية لا تمس.
2. يفتح تطبيق المختبر العربي Portrait ويختار «تشغيل T1 تلقائيًا»؛ T1-01..T1-05. يرفع events*.jsonl + summary*.json إلى CL/test.
3. افحص نتيجة T1-05 الحقيقية (gpu SSBO readback checked_floats=1024, gl_error=0x0, max_abs_error <=0.00003) واحفظ snapshot. FAIL أو BLOCKED دليل، لا تعدّل الحالة. لا حاجة screenshot.
4. **حد الإثبات:** مصنوع GLES3.1، ليس original Raft shader أو Unity FindKernel/Dispatch؛ WATER-001 ما يزال OPEN/NOT_READY، لا XAPK كاملة ولا vote 5/5 جديد.

Next: T1 يقرأ CL/test الجلسة التالية ويبني تفسيرًا مقيدًا لنتيجة GPU؛ T5 يراجع artifact consistency/OBB إن ظهرت ملفات مستخدم جديدة.
