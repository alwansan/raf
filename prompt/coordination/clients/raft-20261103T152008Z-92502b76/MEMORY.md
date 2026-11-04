# W2 memory — raft-20261103T152008Z-92502b76

## الهدف
استعادة ظهور اللعبة والألوان عبر تحليل مراجع Material→Shader/Texture الخارجية، وبناء قاعدة أدلة مجمعة (aggregate-only) تدعم إصلاح فقدان الألوان والأسطح الشاحبة. نطاقي: فقدان الألوان/الخامات/المراجع؛ لا أفترض أن الماء سبب كل الأعراض (W1 قدّم أدلة CL أن بروبس ملوّنة ما تزال ظاهرة مع أسطح شاحبة).

## ما راجعته حياً (2026-11-03T15:20Z)
- prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md (كامل 715 سطر), docs/CURRENT_OWNER_REQUIREMENTS.md, AGENTS.md, prompt/coordination/README.md, UNIFIED_PROMPT_AR.md, TEMPLATES.md.
- HEAD مباشرة عند التسجيل: 891e10a9dcc8b5cc16e66e12457b039e6f6d3086 (commit جديد يتضمن عمل W1 عن الضباب).
- Actions مباشرة: W1 نشط — تشغيلات Depth Copy ShaderLab: 41660417713/41660784743/41661298455/41661873679 FAILED ثم 41662298511 SUCCESS على 891e10a قبل دقائق. لا تشغيلات غير نهائية أخرى عند الفحص.
- تقارير W1 كاملة (W1_GRAPHICS_PROGRAM_RECOVERY وW1_DEPTH_COPY_PASS_RECOVERY)، أعمال A13/A12/A1 من STATUS.
- لا يوجد Release لعبة جديدة؛ lograf-69..73 لوغات فقط. APK80 (9462f8ed/11assets) ما زال الأحدث المثبت.

## الهوية (بروتوكول coordination)
- client_label: W2 — username: raft-20261103T152008Z-92502b76
- الجلسة: w2-20261103T152008Z-92502b76
- الاستعادة: اقرأ RESTORE_AR.md في مجلد الهوية ثم UNIFIED_PROMPT_AR.md.

## أدلة مدخلات معتمدة محلياً
نسخة اللعبة بنسخة الجلسة تحتوي نفس الملفين المعتمدين في LFS؛ تحققت SHA256 محلياً بدون أي تنزيل LFS:
- Raft_Data/resources.assets = 111533516 bytes SHA256 87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c (مطابق للمالك المعتمد)
- Raft_Data/sharedassets0.assets = 115978112 bytes SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3 (مطابق للمالك المعتمد)
- موجودة محلياً أيضاً: ملفا .resS، جميع sharedassets* وlevels وglobalgamemanagers وRaft_Data/Resources/unity default resources (6 shaders) وunity_builtin_extra (54 shaders)، وglobalgamemanagers.assets (15 shader). هذه الأخيرة استخدمتها فقط كدليل تحقق متبادل ولا تُعد مخرجات LFS.

## حدود العملاء المعلنة
- W1: فك parameter blob entry0 + غلاف ShaderLab 6+3 + مقارنة عددية — لا أكرر ولا أعدّل ملفاته.
- A12: تقاطع أسماء الشيدرات المدمجة 198 — لا أكرر.
- A13: أنهى الروابط الداخلية (358/358، 48 شيدر محلي) وترك خطوة محددة: حل 156 مرجع خارجي عبر جداول m_Externals — أنفّذها الآن مباشرة من نتيجته، بلا إعادة تنزيل LFS.

## نتيجة 15:45Z — تجربة أولى محلياً (تجربة حاسمة)
**التصنيف محسوم: جميع الـ156 مرجع Material→Shader الخارجية تُحل بالكامل.**
- الاصطلاح الصحيح: `external_id = m_FileID - 1` (1-based). الدليل: (أ) كود UnityPy PPtr.deref نفسه يستخدم m_FileID-1، (ب) التحقق المتبادل: تحت 0-based لم يوجد أي pathID شيدر داخل ملف المدمج الفعلي (0/156)، وتحت 1-based تحققت الوجود الفعلي 156/156.
- التوزيع:
  - resources.assets (149): 142→شيدرات مخصصة داخل sharedassets0.assets (وجود pathID مُثبَت)، 7→`Library/unity default resources` مدمجة (وجود مُثبَت).
  - sharedassets0.assets (7): 2→globalgamemanagers.assets (وجود مُثبَت)، 5→`Library/unity default resources` مدمجة (وجود مُثبَت).
  - المجموع: 142 مخصصة + 14 مدمجة = 156 (كلها موجودة، صفر روابط مفقودة).
- **الدلالة للألوان:** فرضية «روابط شيدرات مكسورة تسبب الأسطح الشاحبة» مرفوضة بهذا الدليل. الروابط الداخلية 358/358 سليمة (A13) والخارجية الآن 156/156 سليمة. يبقى قيد الفحص: الخامات (texture PPtrs)، sRGB/color space، أجسام برامج الشيدر ذاتها (نطاق W1)، render states، ودقة/تطبيع القنوات.
- قيمة إضافية لـW1: جدول المواد الـ142 في resources.assets التي تشير إلى شيدرات sharedassets0 (مع تحقق مستوى الكائن) يعطيه ربطاً موثوقاً برنامج-شيدر ↔ المواد المستهدفة.

## الملفات التي أنشأتها/سأعدّها
- هويتي وwork record وexperiment وdiscussions في مسارات prompt/coordination الخاصة بي فقط.
- scripts/probe_w2_external_material_shader_refs.py + tests/test_w2_external_material_shader_refs.py + .github/workflows/raft-w2-external-material-refs.yml (اسم/مجموعة concurrency مستقلة W2، cancel-in-progress:false، ميزانية معلنة).
- docs تقرير W2 + تحديث STATUS.md مع الدمج من أحدث HEAD.

## Cleanpoint الأخير / الخطوة التالية
الحالة عند آخر checkpoint (2026-11-03T15:50Z): السكربت الرسمي والاختبارات قيد التجهيز؛ ثم workflow ثم دفع ومراقبة CI؛ ثم رسالة نتيجة لـW1 وA13 وتحديث STATUS. الملفات الثنائية الأصلية لا تُرفع ولا تُسمّى كائنات فردية؛ النشر aggregate-only.

## الرسائل المقروءة
- W1 depth-shaderlab-wrapper work record + state.json (15:02Z) + تقريراه + تشغيلاته الحية.
- A13 original-material-links work record + تقريره (خطوته التالية هي نطاقي المباشر).

## تحديث 16:08Z — نتيجة مكتملة + تصحيح تنسيق
- **النتيجة (local authenticated run):** 156/156 مرجع Shader خارجي تحل (142→9 شيدرات مخصصة داخل sharedassets0، 7+5→`Library/unity default resources`، 2→ggm.assets)؛ 159/159 مرجع Texture خارجي يُحل داخل sharedassets0؛ تحقق وجود فعلي 315/315 (0 مفقود)؛ 0-based مرفوض بالأدلة (0 نجاح/310 اختلافات/5 خارج جدول).
- **الفرضية المرفوضة (بمثابة إصلاح إدراكي):** «مراجع خارجية غير محلولة تسبب الأسطح الشاحبة» — مرفوضة بالدليل؛ كل الروابط سليمة.
- **الفرضية المرفوضة الثانية:** اصطلاح الفهرسة 0-based — رُفض بالتحقق الوجودي.
- **تعارض مؤقت مع W3:** كُشف عند rebase على bdb6ca9؛ نشر W3 سابق؛ أعيد تصنيف عملي تحققاً مستقلاً، الأرقام مطابقة 100% عند كل تقاطع (144/12/11). الحادثة متوثقة: incidents/raft-20261103T152008Z-92502b76/2026-11-03T160500Z-race-with-w3.md مع رسالة موصولة إلى W3 وW1 وA13.
- **تشغيل W1:** تشغيله Unity asset bundle الموجّه 41663393724 يسجَّل لي مكتمل SUCCESS على head_sha 2467c031 — ليس APK كاملاً ولا قبول جهاز؛ بانديل أصل شيدر واحد فقط.
- مخرجاتي في الفرع قبل الدفع: scripts/probe_w2_external_material_shader_refs.py + tests (19/19) + workflow raft-w2-external-material-refs.yml + docs/W2_EXTERNAL_MATERIAL_SHADER_REFS_2026-11-03.md + سجلات coordination.
- **الخطوة التالية:** بعد سقوط CI الأخضر أتحوّل إلى مسار مستقل غير متقاطع: فحص ضبط الألوان وصيغ الخامات (sRGB/color space/TexEnv scales) لأعراض فقدان الألوان.

## تحديث 16:55Z — CI أخضر للمسار الأول + مسار فضاء الألوان
- **CI:** 41671654138 COMPLETED SUCCESS @ 50cf650 (aggregate-only artifact 1052 B) — تصنيف المراجع الخارجية CI-verified. Commit أійсمه الدفعي wraps: 50cf650, ثم docs CI a7689df.
- **نتيجة مسار فضاء الألوان (local run):** الأصلي **Linear** (m_ActiveColorSpace=1؛ محرك Unity Gamma=0/Linear=1)، gamuts=[0]، إصدار المحرك 2021.3.45f2، 5 طبقات جودة (textureQuality 3/2/0/0/0).
- **سبب مرشح من الدرجة الأولى:** بناء Gamma على أندروود لمشروع Linear أصلي = أسطح شاحبة مباشرة. أعلى من فرضية مرجعية مرفوضة.
- ملفات المسار: scripts/probe_w2_color_space_settings.py + tests (11/11) + workflow raft-w2-color-space-settings.yml (بلا LFS، SHA gate) + docs/W2_COLOR_SPACE_SETTINGS_2026-11-03.md.
- **الخطوة التالية:** CI أخضر للمسار الثاني ثم micro-lane تنسيقات الخامات وصيغ sRGB في المالكين.

## تحديث 17:45Z — CI فشل ثم أُصلح + حلقة خامات مكتملة محلياً
- **حادثة CI:** 41673021263 فشل (UnityPy مستورد على مستوى ملف قبل تثبيته)؛ الإصلاح: استيراد مؤجل + حقن وحدة زائفة في الاختبارات؛ الملف دُفع 2334195؛ إعادة التشغيل انتظار.
- **حلقة خامات (local):** مزيج sRGB/linear في المالكين: resources 153 sRGB/255 linear (408)، sharedassets0 265/858 (1123). أي بورت لا يُعيد التقسيم + الشيدر العامة Linear يفقد الألوان.
- ملفات: probe_w2_texture_color_formats + 6/6 اختبارات + workflow يغ+docs+سجلات + رسالة W1.

## تحديث 18:05Z — كل سباقات W2 الثلاثة أخضر
- سباقات CI: externals 41671654138 SUCCESS، color-space 41673884477 SUCCESS (بعد إصلاح 41673021263)، texture-colors 41674316772 SUCCESS @ a52841e.
- سلسلة فقدان الألوان كاملة وموثقة: لا روابط مكسورة + مشروع Linear + مزيج sRGB/linear لكل خامة.

## تحديث 18:50Z — أربعة أسباقات CI أخضر
- material-property-stats 41676717657 SUCCESS @ a57127e. كل حلقات W2 الأربع CI-verified: externals 41671654138، color-space 41673884477، texture-colors 41674316772، matprops 41676717657. سلسلة قيود البورت مكتملة.

## تحديث 19:25Z — الحلقة الخامسة: التقسيم اللوني كامل اللعبة (82 مالكاً)
- 82 مالكاً خليد الهويات (3 LFS: resources, sharedassets0, sharedassets36؛ 79 tracked-regular blob). manifest بالهشتاجات في docs/W2_FULLGAME_TEXTURE_COLORS_2026-11-03.json.
- 4,050 خامة كاملة العب (37 مالكاً مع خامات): 1,173 sRGB / 2,877 linear (28.96%/71.03%). خاتمة: تقسيم اللون لكل خامة يمتد لبقية اللعبة.
- سكربت/8 اختبارات/workflow قيد الدفع + سجلات + رسالة W3 بالاستدامة في حقل formats N1.

## تحديث 20:00Z — الحلقة الخامسة CI أخضر بعد إصلاح مصدر الهوية
- first CI 41682133693 فشل fail-closed (الهوية من worktree مهترئ بدل HEAD)؛ الإصلاح 8130cda: قراءة المسجل دائماً من `git show HEAD:<path>`؛ اختبارات 9/9 مع helper git حقيقي؛ rerun 41683656843 SUCCESS: 82 مالكاً، aggregate مكتوب، artifact 5640 B.
- خمس حلقات W2: الأرقام موثقة في CI أو بتسلسل هوية محلي موثق (الحلقة 5 CI-verified الآن أيضاً).

## تحديث 08:15Z (4 نوفمبر) — الحلقة السادسة: صبغ المواد + تحول الليل الحي
- **Ball الليلة:** W1 ← تصدير وثائق المواد (native 41741108965 FAILED قبل Unity، builtin 0/142؛ then original Material Shader graph resolved 1544/1544 في 16 providers CPU 41748891281 SUCCESS)؛ عميل جديد W4: سجلات أخرى ببناء كامل قيد التشغيل (41808015938 full APK+OBB+XAPK in_progress @ 6ed699c) — لا تُمسك ولا تُسهل سحقه.
- الحلقة السادس (tints): من 514، **494 (96.1%) صبغة غير الهَويّة**؛ _EmissionColor (103/321) إالخ؛ CI قيد الدفع؛ baseline إحصائي لتحقق الصادر من وثائقك (W1) وW4.

## تحديث 09:00Z (4 نوفمبر) — سباق الصبغات أخضر
- material-tint-stats 494/514 (96.1%) صبغة غير الهَويّة؛ CI 41809748671 SUCCESS @ 6ea3310. الحلقة السادسة مكتملة؛ سلسلة W2 الست كاملة CI-verified (باستثناء الحلقة 5 بمॷ تأكيد مستقل تحققاً مستقلاً + إحتوى CI لاحق).

## تحديث 09:20Z (4 نوفمبر) — إغلاق الدورة
- دفع ccfe0b7/b5c44a9 بعد rebase (خطأ GitHub العابر حُلّ): 5ce6955/d14d6ea على قلعة c38f036.
- حيّ: W4 build 41808015938 in_progress @ 6ed699c؛ A5 HAPTICS-008 + startup-integration in_progress؛ Blur-4e91 CPU failure مكرر (ليس مساري)؛ preflight أخضر.
- W2: المسارات الستة كلها CI-verified. بعدها: heartbeat فقط حتى نزول وثائق مواد W1 أو إتمام بناء W4 لاختبار خط الأساس الصبغي.

## تحديث 10:00Z (4 نوفمبر) — نتيجة بناء W4 + مسار سابع
- **W4 full build 41808015938 => completed/failure @ 6ed699c** (jobs: gate+license preflight نجحا، reconstruct فشل، delivery failure). مراقبة سلبية فقط؛ لا تدخل. خط الأساس الصبغي يبقى صالحًا لأي إعادة محاولة بناء.
- نشاط ليلي آخر: W3 fallback/custom-editor enumeration على 165 shaders؛ إصلاحات Blur-4e91 جارية لعملاء آخرين.
- مسار W2 السابع: baseline إعدادات أخذ عينات الخامات (wrap/filter/aniso/mip) — أرقام فقط، غير متداخل.

## تحديث 10:35Z (4 نوفمبر) — الحلقة السابعة: إعدادات أخذ العينات
- 4,050 خامة: Repeat 3,434 / **Clamp 616 (15.2%)** (sharedassets0 603, sharedassets1 230, resources 184)؛ Bilinear 3,979؛ aniso=16 على 54؛ **mipbias صفر وmips stripped صفر لكل الوحي** (سرية fail-closed مباشرة)؛ 7 مالكين بwrap غير موحّد لكل محور.
- بناء W4 الكامل فشل (41808015938, reconstruct) — مراقبة سلبية فقط.

## تحديث 11:45Z (4 نوفمبر) — الحلقة السابعة أخضر
- texture-sampler-settings: CI 41811800655 SUCCESS @ 1bfbbc8. سلسلة W2 الآن سبع حلقات كلها CI-verified (refs→Linear→split-خامات→queue/keywords→4,650 لعبة-كاملة→صبغات→أخذ عينات).

## تحديث 12:25Z (4 نوفمبر) — الحلقة الثامنة: روابط الخامات في المواد
- W4 trial 41812889049: **water-gate نجح، Unity import جارٍ** — مراقبة سلبية فقط.
- الحلقة 8 (bindings): 1,556 مادة/18 مالكًا (يطابق مقياس 1,544/1536)، 4,583 ربطًا (5,663 null)؛ أبرز _MainTex 864/_BumpMap 714/_MetallicGlossMap 623؛ **417 مرجعًا خارجيًا عبر 11 فهرس m_FileID** (2:159, 5:189, 6:24…) — الخارجية والإعداد الخارجي يجب أن ينجو الاثنان معًا؛ 2 مالكين مواد بلا روابط (legitimate)؛ CI قيد الدفع.

## تحديث 13:20Z (4 نوفمبر) — الحلقة الثامنة أخضر
- material-texture-bindings CI 41817287992 SUCCESS @ 0e2342a. سلسلة W2 الآن **ثماني حلقات** كلها CI-verified.
- المرايا المباشرة على أي بناء/تصدير: Linear+split، صبغات 494/514، أخذ عينات (Clamp 616/4050، aniso16=54، mipbias=0، مipsstripped=0)، روابط 4,583 + خارجية 417 عبر 11 فهرسًا.

## تحديث 14:35Z (4 نوفمبر) — الحلقة التاسعة: الخصائص العددية
- 1,556 مادة: 33,899 float عبر 486 اسمًا؛ **رباعية وضع الرندر** (_Mode/_SrcBlend/_DstBlend/_ZWrite) ×1,438؛ _Cutoff 1,457؛ **m_Ints فارغة في اللعبة كلها** (سرية fail-closed)؛ لا sentinels؛ 19 مادة بلا scalars. CI قيد الدفع.
- تنبيه بيئة: UnityPy يعمل تحت python3.14 (Termux) وليس usr/bin/python3.12 — استدعاء صريح بالمفسر 3.14 مهم.

## تحديث 15:30Z (4 نوفمبر) — الحلقة التاسعة أخضر
- material-scalar-properties CI 41824352163 SUCCESS @ 5adc7bc. سلسلة W2 الآن **تسع حلقات** كلها CI-verified؛ اكتملة كل التجميعات المادية في نطاقي.
- المرايا التسع على أي بناء/تصدير: refs، Linear، sRGB split (2+game-wide)، queue/keywords، صبغات 494/514، أخذ عينات (Clamp 616، mipbias 0، aniso16=54)، bindings 4,583+417 خارجي، scalars 33,899/486+m_Ints=∅.

## تحديث 16:00Z (4 نوفمبر) — heartbeat: برنامج التجميع مكتمل
- لا التزامات جديدة على الفرع؛ W4 trial ممتد بلا تحديث (آلية Unity import طويلة)؛ W5 Blur raster فشل — خارجه.
- تسع حلقات CI-verified تكمل مرايا التحقق المادية والنقية؛ لا مسار جديد مخطط (تفادي تداخل W3/W5)؛ انتظار طلبات تحقق التصدير من W1/W4.

## تحديث 17:10Z (4 نوفمبر) — التسليم أخضر من المحاولة الأولى
- water-shader-stage-bindings CI 41828808987 SUCCESS @ d5205d8. المهمة المستلمة (Spectrum variant recovery + Foam CB binding) مكتملة.
- اكتشافات جاهزة للاستيعاب: pass4 Spectrum مستقل (2 CBs)، vertex مشترك (1,2)، fragment فريد لكل pass، كل الCBs partial=true.
