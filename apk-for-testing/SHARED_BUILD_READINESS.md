# جاهزية بناء APK المختبر المشترك — T1–T5
**مختلفة تماماً عن** `prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md` الذي يخص XAPK لعبة Raft الكاملة. اقرأ [السياسة](UNIFIED_LAB_POLICY_AR.md).
**shared_round_id:** shared-20261108-r1
**build_decision:** NOT_REQUESTED — لم يراجع T5 الأصوات بعد. أي صوت من العامل **لا يُنشئ طلب بناء تلقائياً**.

| العامل | القرار | لماذا؟ وما الاختبارات/التغييرات؟ | evidence SHA/CI | وقت UTC | الجولة |
|---|---|---|---|---|---|
| T1 | WAITING_MERGE | T1-01..04 are declared and routed to MainActivity via auto_case_id; actual per-case GPU result contract, unified APK integration and phone evidence remain unverified. No T1 driver delta or independent APK request. | source audit 927eb65674db8d7c288d14ec2f0ed54d7562e3ad; historical CI 42497767712 | 2026-11-08T18:07:00Z | shared-20261108-r1 |
| T2 | NEED_BUILD | Compiled T2-02 GLES FBO probe now asserts two distinct spatial regions with actual pixel readbacks from both FBO stages; prior single-color check could not detect spatial sample collapse. Requires unified javac gate, then one T5-reviewed shared APK/device check of T2-01..04. No independent T2 APK request; WATER-001 original ShaderLab remains OPEN. | source 73924c998d91eb64be33c883d9922d44981accd4; source/host-model 7/7 checks PASS; shared javac CI 42504045625 is older than patch (NOT new verification) | 2026-11-08T18:19:00Z | shared-20261108-r1 |
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
