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
