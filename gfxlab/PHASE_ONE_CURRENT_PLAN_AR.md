## 11 Nov 2026 — GFX104 authentic Shader48 DXBC→SPIR-V→GLES310 native interpolation bridge OPEN

**Current restore session:** `memory/sessions/20261111-GFX-chat-original-spirv-interpolation-72.md` (`origin=chat`). The actual owner GFX102 Adreno 730 proved optional NV NoPerspective under GLES GLSL ES310/320 on a synthetic triangle, but **the original Shader48 GPU raster/material/PC pixel proof remains OPEN**. Prior GFX039 **16** original NP declarations and **16** system-interpreted input declarations are not necessarily the same input records or the same denominator as the 524 exact pairs. Never equate them until original source-only stage analysis.

**New engineering:** Hardened GFX103 GLSL native qualifier checker to exclude comments/strings and support centroid/sample qualifier ordering; two additional negative tests. Added `gfxlab/tools/gfx104_spirv_input_interpolation.py` (SPIR-V OpDecorate 71, NoPerspective 13, BuiltIn 11, Flat 14, member input and group/unresolved cases), `gfxlab/tools/gfx104_source_shader_spirv_bridge.py` (source authentic exact 524 pairs, private selective DXBC→SPIR-V→GLES310 translation), 9+5 synthetic source-free tests, and `.github/workflows/gfxlab-multi104-source-spirv-native-bridge.yml` with immutable ZIP2 SHA and original-source purge. Source-only local **independently reconstructed** parser: 6/6 synthetic cases and 6 GLSL lexer examples PASS; this is not proof of GitHub CI terminal success. No source bytecode or private owner log copied into public repo.

**GFX103 & GFX104 Actions terminal results/artifacts NOT CONFIRMED** from this chat's connector; do not report exact authentic ordinary/SIV counts or SPIR-V parity without safe CI aggregate. Workflows: `https://github.com/alwansan/raf/actions/workflows/gfxlab-multi103-source-interpolation-classes.yml` and `https://github.com/alwansan/raf/actions/workflows/gfxlab-multi104-source-spirv-native-bridge.yml`. **No further owner APK needed for these CPU source-private tasks.** Next is exact original source + SPIR-V decoration aggregate, then original-stage driver link with authenticated material/CB, rig, PC/Adreno pixels. `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`.

---

## 11 Nov 2026 — GFX102 genuine native NoPerspective on owner Adreno, GFX103 original source next gate

**Latest session:** memory/sessions/20261111-GFX-chat-owner-gfx102-native-noperspective-71.md (origin=chat). **GFX102 actual owner phone success** (NOT merely CI/source): ZIP SHA256 82fa4235ec6e4a88e8d02fd89cb4077fa228dd8c617cb697503c3137dfa44ff5 and 858d6bd354b17fdfdf6f8f2c6f3930099bce015d36c206b2f990f20a37a58a29, CRC pass each, 8 entries and five hashed/decoded 256×256 RGBA PNGs each, 25 events per export. Both exports contain identical summary/events and images, so **not proof of two independent GPU runs**. Safe aggregate gfxlab/evidence/20261111_gfx102_owner_adreno_native_noperspective_safe.json; private ZIP/PNG/logs are NOT in GitHub.

Owner GLES3.2/GLSL ES3.20 Adreno730 advertises NV_shader_noperspective_interpolation. 300 es native VS/FS GLSL **FAIL** reserved keyword. 310 es and 320 es native VS/FS compile+link+real GPU readback **PASS**. Smooth, Flat, AffineEmulated controls pass. Both native modes have exact full-pixel raw RGBA SHA256 ee7ceeaf02c698f4c805caea6d8ffad23913a86c25aec794429fd0cf174456a3 **same as affine emulation**, and CPU affine MAD .001141990429516256 vs smooth MAD .16301616768295013. **GFX102 proves native NoPerspective for one original-free test triangle on this phone, NOT original Raft Shader48 rendering or all DXBC semantics.** GLSL ES310 already used in original-source GFX094 stage pipeline, so do not globally change to ES320 without source-specific evidence. GFX097 proved 285 authentic original translated stages compile and 128 pairs link on Adreno, 29 pairs CPU BaseInstance unavailable, but no original material binding or pixels.

**GFX103 new engineering committed, source-private test CI pending**: gfxlab/tools/gfx103_source_interpolation_gate.py and gfxlab/tools/gfx103_source_interpolation_census.py parse original DXBC SHDR interpolation into ordinary DCL_INPUT_PS versus system-interpreted DCL_INPUT_PS_SIV and forbid silent loss of ordinary native qualifier, require optional NV extension under ES310/320, reject ES300. Tests gfxlab/tests/test_gfx103_source_interpolation_gate.py (11 synthetic) and gfxlab/tests/test_gfx103_source_interpolation_census.py (4 synthetic); source-pinned workflow https://github.com/alwansan/raf/actions/workflows/gfxlab-multi103-source-interpolation-classes.yml runs over all 524 authentic pairs and publishes safe aggregate only; private source purge even on failure. **Actual source counts and CI terminal outcome are NOT verified**. Critical: GFX039 prior 16 linear_noperspective and 16 SIV declarations must be cross-tabulated; no assumption they are the same/different or that SIV means ordinary native qualifier.

**Next**: verify GFX103 workflow and safe 524-pair ordinary/SIV cross-tab; add DXBC→SPIR-V→GLSL native qualifier source-variant preservation if ordinary declarations exist. Resolve SIV/builtin semantics separately and original Material/CB/normal/rig/PC pixel parity; full phase one still OPEN. Flags originalShaderRestored=false, originalAnimationRestored=false, phase_closed=false. Only branch experiment/android-graphics-rootcause modified; T1–T5 untouched.

---

## GFX101 Owner Adreno ZIP result + GFX102 GLSL ES 3.20 fix candidate — 11 Nov 2026

**Newest chat session:** `memory/sessions/20261111-GFX-chat-gfx101-owner-adreno-102-matrix-70.md`, origin=chat. **Actual uploaded ZIPs** have SHA256 `8b788636517fc672416ccd76d5a32baea9da627fa8c7b2a261c04ba81556af6c` and `350a42d8494918c16e07e3c73dde1ef9622f8bc2cec813c930b9290115d512c4`; both CRC valid and identical summaries/events, each 17 logged events and three SHA-verified actual GPU PNGs. On **owner Adreno 730 GLES3.2, GLSL ES3.20**, 104 GLES extensions listed, **`GL_NV_shader_noperspective_interpolation` TRUE**. GFX101 three real GPU controls Smooth, Flat, AffineEmulated all compile/link/readback success, reported zero GL compile errors; Smooth CPU MAD 0.001091419; AffineEmulated CPU MAD 0.001141990; Flat constant. Both native `#version 300 es` Vertex+Fragment compile calls fail **`'noperspective' : Reserved word`**, not unsupported extension. This **supersedes any inference that owner Adreno does not advertise NV extension**. No original Shader48 pipeline, original rig or PC matched pixels.

**External rationale:** [Khronos NV extension specification](https://registry.khronos.org/OpenGL/extensions/NV/NV_shader_noperspective_interpolation.txt); [Skia Qualcomm GLSL ES 320 workaround](https://skia.googlesource.com/skia.git/+/d782fd600e2c44d09e751588189a54f1d3612484/src/gpu/ganesh/gl/GrGLCaps.cpp). Hypothesis: use `#version 320 es` to reach required token. This is **not** proven on owner until GFX102 device run.

**GFX102 committed source-only** standalone original-free `com.alwansan.gfx102` under `gfxlab/android-gles-qualifier-probe-v102`: tests native `#version 300/310/320 es` with required NV extension individually, retains error logs, GPU/CPU colour comparisons, per-trial PNG SHA and safe `Download/Games/cl/test/g/` ZIP. Separate new Action: `https://github.com/alwansan/raf/actions/workflows/gfxlab-multi102-qualifier-version-matrix-apk.yml`. Checks: 8 source/analytic tests and 10 owner ZIP synthetic controls (full PNG chunk CRC/identity) via `gfxlab/tools/gfx102_owner_zip_audit.py`. Safe aggregate `gfxlab/evidence/20261111_gfx101_owner_adreno_safe_counts.json`. Owner guide `gfxlab/GFX102_OWNER_TEST_AR.md`.

**Build status:** GFX102 source/workflow committed, but terminal GitHub Actions run, signed APK and artifact **NOT VERIFIED YET**. Don't claim a download file exists or manufacture run ID/hash. Next check workflow, validate signed package/CRC/artifact, then owner GPU ZIP. Even a true GFX102 native interpolation pass is original-free and does NOT close GFX phase one. `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`. Team T branches and main untouched.

---

## 11 Nov 2026 — GFX101 standalone real GLES extension qualifier proof (source committed, APK CI NOT VERIFIED)

Following GFX100 owner `g.zip` actual Adreno evidence, GFX101 implements an original-free direct `GLSurfaceView` GLES3 Android app: `gfxlab/android-gles-qualifier-probe/` (`com.alwansan.gfx101`). It queries GLES30 `GL_NUM_EXTENSIONS/glGetStringi` **on the GL context**, requiring advertised `GL_NV_shader_noperspective_interpolation` before compiling an explicit vendor-`noperspective` GLSL ES3 variant. There are three mandatory controls—Smooth, Flat and perspective-correct affine emulation—plus optional native qualifier, all with real RGBA8 GPU `glReadPixels`, CPU pixel barycentric reference and PNG SHA-256. Native success requires extension + compile/link + Smooth/Flat/Affine controls + GPU affine match; absent extension yields `NATIVE_EXTENSION_NOT_ADVERTISED`, **not a GPU-driver failure**. GFX101 auto-exports private ZIP to `Download/Games/cl/test/g/` via Android MediaStore; separate privacy-safe auditor rejects forged success and wrong/missing hashes.

Tests `gfxlab/tests/test_gfx101_gles_capability.py` (9 synthetic/analytic checks) and `gfxlab/tests/test_gfx101_owner_zip_audit.py` (6 positive/negative archive checks); source code `gfxlab/tools/gfx101_owner_zip_audit.py`; workflow `https://github.com/alwansan/raf/actions/workflows/gfxlab-multi101-gles-native-interpolation-apk.yml`. Latest workflow update `73f8ca3be73ceeac404ad09ea8f54a688d3c56f4`. **GitHub Actions terminal success, signed APK and device execution remain UNVERIFIED**: no direct CI workflow-run status was obtainable with the available GitHub connector. Do not provide invented artifact ID or claim downloadable APK. No original Raft shader assets, T-team branches, ZIP2, OBB or full-game build touched. This is a **diagnostic original-free experiment only**; `originalShaderRestored=false`, `originalAnimationRestored=false`, `phase_closed=false`. Session `memory/sessions/20261111-GFX-chat-gles-native-qualifier-69.md`.

**Next:** Once CI artifact exists and its signature/ZIP/package SHA are independently checked, deliver the exact APK URL. Owner install on POCO F5 Pro, keep foreground and return auto-exported `GFX101-ALL-TEST-LOGS-*.zip`. If extension absent, proceed to a native Vulkan SPIR-V `NoPerspective` vs Smooth GPU experiment instead of relabeling GLES3 emulation as native. In parallel restore indexed original skinned data and PC↔Adreno shader/material pixel parity; do not close first phase.

---


**Khronos specification correction (GFX100 P0):** GLSL **ES 3.20 core supports only `smooth` and `flat`** interpolation; it has **no core `noperspective`**. Official ES 3.20 §4.5: https://registry.khronos.org/OpenGL/specs/es/3.2/GLSL_ES_Specification_3.20.html . The optional vendor extension `GL_NV_shader_noperspective_interpolation` can expose it (not evidenced on this Adreno), see https://registry.khronos.org/OpenGL/extensions/NV/NV_shader_noperspective_interpolation.txt . Vulkan SPIR-V `NoPerspective` is defined and supported in Vulkan shader semantics: https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html . **Do not attempt unconditional native `noperspective` in GLES3**. First enumerate actual GLES extensions; if unavailable, use a genuine Vulkan SPIR-V NoPerspective vs Smooth GPU experiment, and/or explicit analytically checked GLES3 affine-emulation without claiming a native qualifier. GFX041 exact Linear/NoPerspective PNG equality is consistent with unsupported core qualifier translation; it does not imply a hardware error or successful original-source preservation.

## تحديث فحص الهاتف GFX100 — 11 نوفمبر 2026

استلمنا `g.zip` لتطبيق GFX098، ونجحت مراجعة الأرشيف (SHA256 `60b6cb3e13ea1da7808128311696e9a906655340ea6a2537ad9c9db8d50faa69`): 3 جلسات، 227 حدثًا و147 snapshot، بلا أخطاء Unity مسجلة؛ 4 جولات مكتملة × 12 لقطة استوديو، بصمات PNG متحققة 48/48، وتكرار 12 حالة متطابق البايتات. التجربة الاصطناعية GFX041 جرت مرتين، ولكن صور Linear وNoPerspective متطابقة SHA256؛ لا تعتبر الاستيفاء no-perspective مثبتًا أو عطل Adreno. `gfxlab/evidence/20261111_gfx100_gfx098_owner_safe_counts.json` و`memory/sessions/20261111-GFX-chat-owner-gfx098-archive-68.md` هما مرجع الدليل الجديد.

**الأولوية الهندسية الآن:** اختبر مصدر GLSL ES3 أصليًا مؤكدًا بكلمة `noperspective` مع مرجع منظور مختلف W، وافحص الناتج فعليًا؛ لا تعِد استخدام ShaderLab diagnostic إذا حوّل المقاطع إلى `smooth`. بالتوازي استعد Mesh streams مع skinned weights/bindposes/hierarchy، وأكمل تصحيح sampling/normal/mips. ورغم GFX099 14/14 PC SHDR exact في إعداد Linear فإن المقارنة المرجعية PC ↔ Adreno وأصل Shader48 GPU ما زالت مفتوحة. لا نغلق المرحلة الأولى.

---

# المرحلة الأولى — القرار والخطوات التالية

**GFX-LAB | 11 نوفمبر 2026، بغداد**

فرع الكتابة الوحيد: `experiment/android-graphics-rootcause`.
مصدر ZIP2 المثبت: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
لا ننتقل إلى الماء أو النار، ولا ننشئ عاملًا عامًا الآن.

## تصحيحان أساسيان

1. **GFX093 / CI42922411580 SUCCESS:** بيانات الربط كانت موجودة في مصدر لم يفحصه المسار السابق: `m_ParameterBlobIndices` و`m_CommonParameters`. جدول 1656 سجلًا يتكون من 1275 برنامج GPU أصلي مرتبط و381 كتلة معاملات مستقلة. قراءة UnityPy 1.25.4 لجميع السجلات كبرامج أنشأت تصنيفات GL غير موثقة للسجلات الباقية؛ يجب سحب تلك الاستنتاجات. غياب RDEF من البرامج المرتبطة يبقى حقيقة مستقلة.
2. **GFX096 / CI42924121842 SUCCESS:** اسم المصدر هو builtin `Standard`، والمحرر `StandardShaderGUI`، والـfallback هو `VertexLit`. الحزمة الرسمية لنفس إصدار Unity 2021.3.45f2 تطابق أسماء الخصائص الـ27 وأنواعها وقيمها الافتراضية، وأسماء الـPasses السبعة بعد استثناء اثنين META للمحرر. هذا دليل على بنية المصدر؛ تطابق DXBC والبكسلات ما زال مطلوبًا. لا تعتبر كل استخدام لـStandard صحيحًا؛ المختبر القديم استعمل `_Glossiness=.45` واستيراد Metallic مختلفًا ولم يستعد الـrig.

## الأدلة المثبتة لهذه الدورة

| التجربة | الدليل | الحدود |
|---|---|---|
| GFX092، تشغيل 42921521714 | 883 اختبارًا؛ 12 مدخلًا فعليًا، كلها تستعمل المكوّن الأول في التعليمات المغطاة | 102 تعليمة غير مغطاة و36 معاملًا نسبيًا غير متتبع؛ لا إثبات للقيمة أو SSA |
| GFX093، تشغيل 42922411580 | 1435 رابط معاملات؛ 3642 رابطة صور و6562 رابطة CB تطابق تصريحات DXBC؛ 1852 تطابق اسم خاصية مع t/s و3344 مع b/member byte | أعداد مرات وقوع، وليست خصائص فريدة. 89 اختلاف حجم بين common وvariant محفوظة؛ تصريح DCL هو مرجع حجم التشغيل |
| GFX095، تشغيل 42923520045 | 905 اختبارات؛ 7 slots و6 مواد فريدة؛ 23408 كتابة أعضاء Float32 تطابق readback، منها 17283 float و6125 color | 167132 بايتًا معلومًا مقابل 10201380 بايتًا مجهولًا عبر مرات الوقوع. لم يرفع payload إلى GPU |
| GFX096، تشغيل 42924121842 | 910 اختبارات؛ تطابق أسماء وأنواع وقيم الخصائص الافتراضية الـ27، وأسماء الـPasses | لم يعاد compile المصدر الرسمي لمقارنة DXBC بعد |
| GFX094 | APK مستقل لاختبار compile/link الفعلي على الهاتف؛ 157 زوجًا ممثلًا، 285 stage متاحًا و128 زوجًا مرتبطًا offline | 29 مرحلة VS يرفضها SPIRV-Cross بسبب BaseInstance في GLES. لا عرض موديل أو إثبات بكسلات |

الحزمة الرسمية:
`https://download.unity3d.com/download_unity/88f88f591b2e/builtin_shaders-2021.3.45f2.zip`

SHA256:
`5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5`

## الخطوات التالية

1. استقبل ZIP اختبار GFX094 من المالك. افصل حالات CPU غير المتاحة الـ29 عن فشل driver الفعلي. اربط النتيجة بـAPK SHA256 وbuild_source_sha وGPU وGLES version. التطبيق يصدّر جميع السجلات تلقائيًا إلى `Download/Games/cl/test/g/`.
2. **مرجع Unity الرسمي:** أعد compile لزوج VS/FS ممثل لكل Pass باستخدام `ShaderUtil.GetShaderData(shader).GetSubshader(...).GetPass(...).CompileVariant(...)` في Editor 2021.3.45f2، على Windows64/D3D، وبنفس keywords وhardware tier. المصدر الأولي للواجهة: `Unity-Technologies/UnityCsReference:2021.3/Editor/Mono/ShaderUtil.cs`. نتيجة `VariantCompileInfo` تعطي `ShaderData` و`ConstantBuffers` و`TextureBindings`. قارن SHDR وISGN وOSGN الأصلية بالناتج داخل runner خاص. لا تخمّن platform defines إذا اختلف الناتج.
3. بعد التحقق من البرنامج، انقل كل Float وColor وTexEnv وUV وkeywords وrender queue وinstancing كما هي. حافظ على مشاركة هويات 6 مواد و18 صورة. أزل ثابت 0.45 من وضع المادة الأصلية، واحتفظ بالأوضاع التشخيصية الموسومة.
4. **Normal وMetallic:** تحقّق من دوال UnpackNormal وDXT5nm الرسمية لنفس الإصدار قبل استيراد PNG. لا تعامل AG المضغوط كصورة RGB normal. Metallic مؤلف sRGB؛ لا تغيّره إلى Linear بناء على قاعدة عامة.
5. استعد vertex/index/submesh/tangent وskin weights وbind poses وbones والـhierarchy الأصلية، خصوصًا M01 وM04. اختبر M03 بمادتين. عرض OBJ ثابت لا يغلق بوابة rig.
6. ابنِ APK للعارض بالمادة والشيدر المثبتين، وسجّل هوية البرنامج والـpass والـkeywords والـCB واستيراد الصور، مع لقطات مرتبطة باللوغ. قارنه بمرجع PC تحت نفس الكاميرا والضوء والمشهد، ثم احصل على قبول المالك.

## شرط إغلاق المرحلة

مرجع القبول: `gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md`.
يجب اجتياز بوابات المصدر والهندسة والمواد والصور والاستيراد والشيدر والربط وحالات الرسم والـrig ومقارنة PC/الهاتف وقبول المالك، ثم إثبات الوصفة على نموذج بسيط وحالة مادتين وحالة skinned وموديل جديد.

حتى ذلك الحين: `originalShaderRestored=false` و`phase_closed=false`.
اختبار GFX094 وحده لا يغلق هذه البوابات.


## ملاحظات متابعة GFX098

- أصبحت نتيجة هاتف GFX094 مثبتة: 285 compile و128 link ناجحة، دون أخطاء GL؛ الـ29 غير المتاحة تخص تحويل BaseInstance على CPU.
- المختبر الموحد GFX098 يجمع عارض الموديلات الستة واختبارات GFX041 في مشهدين، ويضيف وضع قيم المواد المصدرية مع مشاركة هويات الأصول والتقاط 12 حالة تلقائيًا.
- بيانات `m_PlayerSubPrograms` الأصلية لا تعطي hardware tier صريحًا لكل طلب مختار. لذلك يسجّل طلب PC القيمة -1 بوصفها UNKNOWN، ويجرب المترجم tiers الثلاثة كمرشحين؛ لا يستنتج source tier بلا تطابق مستقل.
- يجب ضبط `PlayerSettings.colorSpace=Linear` قبل مقارنة compile لبرامج PC وتسجيله في تقرير الشاهد، لا الاكتفاء بإعداد Android اللاحق. عدم تطابق ناتج compile مع مرجع ذي إعدادات مختلفة لا يثبت أن المصدر الرسمي مختلف.
- مرشح Normal الحالي يفك R*A وG وفق Unity الرسمي ويعيد تمثيل XYZ على CPU قبل TextureImporter. هذا لا يثبت تماثل الترشيح: bilinear ثم إعادة بناء Z في shader يختلف عمومًا عن ترشيح Z المعاد بناؤه مسبقًا. اختبر لاحقًا Raw RG/AG sampling مع فك Z على GPU، وحافظ على mip chain الأصلية أو علّم الفرق صراحة، قبل إغلاق بوابة Normal/pixels.

- فحص بيانات Skin الأصلية متاح في `gfxlab/evidence/20261111_original_skin_availability_safe.json`: خمسة موديلات skinned تحتوي أوزانًا وفهارس لكل 14033 رأسًا و213 bind poses، دون أوزان غير منتهية أو مجاميع خارجة عن سماحية1e-3 أو فهارس موجبة الوزن خارج bind poses. لم تتحقق hierarchy أو مصفوفات الوضع بعد.
- عند استعادة الـrig استخدم مسار VertexData كاملًا بدل افتراض كفاية OBJ: دمج رؤوس ذات position/UV/normal متطابقة قد يطمس اختلاف bone weights/indices أو tangents. انقل السمات والفهارس وsubmeshes والـbind matrices الأصلية مع تحقق إعادة skinning في وضع مرجعي.
