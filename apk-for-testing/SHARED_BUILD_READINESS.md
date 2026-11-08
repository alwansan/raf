# جاهزية بناء APK المختبر المشترك — T1–T5
**مختلفة تماماً عن** `prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md` الذي يخص XAPK لعبة Raft الكاملة. اقرأ [السياسة](UNIFIED_LAB_POLICY_AR.md).
**shared_round_id:** shared-20261108-r1
**build_decision:** T5_REVIEWING — صوت T5 واحد NEED_BUILD بسبب تغيير host Java حقيقي؛ لم يُطلب CI بعد. بناء Mini واحد فقط بعد تأكيد عدم التكرار.

| العامل | القرار | لماذا؟ وما الاختبارات/التغييرات؟ | evidence SHA/CI | وقت UTC | الجولة |
|---|---|---|---|---|---|
| T1 | NEED_BUILD | Bounded EGL startup fix in compiled T1ComputeProbe now prevents early synthetic Compute assertions before onSurfaceCreated (7s deadline/100ms poll). T1-01..04 need one shared Mini APK device test on Adreno; this is a driver/source change, not importable JSON. Unity original FFT and Raft water remain unverified; no standalone T1 APK. | source d83a4e4379fb8677daebea81da203281a1d89e82; test 2f26cd2e241a584fbd44d8d9343d2736584fc956; shared Java/pack CI 42509359669 SUCCESS at 695daa697b0ccc0e53ed0533f43b2d267e0036f5 | 2026-11-08T18:19:51Z | shared-20261108-r1 |
| T2 | NEED_BUILD | Compiled T2-02 GLES FBO probe now asserts two distinct spatial regions with actual pixel readbacks from both FBO stages; prior single-color check could not detect spatial sample collapse. Requires unified javac gate, then one T5-reviewed shared APK/device check of T2-01..04. No independent T2 APK request; WATER-001 original ShaderLab remains OPEN. | source 73924c998d91eb64be33c883d9922d44981accd4; source/host-model 7/7 checks PASS; shared javac CI 42504045625 is older than patch (NOT new verification) | 2026-11-08T18:19:00Z | shared-20261108-r1 |
| T3 | NEED_BUILD | Compiled shared T3 GLES driver now validates exact same-case frame/readback/GL errors and PixelCopy generation for T3-01..06; this is NOT deliverable by JSON pack alone. Source-only 26/26 checks pass; new Java compile, Android screenshots, Unity/Raft visual acceptance still unverified. T5 only may evaluate ONE shared Mini APK after CI/signature/Actions review. | T3 commits 204dabb9, 6bb0b165, c0a2213b; source audit 26/26; old CI42504045625 predates fix | 2026-11-08T18:24:00Z | shared-20261108-r1 |
| T4 | NOT_REVIEWED | يبدأ T4 بالمراجعة بنفسه | — | — | shared-20261108-r1 |
| T5 | NEED_BUILD | Unified host Java fix: file SHA EVIDENCE_READY retained, FAIL/BLOCKED remain pending, force rerun explicit; certificate SHA256 and package assertion added. First shared APK still unbuilt. Need one Android15 device trial of T5-01..02 and UI state persistence, not Unity evidence. | https://github.com/alwansan/raf/commit/f6cb665f01770778c7e2f699e0f132ec57e9a334 ; JVM 20/20 local, regression source https://github.com/alwansan/raf/commit/6145c7231d6dd7afb63b07f520920b87c366ccc2 | 2026-11-08T18:24:32Z | shared-20261108-r1 |

## T5 — سجل قرار بناء المختبر فقط
- **latest_shared_apk_sha256:** لا يوجد منشور موحد حتى الآن.
- **candidate_source_sha:** لم يثبت بعد.
- **pack_sha256:** لم يثبت بعد.
- **native mini request/run:** لا طلب بهذه الجولة؛ افحص Actions حياً.
- **direct APK URL / direct pack URL:** لا تضع رابطاً تخمينياً، ولا تعتبر صفحة ZIP رابطاً APK مباشراً.
- **delivery verdict:** WAITING_FOR_WORKER_REVIEW.
- في حالة **NEED_BUILD واحد على الأقل** مع تغيّر driver/host حقيقي، راجع كلفة وتجارب CI وبناء واحد فقط. إن تغيّر testpack فقط، صدّره للاستخدام في APK الموجود دون إعادة build. أصوات «NO_BUILD» لا تمنع الحاجة المبررة لعامل آخر.
