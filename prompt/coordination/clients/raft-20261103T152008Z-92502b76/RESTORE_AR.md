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

## استرجاع جلسة 3 نوفمبر — الحلقات الأربع المكتملة (بحلول 18:35Z)
- **ظروف التشغيل:** استنساخ `/tmp/opencode/raf-w2`، فرع محلي `w2-work` → دفع `HEAD:feature/android-native-port` عبر credential.helper بـ`gh auth token`؛ تكرار نمط rebase-race: stash (بدون `__pycache__`) → reset --hard على origin tip → pop → اختبارات → commit → push (وإعادة الانتظار لو تحرك tip بين fetch وpush).
- **حليلات أصلية محلية من:** `/root/test/test/raft/Raft/Raft_Data` (نسخة مطابقة للمالكَين المعتمدَين، بلا LFS إضافي).
- **حلقة 1 (externals):** scripts/probe_w2_external_material_shader_refs.py + 19 اختبارا + docs/W2_EXTERNAL_MATERIAL_SHADER_REFS_2026-11-03.md؛ CI 41671654138 SUCCESS @ 50cf650؛ سبق W3 موثق في incidents.
- **حلقة 2 (color space):** probe_w2_color_space_settings + 11 اختبار; **الأصلي Linear (m_ActiveColorSpace=1)، gamuts=[0]، محرك 2021.3.45f2**، 5 طبقات جودة; docs/W2_COLOR_SPACE_SETTINGS_2026-11-03.md; أول سباق 41673021263 فشل fail-closed (استيراد UnityPy قبل التثبيت) ثم الإصلاح: استيراد مؤجل + حقن وحدة زائفة → 41673884477 SUCCESS.
- **حلقة 3 (per-texture split):** probe_w2_texture_color_formats + 6 اختبارات; resources 408 خامات (153 sRGB/255 linear) وشيعتها سائدة (fmt12 L 151، fmt10 L 98، fmt1 G 66، fmt12 G 63)؛ sharedassets0 1123 (265/858؛ 12 Linear 466، 10 Linear 259، 12 Gamma 243، 4 Linear 133); docs/W2_TEXTURE_COLOR_FORMATS_2026-11-03.md; CI 41674316772 SUCCESS @ a52841e.
- **حلقة 4 (material props):** probe_w2_material_property_stats + 8 اختبارات; 163+351=514 مطابقة A13/W3; 35 من قيد الطابور أُصلياً (2450×29، 3000×5، 5000×1، 2000×2); علم lightmap 4 السائد (140/210); instancing 141/163 & 266/351; DoubleSidedGI 36/9; أشكال الكلمات متباينة لكل المالك; docs/W2_MATERIAL_PROPERTY_STATS_2026-11-03.md; CI 41676717657 (مُسترَجَ أن يأتي).
- **قاعدة التنسيق الثابتة:** أرقام aggregate فقط، لا أسماء مواد/شيدرات/كلمات/IDs؛ هوية W2 <w2@raft-local.example>؛ لا touch لملفات W1/W3/كلون CL؛ نفس نمط النسخ السابقة للاستمرارية.
- **قيود ما بعدها:** NOT_READY / WATER-001 / RENDER-002 / FFT-FORMAT-009 مفتوحة؛ 0/3 reviews؛ المتبقي: امتداد محتمل خامات شخصية مجمّع أو إغلاق heartbeat.

## استرجاع الحلقة الخامسة (19:30Z) — التقسيم اللوني كامل اللعبة
- `scripts/probe_w2_fullgame_texture_colors.py` + 8/8 اختبارات + `raft-w2-fullgame-texture-colors.yml` + `docs/W2_FULLGAME_TEXTURE_COLORS_2026-11-03.{md,json}`.
- 82 مالكاً (42 `*.assets` + 40 مستوى بلا امتداد) متحقق هوية من المستودع نفسه: 3 LFS pointer-oid + 79 tracked-regular blob؛ أي خلاف هويّة يفشل فوراً دون أي مخرجات.
- النتيجة: 37 مالكاً فقط يحمل خامات، **4,050** خامة (1,173 sRGB / 2,877 linear)؛ التقسيم يمتد للخامات في ملفات مستويات levelN.
- CI 41682133693 @ 8e0c9dc: عبر كاش W1 للمالكين الاثنين + تهيئة fresh لـ`sharedassets36.assets` (110MB)؛ الاختبارات قبل any serializer (استيراد UnityPy مؤجل داخل aggregate_owner).
