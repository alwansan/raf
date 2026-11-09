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
