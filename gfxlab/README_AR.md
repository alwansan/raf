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
