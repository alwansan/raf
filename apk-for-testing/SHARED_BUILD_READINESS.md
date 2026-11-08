# جاهزية بناء APK المختبر المشترك — T1–T5
**مختلفة تماماً عن** `prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md` الذي يخص XAPK لعبة Raft الكاملة. اقرأ [السياسة](UNIFIED_LAB_POLICY_AR.md).
**shared_round_id:** shared-20261108-r1
**build_decision:** NOT_REQUESTED — لم يراجع T5 الأصوات بعد. أي صوت من العامل **لا يُنشئ طلب بناء تلقائياً**.

| العامل | القرار | لماذا؟ وما الاختبارات/التغييرات؟ | evidence SHA/CI | وقت UTC | الجولة |
|---|---|---|---|---|---|
| T1 | NOT_REVIEWED | يبدأ T1 بالمراجعة بنفسه | — | — | shared-20261108-r1 |
| T2 | NOT_REVIEWED | يبدأ T2 بالمراجعة بنفسه | — | — | shared-20261108-r1 |
| T3 | NOT_REVIEWED | يبدأ T3 بالمراجعة بنفسه | — | — | shared-20261108-r1 |
| T4 | NOT_REVIEWED | يبدأ T4 بالمراجعة بنفسه | — | — | shared-20261108-r1 |
| T5 | NOT_REVIEWED | يبدأ T5 بالمراجعة بنفسه | — | — | shared-20261108-r1 |

## T5 — سجل قرار بناء المختبر فقط
- **latest_shared_apk_sha256:** لا يوجد منشور موحد حتى الآن.
- **candidate_source_sha:** لم يثبت بعد.
- **pack_sha256:** لم يثبت بعد.
- **native mini request/run:** لا طلب بهذه الجولة؛ افحص Actions حياً.
- **direct APK URL / direct pack URL:** لا تضع رابطاً تخمينياً، ولا تعتبر صفحة ZIP رابطاً APK مباشراً.
- **delivery verdict:** WAITING_FOR_WORKER_REVIEW.
- في حالة **NEED_BUILD واحد على الأقل** مع تغيّر driver/host حقيقي، راجع كلفة وتجارب CI وبناء واحد فقط. إن تغيّر testpack فقط، صدّره للاستخدام في APK الموجود دون إعادة build. أصوات «NO_BUILD» لا تمنع الحاجة المبررة لعامل آخر.
