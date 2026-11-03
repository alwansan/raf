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

## نقطة الاستعادة / الخطوة التالية
راجع HEAD/Actions حيّاً ثم اختر: تقرير أولويات W1 (تم عبر مناقشتين)، **توسيع الحسم للعبة كاملة (تم — جرد 82 مالكاً، 1556 خامة/165 شيدر، كل الإحالات 1556 محسومة، الأدلة W3_FULL_MATERIAL_SHADER_INVENTORY_2026-11-03)**، أو تدقيق خصائص/ألوان خامات الشيدرات المتأثرة (الخطوة التالية المقترحة: Standard 2398 / Skin_Amplify 2416 / BlockPaint 2424 / FireParticles 2440). لا تعلن مطابقة مظهر ولا إغلاق WATER-001/RENDER-002.
