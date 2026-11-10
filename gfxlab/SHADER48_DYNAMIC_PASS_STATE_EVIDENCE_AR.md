# Shader48 — دليل حالات الرسم الديناميكية وعائق الربط
**GFX-LAB | 2026-11-10 | ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385**

## حقائق الأصل
- [GFX-MULTI-026S CI42749148702](https://github.com/alwansan/raf/actions/runs/42749148702): Shader48 7/7 original m_State fields موجودة، direct rtBlend/colorMask absent؛ 7 material instancing، 5 default render queue و2 explicit.
- [GFX-MULTI-028S CI42749968983](https://github.com/alwansan/raf/actions/runs/42749968983): **كل** Cull/ZWrite/ZTest/AlphaToMask `name` ديناميكي (7/7 لكل حقل)، وليس إثبات أن `val` fixed effective state. سبع `m_ValidKeywords` غير فارغة، و`m_InvalidKeywords` فارغة.
- [GFX-MULTI-029S CI42750996280](https://github.com/alwansan/raf/actions/runs/42750996280): 164 اختبارات، full source-only negative controls. أسماء حالات الرسم parseable 7/7، لكن direct Shader48 Property+Material saved Float match لـCull/ZTest/AlphaToMask هو **0/7** و0 لكل واحد. ZWrite يطابق الأصل في **2/7** Passes، ويطابق **14 material-slot-per-Pass** Float entries جميعها 0/1 (2×7)، وليس 14 Material objects.
- Original source private state values/names kept inside CI and purged. `originalShaderRestored=false`, PC/device shader state pixels unverified.

## لا تستنتج
- `source Float m_State.val` أو `rtSeparateBlend=false` أو غياب direct `rtBlend` لا يثبت أن GPU عطّل/فعّل Cull/Blend/Depth.
- `m_ValidKeywords` nonempty لا يعني keyword list مطبّقة بشكل صحيح من دون ربط compiled variant/pass.
- فشل تطابق الاسم مع 27 Shader48 m_Props لا يعني أن أصل الشيدر مفقود أو أن المادة ناقصة؛ قد يكون اسم محرك أو مرجع Compile metadata آخر، يحتاج دليل مستقل.

## خطط المتابعة
1. **GFX-MULTI-030S**: مقارنة `m_State.name` source per Pass مع `m_NameIndices` وper-pass typed metadata (count-only), وتوثيق وجود مرجع صريح أو عائق مفقود.
2. التحقق من original Blend/ColorMask/queue/keyword effective render states، ثم GPU reference/PC parity. لا تستخدم ShaderLab fixed Cull/ZTest/ZWrite defaults بدون هذه الخطوة.
3. احتفظ باستقلال GFX026 diagnostic channel Android APK (not Shader48): [owner handoff](https://github.com/alwansan/raf/blob/experiment/android-graphics-rootcause/gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md). اختبار الجهاز وصور اللوغ ينتظران المالك، لا تعتبر CI compile Pixel proof.
4. Source property→DX11 t/s/CB map وnormal metallic/UV وrig، والماء/النار/الإضاءة تبقى مراحل منفصلة.
5. لا تُنشئ agent عام لاستعادة الأيتمات حتى تعليمات المالك؛ استعد `prompt/graphics-lab/RESTORE_AR.md` و`memory/STATE.json` و`memory/sessions/20261110-GFX-chat-passstate-material-binding-29.md` و`gfxlab/OPEN_WORK_AND_IDEAS_AR.md` أولًا.
