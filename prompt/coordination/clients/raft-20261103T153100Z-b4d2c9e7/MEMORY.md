# W3 MEMORY — raft-20261103T153100Z-b4d2c9e7

client_label: W3 — مظهر/شيدرات/خامات/مؤثرات. session_id لهذه الدورة: `w3-20261103T153254112Z-9f3c1a85`.

## الهدف
تتبع سلسلة المظهر الأصلية من المجسم إلى Material ثم Shader وTexture وخصائصه وkeywords: تكميل أعمال W1 (برامج/ShaderLab) وA13 (روابط الداخلية) دون تكرارهما.

## آخر مصدر راجعه
- الحية: prompt/README.md, CONTINUE_RAFT_AR.md, STATUS.md (كامل), docs/CURRENT_OWNER_REQUIREMENTS.md, AGENTS.md, coordination/README.md, UNIFIED_PROMPT_AR.md, TEMPLATES.md.
- تقارير: W1_GRAPHICS_PROGRAM_RECOVERY_2026-11-03.md, W1_DEPTH_COPY_PASS_RECOVERY_2026-11-03.md, W1_DEPTH_SHADERLAB_RECONSTRUCTION_2026-11-03.md, A13_ORIGINAL_MATERIAL_SHADER_LINKS_2026-11-03.md.
- HEAD عند البدء: 153edf140d17cac8c2552a998a2f0ed104e0cb71 (بعد ff-merge للحياة)، Actions: لا مهام نشطة وقت الفحص (فحص head_sha عبر API عدده 0).

## هويات العملاء المتحقق منها
- W1 = `raft-20261103T162900Z-73e8c2a1` — نشاط حقيقي (commits أخيرة + state paused + تشغيل Unity run41663393724 قيد الانتظار).
- **W2 غير موجود** في سجلات coordination ولا في STATUS.md (تحقق grep)؛ لم أفترض نشاطه.

## اكتشاف بيئي حاسم
القرص المحلي `/root/test/test/raft/Raft/Raft_Data` (نسخة PC أصلية، 7.3GB) يحتوي **نفس ملفي LFS الموثقين**:
- resources.assets = 111,533,516 B، SHA256 `87493249f1adfc0c...c4838595c` (مطابق).
- sharedassets0.assets = 115,978,112 B، SHA256 `0498f738dc86e90e...1628a3c3` (مطابق).
إذن يمكن تنفيذ كل تجارب المظهر على هذين الملفين + بقية sharedassetsN/level0..N محلياً **دون أي تنزيل LFS إضافي**. وثّقت هذه البصمات في evidence قبل أي parse.

## أدلة هذه الدورة
- الحسم: أصل أزاحة 156 ربط Material→Shader خارجي عند A13 = 144 حُسمت إلى شيدرات لعبة حقيقية بأسماء parsed-form + 12 نقل محرك (fail-closed). تفصيل في docs/W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.md و JSON بSHA `b15ab1494db0d17e823201400db8cac5480e6cfc6bc832a402d999cc24b695a2`.
- أبرز أهداف الشيدر: Skin_Amplify=50 خامة (pathID 2416)، SpeedTree8=41 (2405)، Standard=29 (2398)، Hair_Amplify=7 (2448)، Vegetation=5 (2439)، Shimmer=5 (2445)، TMP=2+2، GlassWater=1 (2434)، Azure[Sky]/Fog Scattering=1 وPixel Dynamic Cloud=1 (عبر globalgamemanagers).
- اختبارات اصطناعية 9/9 OK (scripts/w3_test_material_shader_externals.py)؛ negative controls الحقيقية كلها true؛ شغيل محلي موثق ولا يُدَّعى أنه CI.
- تفعيل: `python3 scripts/probe_w3_material_shader_externals.py --game-data <Raft_Data> --aggregate-json <out>`.

## فرضيات مرفوضة/تصحيحات
- `FileIdentifier.path_name` غير موجودة في UnityPy 1.25.4؛ الصحيح `.path` (أصل خطأ أول ثم صُحح قبل النتيجة النهائية).
- اسم الشيدر ليس في m_Name (فارغة) بل في m_ParsedForm.m_Name — نسق مع W1.
- A13 صيغته "156 unknown" محافظة: 142 منها إلى sharedassets0 (ملف عندها!) و2 إلى globalgamemanagers.

## رسائل مقروءة
 coordination/clients/* (state/memory), docs/W1_*, docs/A13_*, STATUS.md كامل. حظر تعديل سجلات الغير منه.

## ملفات غيّرتها
- scripts/probe_w3_material_shader_externals.py (جديد), scripts/w3_test_material_shader_externals.py (جديد),
- docs/W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.{md,json} (جديد),
- prompt/coordination/clients/raft-20261103T153100Z-b4d2c9e7/* (جديد),
- prompt/coordination/work/RENDER-002/raft-20261103T153100Z-b4d2c9e7-externals.json,
- prompt/coordination/experiments/raft-20261103T153100Z-b4d2c9e7/material-shader-externals.json,
- prompt/coordination/discussions/RENDER-002/2026-11-03T154500Z-raft-20261103T153100Z-b4d2c9e7-externals-done.md,
- prompt/STATUS.md (قسم جديد).

ملاحظة اليوم (2026-11-04): سلالة ليلية للعميل W4 (تصدير/بناء/طلب XAPK تجريبي، تشغيل 41808015938) ومتابعات W1 — مسارات أخرى، لا لمس ولا تحقق ولا دعى.

## نقطة الاستعادة / الخطوة التالية
تسع خطوات W3 مكتملة (الثامنة والتاسعة بانتظار القياس النهائي دفعة واحدة): (1) حسم 144 من 156 (SHA `b15ab149…`)، (2) جرد اللعبة الكامل (SHA `d80256a7…`)، (3) مخطط خصائص/keywords (SHA `7a698ec2…`)، **(4) تدقيق استخدام keywords لكل خامة (SHA `3e1ebc2…`; صفر مخالفات، 1282 خامة، بصمة Standard 7/37 والبقية أصغر)**. الخطوة 5 (اليوم): تعداد m_FallbackName (52/165 غير فارغ، 10 مميزة، بوجود واحد يغطي 37) وm_CustomEditorName (69/165، 10 مميزة، مهيمن 42) — بلا أي أسماء جديدة، تثبيت هيكلي لعائلات المورد (SHAs 8cfe2c94/4b0df353، الأداة 47b2ba67). الخطوة 11 (اليوم): تجانس zip2 — ميتاداتا 82/82 متساوية fail-closed (docs 7ba7d51a)؛ إثبات بايتي للملفين المثبتين من تدفق أجزاء raw@zip2 (docs 46e281cc)؛ مثلث الهوية المحلي⇄LFS⇄zip2 مغلق. اكتشاف: 5 أشجار أجزاء على zip2 (الملفان المثبتان + sharedassets36 + level30/34)؛ المستويات bare-name عند الفرعين؛ level30/34 باينات مباشرة على feature وأشجار على zip2. إلغاء انقطاع الشبكة: إعادة تشغيل نظيف لكامل الشارحة (الكشف لا يعاد الدمج). الخطوة 10 (اليوم): مسار تحقق Actions مصرح به من المالك — workflow `w3-verification.yml` (ubuntu-24.04 مثبّت، LFS منه للملفين فقط، lint guard ملتزم) + بروسبيت `w3_probe_pin_verification.py`؛ run **41828539269 SUCCESS** على `0666860`: كل الأجنحة خضراء بUnityPy 1.25.4 و`all_pins_verified: true` (أرتيفكت 498B). محاولتان بصدق: الأولى `c65e2719` فشل job B بسبب استمرارات أسطر YAML + شرط lint (ثُمّت سطراً واحداً وليبل مثبّت). الخطوة 9 (اليوم): schema للأهداف غير المسماة الـ65 — إغلاق قصة schema للعبة كلها (77/77 مطابقة ضد أداة الخطوة 7، التزامات فقط؛ الأداة 1ad59542)؛ histogram مجمّع Texture 229/Float 229/Range 206/Color 73/unknown 24؛ 6 أهداف بلا مسارات نسيج. ملاحظة بيئة: المضيف غيّر تفضيل python3؛ UnityPy متاح فقط في python3.14 (`/data/data/com.termux/files/usr/bin/python3.14`). مصادقة المالك على تجارب Actions وفرع zip2 (ملفات اللعبة كاملة في Raft/) للخطوة 10. الخطوة 8 (اليوم): إحصاء الجُمَعات الصغيرة — StandardVColor (880): 18/18 بلا keywords وتغطية 18/18 (schema 26kw/5slots، commitments 55d51555/931a27f0) وجمهور Standard الافتراضي **22/674** بالضبط مع توزيع المالكين أعداداً (الأداة 71ad7665)؛ الاستخدام الفعلي للون الرأس بيانات شبكة — لم يُقرأ وترك مكشوفاً. كل الخيارات المسجلة استُنفدت. الخطوة 7 (اليوم): إغلاق اتساق keywords على مستوى اللعبة كلها — 1556 ممشية، 1540 مدققة (66 هدفاً غير أولوية بخاماتها 258)، صفر مخالفات عالمياً؛ بوابة الكلمات مغلقة بالاكتمال (الأداة df1dbdc8). الخطوة 6 (اليوم): تدقيق اكتمال ربط m_SavedProperties على مستوى البنية — 1282/1282 خامة تحمل كل المسارات المعلنة (صفر فجوات/زيادات؛ الأداة c16d7892؛ إفصاح تراجع: مستخرج dict-form تجاهل صيغة tuples صمتاً — أصُلح ونُشر المصحح فقط). الخيارات القادمة: تدقيق 22 خامة Standard بلا keywords (جمهور الـvariant الافتراضي)، أو StandardVColor (sharedassets36:880) vertex-color. لا مطابقة مظهر، لا إغلاق WATER-001/RENDER-002؛ الأسماء تبقى commitments فقط.
