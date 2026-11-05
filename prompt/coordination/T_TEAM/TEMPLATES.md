> **تحديث المالك، 5 نوفمبر 2026.** الدردشة العامة تبقى في مكانها (Stay in Chat). الدردشة والمهمة المجدولة تتشاركان هوية العامل وتكتبان في ملفات جلسات مستقلة. تتقدم كل دورة في نطاق مختلف عند وجود تداخل. [بروتوكول الدردشة والجدولة](CHAT_AND_SCHEDULE_AR.md) هو المرجع الحالي عند تعارض تعليمات الذاكرة أو حالة الجلسة أدناه. أذن المالك باستخدام REA والأدوات المفيدة وتجارب GitHub Actions وفق سياسة الفريق.

> T1–T5 الأسماء الفعلية؛ Tn مجردplaceholder للقالب. ملفاتissues/resources/events فيB_TEAM مقصودة لإبقاء السجل القانوني نفسه، ولا تعني عملB.

# قوالب فريق T — لا تنشئ نتائج وهمية
استعمل اسمك المعروف كما هو. قيم SHA/run/device غير المعروفة null، وليس قيمة مثال. paths أدناه نسبية إلى prompt/coordination إلا B_TEAM/…

## clients/Tn/state.json
{"schema_version":1,"username":"Tn","generation":"T-2026-11-05","session_id":"UTC-random","resumed_from_session":null,"status":"active","base_sha":null,"last_commit":null,"updated_at":null,"tracks":[],"work_ids":[],"run_urls":[],"next_step":"","memory_path":"prompt/coordination/clients/Tn/MEMORY.md"}
قيم status:active/paused/blocked/completed؛ completed لنطاق الدورة لا اكتمال اللعبة. عند احتمال جلسة هوية متزامنة لا تعدل state؛ اكتب sessions/<session_id>.md وسجّل identity_conflict.

## MEMORY.md وsessions/<session>.md
الاسم والجلسة، هدف الدورة، docs/HEAD/CL التي قُرئت، work وissue/approach، فرضية وما ثبت وما رُفض، source pins/bytes/SHA، ملفات/commits، أوامر ونتائج tests وروابط runs/artifacts وقيودها، آخر نسخة هاتف المعنية، رسائل مقروءة/ردود، work الجاري وآخر checkpoint وخطوة الاستعادة. حدّث قبل تغير المهمة وقبل/بعد تجربة وبنهاية الدورة؛ لا تحفظ أسراراً أو المصدر الخاص.

## work/<issue>/Tn-<session>-<id>.json
{"schema_version":1,"owner":"Tn","generation":"T-2026-11-05","session_id":"","issue_id":"","track":"","approach":"","status":"planned","base_sha":null,"intended_files":[],"hypothesis":"","related_work":[],"taken_over_from":[],"experiment_ids":[],"run_urls":[],"result":null,"next_step":"","updated_at":null}
قبل التنفيذ غيّر planned إلىactive؛ completed/blocked/paused بدقة بعد النتيجة. سجّل سبب أي تحقق مكرر مقصود.

## experiments/Tn/<id>.json
{"schema_version":1,"owner":"Tn","session_id":"","issue_id":"","hypothesis":"","source_commit":null,"input_hashes":[],"tool_versions":{},"commands":[],"negative_controls":[],"workflow_path":null,"run_url":null,"artifact_urls":[],"budget":"","status":"planned","observed_result":null,"rejected_hypotheses":[],"limitations":[],"integration_commit":null,"next_step":""}
نجاحCI ليس نجاحالفرضية دائماً: سجّل assertion/control الفعلي.

## B_TEAM/issues/<stable-id>.json
{"id":"","title":"","priority":"P0","status":"OPEN","track":"","evidence":[],"acceptance":[],"remaining":[],"updated_by":"Tn","updated_at":null}
أضف روابط دليل أصلية قابلة للفتح؛ unknown كما هو. source fix يحتاجcommit+test، device status يحتاجنسخة+جلسة+ملاحظةمالك. لا تعمل transition صامت، أضفحدثاً مستقلاً.

## B_TEAM/resources/<stable-id>.json
{"id":"","title":"","kind":"","source":{"provider":"","commit":null,"path":null,"bytes":null,"sha256":null},"stages":{"acquisition":"UNKNOWN","extraction":"UNKNOWN","reconstruction":"UNKNOWN","binding":"UNKNOWN","integration":"UNKNOWN","device":"UNKNOWN"},"evidence":[],"remaining":[],"updated_by":"Tn"}
سجل الفردي أو inventory بنطاق معلوم؛ لا تخلط bytes group مع object hash أو name مع GUID. عدم نشر raw لا يعني عدم حفظأوامرالبناءوالأدلة.

## B_TEAM/events/Tn/<UTC>-<id>.json
{"id":"","owner":"Tn","session_id":"","issue_id":"","type":"discovery","summary":"","evidence":[],"at":""}
أنواع:discovery/start/result/integration/closure/failure/reopen. هذه الرسائل التاريخية لا تغلق issue آلياً. لا تعدّلحدثغيرك. لا تجعلtimestamps فقط دليل حسمخلاف.

## discussions وincidents
عنوان/author/session/issue/date/sourceSHA/reply_to، السؤال أوالفرضية، الدليل، المطلوب أوالقرار، حالةالحوار والخطوةالتالية. العطللهimpact وrecovery وclosed_reason. ملفمستقل لكلرسالة/عطل.

## نقاط حفظ الدردشة والجدولة
ملف sessions/<session_id>.md هو نقطة حفظ الدورة. الحقول المطلوبة origin وsession_id وresumed_from_session(s) وbase_sha وstatus وwork_ids وrun_urls وnext_step. استخدم chat أو scheduled في origin. في work أضف experiment_key وresource_key عند اللزوم، وwaiting_ci عند انتظار تشغيل معروف مع رابطه. اتبع بروتوكول الدردشة والجدولة قبل العمل والدمج.
