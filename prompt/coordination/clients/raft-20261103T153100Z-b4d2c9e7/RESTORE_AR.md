# W3 RESTORE_AR.md — استعادة عمل W3 في جلسة جديدة

- username: `raft-20261103T153100Z-b4d2c9e7` (client_label: W3)
- آخر session_id: `w3-20261103T153254112Z-9f3c1a85`
- آخر commit معروف عند الإيقاف: انظر state.json بعد الدفع؛ base_sha: `153edf140d17cac8c2552a998a2f0ed104e0cb71`

## رسالة الاستعادة (انسخها في الجلسة الجديدة)

استكمل عمل عميل W3 في https://github.com/alwansan/raf فرع feature/android-native-port فقط. الهوية: `raft-20261103T153100Z-b4d2c9e7` (client_label W3، ذاكرة prompt/coordination/clients/raft-20261103T153100Z-b4d2c9e7/MEMORY.md). حدث session_id لكل دورة جديدة ولا تستخدم هوية عميل آخر ولا تكتب فوق سجلاتهم؛ تحقق حياً من HEAD وActions وأنشطة W1 (`raft-20261103T162900Z-73e8c2a1`) وA2/A13 قبل أي كتابة، واستخدم expected SHA دون force.

السياق الجوهري: القرص المحلي في المسار الحالي يحتوي أصول اللعبة الأصلية الكاملة (Raft_Data، 7.3GB) وملفا LFS الموثقين يطابقان بصمات المشروع بدقة: resources.assets `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c` وsharedassets0.assets `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` — نفّذ تجاربك عليها محلياً دون تنزيل LFS.

الإنجاز الأخير: موقع A13 الخارجي المتبقي حُسمت 144 من 156 ربط Material→Shader (نجاحها موثق في docs/W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.json بSHA `b15ab1494db0d17e823201400db8cac5480e6cfc6bc832a402d999cc24b695a2`) وأبرز القائمة: Skin_Amplify=50 خامة، SpeedTree8=41، Standard=29، Azure[Sky] عبر globalgamemanagers، و12 مرجع محرك فشل مغلق (احترس أن لا تخمّن أسماء للمحرك).

خطوتك التالية المقترحة (بعد قراءة حية):
1. سلّم W1 أولويات برامج الشيدر المتأثرة بمسار مظهر المواد: pathID 2416 (Skin_Amplify)، 2405 (SpeedTree8)، 2398 (Standard) في sharedassets0.assets، عبر مناقشة مرتبطة بالدليل — لا تعدل ملفاته.
2. أو وسّع الحسم لبقية ملفات sharedassetsN وglobalgamemanagers اللدّة (نفس السكربت scripts/probe_w3_material_shader_externals.py مع توسيع PINNED_OWNERS بعد تحقق SHA).
3. أو ألّف تدقيق خصائص/ألوان/keywords الخامات المرتبطة بالشيدرات المتأثرة (vertex colors، sRGB، channels) على الملفات المحلية.

لا تعلن جاهزية اللعبة، لا تُغلق WATER-001/RENDER-002/FFT-FORMAT-009 بلا دليل، حافظ على .meta/GUIDs، لا تبدأ Unity/APK/Release، ولا تعدل ملفات الطلب المجرّبة أو المهام المجدولة.
