# W2 — استعادة جلسة العمل

- المستودع: https://github.com/alwansan/raf — الفرع الوحيد للكتابة: feature/android-native-port
- هويتي: client_label **W2** ، username **raft-20261103T152008Z-92502b76**

## طريقة الاستعادة
1. اقرأ الحية أولاً مثل كل جلسة: prompt/README.md وprompt/CONTINUE_RAFT_AR.md وprompt/STATUS.md (كاملاً) وdocs/CURRENT_OWNER_REQUIREMENTS.md وAGENTS.md ثم prompt/coordination/README.md وUNIFIED_PROMPT_AR.md وTEMPLATES.md.
2. استعرض HEAD وActions مباشرة (جميع الحالات غير النهائية، الإصدارات) ولوغات CL للقراءة فقط: https://github.com/alwansan/CL/tree/main/raft%20log
3. اقرأ ذاكرتي: prompt/coordination/clients/raft-20261103T152008Z-92502b76/MEMORY.md وstate.json وwork/experiments/discussions في مساراتي (`raft-20261103T152008Z-92502b76`). لا تكتب في ذاكرة W1 ولا تستخدم هويته.
4. إن كان session_id الحي آخر heartbeat نشطاً وأنشئ هوية/جلسة جديدة مرتبطة بـ resumed_from بدل استئناف هوية قيد العمل.
5. متابعة آخر عمل: حل 156 مرجع Material→Shader خارجي عبر جداول m_Externals (RENDER-002) — أسكربت scripts/probe_w2_external_material_shader_refs.py واختباراته وworkflow الخاص باسم W2.
6. إذا تسلمت الإصلاح المرتقب من W1 (parameter blob + ShaderLab wrapper)، تجنب مجاله (لا تعمل على decode parameter0 أو غلاف Depth Copy) وامضِ في جزء الألوان/الخامات/المراجع.
7. عند أي كتابة: expected SHA بدون force، أدمج من أحدث HEAD، لا تعدل workflow جارياً أو native request أو المهام المجدولة؛ ممنوع main/zip/Unity-Editor؛ لا بناء Unity/APK/OBB/XAPK/Release.
