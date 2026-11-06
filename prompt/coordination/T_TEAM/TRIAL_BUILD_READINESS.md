# تصويت الفريق على طلب حزمة APK/OBB/XAPK تجريبية

**توجيه المالك (6 نوفمبر 2026):** يحدّث كل عامل صفه حسب [البروتوكول](TRIAL_BUILD_POLICY_AR.md). هذا **ليس** ملف الجاهزية النهائية ولا تصريحاً آلياً للبناء.

**round_id:** trial-20261106-r1

**round_state:** COLLECTING

**آخر مصدر حزمة هاتف مختبرة:** e9c358eda01785b65e4eb14f18723da426635628 — Artifact التشغيل [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739)؛ أبلغ المالك أنه دخل العالم وحفظه وأعاد الدخول. **هذا ليس SHA مثبتاً تشفيرياً لملف APK المثبّت على الهاتف.**

**ملاحظة:** عند إنشاء الملف **لم يصوّت أي عامل بعد**. «لم يحدد» لا تعني «لا يحتاج» ولا «يحتاج»؛ على العامل أن يقرر بنفسه من أدلة عمله الحالية.

<!-- TRIAL_VOTES_BEGIN -->
| العامل | القرار | السبب المختصر / سؤال اختبار الهاتف | دليل commit / CI | آخر تحديث UTC | الجولة |
|---|---|---|---|---|---|
| T1 | لا يحتاج | آخر إنجازات FFT اختبارات Vulkan وUnity اصطناعية فقط؛ لم يُدمج إصلاح جوهري لشيدر/Kernel الماء الأصلي بعد حزمة الهاتف، وما زال تشخيص اختلاف Butterfly ممكنًا دون APK جديد | [CI42254539826](https://github.com/alwansan/raf/actions/runs/42254539826)، [CI42261467757](https://github.com/alwansan/raf/actions/runs/42261467757)، [2373a931](https://github.com/alwansan/raf/commit/2373a9310c659520e46479a0373d2b44f0d26134) | 2026-11-06T17:43:16Z | trial-20261106-r1 |
| T2 | لا يحتاج | فحوص Foam الأصلية أثبتت بنية FileIdentifier وShader فقط؛ لم يُدمج بعد إصلاح جوهري لـShaderLab أو CB0 أو رسم الماء يحتاج اختبار Android. يمكن متابعة ربط الخامة بالمصدر دون APK جديد. | [CI42262404131](https://github.com/alwansan/raf/actions/runs/42262404131) و[5f5ba445](https://github.com/alwansan/raf/commit/5f5ba4450209841993c8600534cdc63e097a5de9) | 2026-11-06T17:43:45Z | trial-20261106-r1 |
| T3 | لا يحتاج | ثبتت ترجمة المراحل الأصلية الثماني وبناء أربع نسخ ShaderLab خاصة مكتملة بنيوياً مع تطابق 13 خاصية، لكن لم يثبت استيراد Unity أو اختيار keywords وقت التشغيل أو ربط Material داخل اللعبة؛ لا إصلاح بصري مدمج يحتاج APK بعد | [CI42291454379](https://github.com/alwansan/raf/actions/runs/42291454379) و[f1f15872](https://github.com/alwansan/raf/commit/f1f1587296ec48853b4ef57511291ceb2ee3c23d) | 2026-11-06T20:49:30Z | trial-20261106-r1 |
| T4 | يحتاج | إصلاح التقاط الماوس الفعلي وحماية Android View وepoch مدمجان بعد حزمة الهاتف e9c358ed؛ اختبار الكاميرا النسبية بلا اصطدام بالحواف ومؤشر Raft بالقائمة وتحرير الالتقاط والكيبورد وإعادة فتح العالم على الهاتف مطلوب؛ لا إثبات جهاز حديث | [d234b10e](https://github.com/alwansan/raf/commit/d234b10e431e9b1f416456c5e767d70e49680397) و[CI42204448436](https://github.com/alwansan/raf/actions/runs/42204448436) | 2026-11-06T17:36:00Z | trial-20261106-r1 |
| T5 | لا يحتاج | تكامل OBB وقياس الأداء الحالي فحوص تشخيصية وحواجز مصدر/CI فقط، ولم يندمج من نطاق T5 إصلاح جوهري جديد للرسم أو اللعب يبرر APK مستقلًا؛ يمكن متابعة فحص الأصل والتكامل دون بناء. | [CI42257103707](https://github.com/alwansan/raf/actions/runs/42257103707)، [CI42260528639](https://github.com/alwansan/raf/actions/runs/42260528639)، [CI42263013004](https://github.com/alwansan/raf/actions/runs/42263013004) | 2026-11-06T17:46:28Z | trial-20261106-r1 |
<!-- TRIAL_VOTES_END -->

## قرار T5 للبناء (لا يغيره غير T5)
- **حالة الإجماع الحية:** مراجعة T5 بتاريخ 2026-11-06T17:46:28Z للجولة trial-20261106-r1: أصوات T1 وT2 وT3 = «لا يحتاج»، وT4 = «يحتاج»، وT5 = «لا يحتاج»؛ لم يتحقق الإجماع 5/5. تُعاد قراءة الصفوف عند كل مراجعة؛ هذه لقطة قرار وليست عداداً بديلاً عن الفحص.
- **candidate_sha:** لم يتم اختيار مرشح بناء لهذه الجولة؛ HEAD عند حجز المراجعة `99658d34f59ce64a8f961e942c641882c0750110`، لكنه لا يمثل اعتماداً للبناء.
- **native request / run:** **لا إطلاق** من هذه الجولة. طلب `.github/raft-native-build-request.json` الحالي يعود إلى تجربة أقدم `t5-exact-water-ack-20261105T1543Z-f2c9`، ولم يُعدّل. مراجعة قائمة Actions الحديثة لم تجد بناء Unity مطابقاً جارياً عند هذا checkpoint، لكن ذلك لا يغيّر منع البناء بسبب نقص الإجماع.
- **delivery / signed artifacts:** مصدر الحزمة القديمة المختبرة `e9c358eda01785b65e4eb14f18723da426635628`، التشغيل [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739)، أنجز reconstruction لكن نشر GitHub Release فشل HTTP403؛ لا Release مثبت لهذا التشغيل. الأرشيف المنقذ [42110297871](https://github.com/alwansan/raf/actions/runs/42110297871) artifact `13454900880` ما زال `expired=false` وقت المراجعة، وتنتهي مدته 2026-11-08T21:12:40Z؛ لا ينسب إلى HEAD الجديد.
- **العوائق أو سبب عدم البناء:** القرار الحالي لا يحقق خمسة «يحتاج»؛ T1–T3 ما زالوا في اختبارات أصلية/شيدر غير مكتملة الدمج، ونتائج T5 الأخيرة تشخيصية. لا نسخ APK/OBB/XAPK جديدة بناءً على هذه الجولة، ولا تغيير لبوابات الأصالة أو 3/3 الجاهزية الكاملة.
- **تحديث قرار T5 (UTC):** 2026-11-06T17:46:28Z؛ صاحب المراجعة T5، `origin=chat`، جلسة `20261106T1745Z-T5-chat-trial-vote-adoption-46c2`.

## قواعد سريعة
- القراران المسموحان لكل عامل بعد التقييم: **يحتاج** أو **لا يحتاج**. لا تكتب «يحتاج» بسبب patch صغير، فحص نظري، أو commit وثائق.
- عند «يحتاج» أضف دليل commit مدمج وسؤالاً محدداً لا يمكن الإجابة عنه دون هاتف؛ عند «لا يحتاج» أضف السبب المختصر. حدد الوقت UTC والجولة الصحيحة. لا تستخدم حرف | داخل الخلايا.
- **T5 وحده** يراجع 5/5 في نفس الجولة، صلاحية كل صوت (48 ساعة)، HEAD/CI/last candidate، وجود build/artifact آخر ومخاطر النشر قبل تشغيل بناء واحد. لا تضبط خانة «مجموع الأصوات» يدوياً كبديل للتحقق من الصفوف.
- بعد بدء البناء يضبط T5 round_state إلى REQUESTED أو RUNNING؛ بعد النتيجة يسجل FAILED أو DELIVERED ورابطها ويفتح جولة جديدة بقرار واضح. الأصوات القديمة لا تتحول تلقائياً إلى موافقات جديدة.
- إذا انتهى عملك وصرت تنتظر هاتفاً، استمر في مساعدة العمال الآخرين أو سد عائق بديل؛ لا تتوقف عن العمل.

**فحص اختياري لـT5:** python3 scripts/t_team_trial_votes.py --require-consensus — يفشل عند نقص/قدم/تعارض الأصوات؛ نجاحه لا يشغّل أي بناء ولا يعني READY.

<!-- T5_OWNER_DIRECT_42281310905 -->
## استثناء مستقل: أمر بناء مباشر من المالك — مراجعة T5 بتاريخ 2026-11-06 19:55 UTC

- **هذا ليس تصويت 5/5 ولا تغييرا للأصوات.** الجولة `trial-20261106-r1` تبقى `COLLECTING`: T1/T2/T3/T5 «لا يحتاج»، وT4 «يحتاج». لا تنسب قرار المالك المباشر إلى العمال أو توحي أن إجماعهم تحقق.
- أضاف المالك بنفسه طلبا واضحا في `.github/raft-native-build-request.json`: `request_id=owner-direct-20261106-latest-integrated-trial-xapk-42058825739-01`، `owner_direct_request=true`؛ ينص على أن أمره الأحدث يتجاوز **شرط توقيت تصويت الفريق لهذا الطلب الواحد فقط** دون تجاوز بوابات الأصالة أو توقيع APK أو الوثائق.
- [GitHub Actions **42281310905**](https://github.com/alwansan/raf/actions/runs/42281310905) أطلقه commit مباشر من `alwansan` بتاريخ 2026-11-06 19:37 UTC عبر `push`، **source SHA مستقل ثابت `d692400115c36c4839fa4f4954e5f6ed1c60d413`**، وليس HEAD الحالي.
- **نقطة الفحص 19:54 UTC:** `in_progress`، `native-request-gate=success`، `unity-license-preflight=success`، `reconstruct` جار. ثبت نجاح تصدير 40 مشهدا وB04 Linear وB11 sRGB واستعادة 2021.3.45f2 built-in shaders، ووصل إلى استعادة ScriptableObjects. **لم يحدث بعد Unity Editor APK/OBB/XAPK مكتمل أو تثبيت جهاز، وأية خطوة مستقبلية pending لا تُعد نجاحا**.
- هذا التشغيل بدأ **قبل** إضافة T5 لفحص B46 الفعلي `Material→Texture`، commit `8789a710e21c5cbd48f7bec97a509bbd16a574c3`، وقبل إصلاح تباين أرقام مراحل CI `281aec74d74f31f84d0e5442052e502cfbaa60f0`. لا تدّع إدماج هذه التغييرات في الحزمة من run42281310905، ولا تعيد تشغيل Unity للتعويض أثناء عمله. التغييرات اللاحقة تُفحص لمرشح لاحق فقط.
- **حدود الاستثناء:** لا إلغاء للتشغيل، لا dispatch مكرر، لا تغيير `.meta`/GUID أو شيدرات وهمية، لا تزوير جاهزية 3/3، لا ادعاء Release أو Android GPU قبل تحقق الشروط والأدلة. راجع حالة Actions الحية لا نص هذه اللقطة عند الاستكمال.
- **سجل T5 مستقل:** [`20261106T1950Z-T5-chat-native-stage-shift-4c6b`](../clients/T5/sessions/20261106T1950Z-T5-chat-native-stage-shift-4c6b.md)؛ هذا توثيق مراقبة أصل طلب المالك، وليس تبنيا لتصويت آخر.

<!-- T5_OWNER_DIRECT_42281310905_FINAL -->
## النتيجة النهائية لأمر المالك المباشر (T5 — 2026-11-06T20:36:17.470Z)

- التشغيل الأصلي [42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) انتهى **FAILED** على SHA `d692400115c36c4839fa4f4954e5f6ed1c60d413`: خطوة Unity Editor 2021.3.45f2 import and compile فشلت بسبب **10 أخطاء CS0234** في مراجع `RaftAndroid.Platform.AndroidPhysicalMouseCapture` تحت `UNITY_EDITOR`؛ الفحص سجّل 0 kernel OOM kills. فشل `delivery-result` لاحقًا، وتجاوز `publish-early-test` بالتبعية؛ **لا APK/OBB/XAPK جديدًا** من التشغيل.
- أصلح T4 الشيفرة في [f554e8b6](https://github.com/alwansan/raf/commit/f554e8b6757e46aa037603ed592a04acc2bf7a61)، ونجح [CI42287041110](https://github.com/alwansan/raf/actions/runs/42287041110) و[CI42288563457](https://github.com/alwansan/raf/actions/runs/42288563457) على مراجع Unity2021 الأصلية. دمج T5 [7d1981ae](https://github.com/alwansan/raf/commit/7d1981ae8f349c5afd8a37082982ac2ccd548c03) فحص ترجمة C# Editor وAndroid مبكرًا، بالـDLL الأصلية التي تطابقت Git blob IDs لها بين `feature/android-native-port` وZIP2 المثبت `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، قبل جلب ZIP2 الثقيل وبدء Unity. نجح [CI42288716874](https://github.com/alwansan/raf/actions/runs/42288716874) **20/20** مصدرًا بعد إصلاح اختبار اصطناعي [ec5b73f7](https://github.com/alwansan/raf/commit/ec5b73f716f46ee671e79ab78bee189e4a2e5396)؛ ليست تجربة Unity كاملة أو جهاز.
- الاستثناء السابق للمالك كان **طلب بناء واحدًا** لا موافقة مشتركة. تبقى الجولة `trial-20261106-r1` بحالة `COLLECTING` دون تغيير الأصوات: **1/5 يحتاج**. لا طلب Native جديد ولا إلغاء Actions ولا تغيير `.github/raft-native-build-request.json`. `NOT_READY 0/3`؛ WATER-001/RENDER-002/LOCAL-005 لا تزال مفتوحة.
- سجلات [جلسة T5](../clients/T5/sessions/20261106T2025Z-T5-chat-early-unity-editor-abi-7e2f.md) و[التجربة](../experiments/T5/20261106T2025Z-T5-chat-early-unity-editor-abi-7e2f.json) توثق المصدر والبناء وحدود الأدلة.
