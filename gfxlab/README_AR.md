# أول مختبر موديل أصلي — GFX-AVATAR-001

الهدف: صورة لاعب/مجسم أصلي **باللون الأبيض** من بيانات ZIP2، لا لعبة Raft كاملة ولا استعادة شيدر. واجهة Unity 2021 ثلاثية الأبعاد: تدوير باللمس، قرص للتكبير، إضاءة ثابتة، نمطان LIT WHITE / UNLIT WHITE وتقرير GPU/الألوان/عدد الـMesh.

## بوابة الأمان
- لا تضع OBJ الأصلي ضمن Git؛ CI يستخرج geometry فقط من providers SHA-pinned في GitHub runner.
- اختيار مصدر PLAYER_LIKE_SKINNED إن أمكن، وإلا ORIGINAL_GENERIC_* (مجسم أصلي لا يُزعم أنه لاعب).
- إذا احتاج الـSkinnedMeshRenderer stream resS غير موجود، يسجل عدم القدرة ولا ينشر وهمًا أو يختار player مقلداً؛ يمكن لاحقاً تطوير hydrate نطاق بايتات mesh الأصلي.
- مشهد Unity build يُنشأ تلقائياً من OBJ بعد استيراده فعلياً؛ لا APK دون `original_geometry_exported` وMeshFilter/Renderer غير صفري.
- الوضع الأول مادة بيضاء Standard، مع زر UnlitWhite لفصل هندسة المجسم عن الإضاءة. لا تعتبر لوناً أصلياً.
- لا APK كامل أو OBB ولا مساس بفريق T1–T5. حزمة التجربة اسمها `com.alwansan.raft.graphicslab` مستقل.
- استخراج الأصل/الإخراج داخل Actions فقط؛ مخرجات CI العامة ملخصات عددية، وAPK واحد فقط للاختبار إذا ثبت import & build/signature.

## GitHub workflow
[`gfxlab-original-white-unity-apk.yml`](../.github/workflows/gfxlab-original-white-unity-apk.yml) على فرع `experiment/android-graphics-rootcause`، شغلته تتبع التغيير في المختبر فقط، لا change في request files للفريق.

## معايير GFX-AVATAR-001
1. SOURCE: ZIP2 عند `15964ea8`، hashes byte matches، GameObject→Renderer→Mesh original linkage.
2. GEOMETRY: OBJ مصدر Mesh.export حقيقي، لا ملف synthetic، عدد vertices/faces حقيقي، لا streams ناقصة.
3. UNITY: imported .obj وبرنامج `Standard` مع scene+mesh/renderer، BuildPipeline actual Android output.
4. DEVICE: المالك يفتح ويشاهد **مجسم كامل**، يتأكد ألا يكون جزءًا منفصلاً فقط، يدور ويكبر، ويجرب LIT/UNLIT، ثم COPY LOG ويرسل تقرير JSON مع لقطة شاشة. لا ترتقي مصدر إلى DEVICE قبل اختباره.
5. بعد نجاح الشاهد البصري فقط نبدأ restore Materials وTexture2D وShader48 الأصلية، قبل تعميم الأداة إلى بقية اللعبة.


## GFX-SHEARS-002..005 — المصدر الأصلي والألوان (10 نوفمبر 2026)

**هوية الهاتف:** الموديل ذو 375 vertices / 420 triangles هو مقص Shears ظاهر في لقطة المالك؛ اسم `original_player_like_skinned` في APK0.1 كان نتيجة تصنيف اسم أحد الآباء، وليس تعريف الجسم نفسه. من فضلك لا تستنتج أن هذا هو نموذج جسم اللاعب.

- [GFX-002 Actions 42705610994](https://github.com/alwansan/raf/actions/runs/42705610994) نجح SHA-source Renderer→Material→Shader→Texture: 1 original Material، 2 SubShader و7 Passes، 9 Texture slots، ثلاث bound وثلاثة bones، normals وUV حقيقية.
- [GFX-003 Actions 42706123513](https://github.com/alwansan/raf/actions/runs/42706123513) أثبت ثلاث صور اصلية: Albedo / Normal / Metallic، جميعها في external resS.
- [GFX-004 Actions 42707235695](https://github.com/alwansan/raf/actions/runs/42707235695) قرأ فقط ثلاث قطع SHA/Git أصلية مجموعها 141,557,760 byte وأعاد بناء ثلاثة PNG أصلية **داخل runner الخاص فقط**، دون نشرها منفردة. قيمة tint أصلية موثقة في runner.
- [GFX-005 Unity colored build](https://github.com/alwansan/raf/actions/runs/42707671345) يختبر 4 حالات: WHITE LIT، WHITE UNLIT، SOURCE ALBEDO على Unity Standard، SOURCE ALBEDO+NORMAL+METALLIC على Unity Standard تقريبي. **لا تعلن APK حتى نجاح BuildPipeline + توقيع + artifact.**
- APK GFX-005 (إن نجح) حزمة منفصلة `com.alwansan.raft.graphicslab.shears`، تنصب بجانب white v0.1 ولا تحذفها.

**حدود قبول:** مجرد عودة لون المعدن/المقبض بواسطة Standard لا يعيد shader الأصلي ذي 7 Passes. ظلاله/اللمعان/depth/culling/compiled variants ما زالت تحتاج استعادة ومقارنة مستقلة بمرجع أصلي. لا توجّه T3 لتغيير shaders الفريق بناء على هذه التجربة دون إثبات مكافأة.


## أحدث حالة GFX-MULTI-022 — 10 نوفمبر 2026
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) SUCCESS: فحص 1,435 link rows / 524 exact variant pairs / 1,275 unique referenced DXBC programs؛ 0 RDEF و0 parameter metadata و0 TextureParams/CB bindings. عائق Material property→DX11 register مثبت عبر جميع البرامج المرتبطة. لا Android shader parity. الجلسة `20261110-GFX-chat-variant-reflection-sweep-23`؛ التالية GFX-MULTI-023 لفحص Material/Texture2D/UV/tint/channel fidelity source-only.


## أحدث حالة GFX-MULTI-023 — 10 نوفمبر 2026
[CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) SUCCESS: 21/21 original Texture2D decoded (53,477,376 pixels), seven materials, all tint white, all UV identity. BaseColor RGB variable; Normal R constant with G/B/A variable; Metallic Alpha variable. Raw texture codes remain uninterpreted; no Shader48/Adreno proof. الجلسة `20261110-GFX-chat-material-texture-semantics-24`؛ التالية GFX-MULTI-024.


## أحدث GFX-MULTI-024 — 2026-11-10
[CI42745536309](https://github.com/alwansan/raf/actions/runs/42745536309) SUCCESS / 139 tests; source-only. Six selected models use 7 material slots but 6 unique original Material21 objects; 21 texture links but 18 unique Texture2D. All 112 floats/14 colors match Shader48 property names. Seven white tints and seven nonidentity secondary color slots; original BaseColor DXT1×5 + DXT5×2, Normal and Metallic DXT5×7, Normal Linear×7, BaseColor+Metallic sRGB×7 each; 21/21 Repeat U/V/W and Bilinear. Unity 2021.3 official enum provenance is recorded. No Shader48 Android equivalence or GPU proof. Session `memory/sessions/20261110-GFX-chat-float-wrap-color-25.md`; GFX-MULTI-025 next.


## أحدث حالة GFX-MULTI-025 — 10 نوفمبر 2026
[CI42746455458](https://github.com/alwansan/raf/actions/runs/42746455458) SUCCESS, 146 tests: source six-model graph includes 7 Material slots/6 unique Material21 and 21 Texture links/18 unique Texture2D, no cross-role texture aliases. Seven white original base tints and seven original `_EmissionColor` named entries are RGB black/Alpha=1, not a lost tint. Source/private only; shader and Android parity remain unproven. Restore from `memory/sessions/20261110-GFX-chat-secondary-color-alias-26.md`. Next GFX-MULTI-026 for original seven-pass render-state and Material queue/keyword metadata.

## GFX-MULTI-026S original seven-pass state census — CI42749148702 SUCCESS (2026-11-10)
Source-only, pinned ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, **154 unit tests** passed after an initial CI42749035585 sparse-checkout test setup failure (4 Unity contract tests looked for omitted Unity assets; source-free-only tests now skip Unity-only contracts when files are intentionally absent). Verified all **7/7** Shader48 source Pass rows have an `m_State` dictionary and tags, with metadata for Cull, ZWrite, ZTest, zClip, Blend separate, alphaToMask, stencil and fog; direct `rtBlend` and generic `colorMask` keys absent. Presence does NOT prove a correct runtime render state or effective Blend/ColorMask behavior. Seven original Material slot rows: instancing enabled 7, shader-default queue -1 in 5, explicit nonnegative queue in 2; `m_ShaderKeywords` direct field absent in 7/7 (not proof there are no keywords in alternate metadata). All source values and IDs private; runner purge successful. Safe artifact [13732363372](https://github.com/alwansan/raf/actions/runs/42749148702/artifacts/13732363372) expires 2026-11-17T03:24:33Z.
- **GFX-MULTI-026 APK build currently NOT completed:** [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) started at commit 818298ce8fcb71d7906f977c5d03cc8d619db57e, Unity 2021.3.45f2 real import/build IL2CPP ARM64 GLES3 is in progress. Six original SHA-authenticated models, 21 texture role links, original color-space vs forced linear diagnostic channel probe added. Package `com.alwansan.raft.graphicslab.channels`, Android minimal standalone APK only. Verify BuildPipeline, signature, package name, SHA256/CRC, artifact, purge before declaring APK issued.
- **Negative evidence:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `devicePixelsVerified=false`, `PCPixelParityVerified=false`. The new channel probe shader `Hidden/GfxLab/ChannelProbe` is independent diagnostic-only GLES3, **not Shader48**. WATER-001, RENDER-002 remain OPEN.
