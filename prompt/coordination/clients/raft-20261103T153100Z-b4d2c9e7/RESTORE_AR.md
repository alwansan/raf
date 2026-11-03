# W3 RESTORE_AR.md — استعادة عمل W3 في جلسة جديدة

- username: `raft-20261103T153100Z-b4d2c9e7` (client_label: W3)
- آخر session_id: `w3-20261103T153254112Z-9f3c1a85`
- آخر commit معروف عند الإيقاف: انظر state.json بعد الدفع؛ base_sha: `153edf140d17cac8c2552a998a2f0ed104e0cb71`

## رسالة الاستعادة (انسخها في الجلسة الجديدة)

استكمل عمل عميل W3 في https://github.com/alwansan/raf فرع feature/android-native-port فقط. الهوية: `raft-20261103T153100Z-b4d2c9e7` (client_label W3، ذاكرة prompt/coordination/clients/raft-20261103T153100Z-b4d2c9e7/MEMORY.md). حدث session_id لكل دورة جديدة ولا تستخدم هوية عميل آخر ولا تكتب فوق سجلاتهم؛ تحقق حياً من HEAD وActions وأنشطة W1 (`raft-20261103T162900Z-73e8c2a1`) وA2/A13 قبل أي كتابة، واستخدم expected SHA دون force.

السياق الجوهري: القرص المحلي في المسار الحالي يحتوي أصول اللعبة الأصلية الكاملة (Raft_Data، 7.3GB) وملفا LFS الموثقين يطابقان بصمات المشروع بدقة: resources.assets `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c` وsharedassets0.assets `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` — نفّذ تجاربك عليها محلياً دون تنزيل LFS.

الإنجاز الأخير: أربع خطوات لسلسلة المظهر مكتملة ومُدفوعة — (1) حسم 144 من 156 ربط Material→Shader (SHA `b15ab149…`)، (2) جرد اللعبة الكامل 82 مالكاً (SHA `d80256a7…`)، (3) مخطط خصائص/keywords للأهداف الـ11 (SHA `7a698ec2…`)، (4) تدقيق استخدام keywords لكل خامة: 1282 خامة مطابقة للجرد، **صفر مخالفات اتساق** (كل m_ValidKeywords جزئية من m_KeywordNames)، بصمة Standard 7/37، وبقية الشيدرات المصممة خصيصاً كل خاماتها بلا keywords (SHA `3e1ebc2…` docs/W3_PER_MATERIAL_KEYWORD_USAGE_2026-11-03.json).

خطوتك التالية المقترحة (بعد قراءة حية):
1. تسليم كل من ميزانية الخطوة 3 وبصمات الخطوة 4 لـW1 كمدخل مباشر (بوابة) لأي إعادة بناء ShaderLab — مناقشة مرتبطة بالدليل فقط، لا تعديل لملفاته.
2. أو تدقيق 22 خامة Standard بلا keywords (جمهور الـvariant الافتراضي) وشيدر StandardVColor (sharedassets36:880).
3. أو خريطة ربط m_NonModifiableTextures داخل المالكين الموثقين، أو تعداد m_FallbackName/m_CustomEditorName.

لا تعلن جاهزية اللعبة، لا تُغلق WATER-001/RENDER-002/FFT-FORMAT-009 بلا دليل، حافظ على .meta/GUIDs، لا تبدأ Unity/APK/Release، ولا تعدل ملفات الطلب المجرّبة أو المهام المجدولة.
