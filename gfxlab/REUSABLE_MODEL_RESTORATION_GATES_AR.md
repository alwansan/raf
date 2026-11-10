# GFX-LAB — خطة إغلاق استعادة الموديلات والأيتمات قبل تكليف عامل مستقل
**10 نوفمبر 2026 | المصدر ZIP2 المثبت 15964ea8f246b6e076ce26b60931ee2e1a9a2385 | فرع GFX-LAB فقط**

## الفصل بين المراحل
- مرحلة هذا المختبر: **Mesh / Geometry / Material / Texture2D / original common Shader48 / optional Skinned Mesh assembly** للموديلات الستة، ثم نموذج قابل للتعميم.
- مستقلة بالكامل: ماء وFFT/compute، رغوة وانكسار الماء، نار/دخان/particle alpha، إضاءة خاصة/post processing، سلوك اللعبة/الشبكة والصوت والحفظ. لا نعتبر نجاح عنصر واحد إصلاحًا لهذه المراحل.

## ما ثبت فعليًا
1. مصدر ZIP2 original Renderer→Mesh→Material→Texture2D وShader48 مربوط ومثبت SHA. مصدر ستة Mesh و7 material slots و21 صورة؛ الوحدة الأساسية تعمل على الهاتف باستخدام **Unity Standard fallback**، مع 14 لقطة و12 LOG في الحزمة التي أرسلها المالك؛ errors=0 لكن originalShaderRestored=false وoriginalAnimationRestored=false.
2. مصدر OBJ مع جميع الرؤوس المستخدمة، وتطابق عدد Vertex الفريد بعد دمج صفات float32 (pos+UV+normal) مع رؤوس Unity في الستة. اختلاف عدد الرؤوس (374 في M01/M04) ليس وحده فقدان Mesh.
3. Class48 واحد مشترك للمواد السبع، SubShaders اثنان و7 Passes، 1435 رابطة stage حقيقية صحيحة إلى DXBC D3D11.
4. [GFX-MULTI-013](https://github.com/alwansan/raf/actions/runs/42732808109) نجح 7/7 Passes: زوج source VS+FS مطابق keyword/tier لكل Pass، DXBC→SPIR-V Vulkan1.1→GLSL ES310، 14 stages صالحة لترجمة CPU، Stage IO (locations/types) متوافقة. لا يوجد Android shader runtime مثبت.

## بوابات إلزامية لإغلاق هذه المرحلة
| البوابة | الحالة | الدليل الناقص |
|---|---|---|
| SOURCE IDENTITY | PASS للعينة | جرد كامل لبقية Renderer slots مع SHA/mesh/submesh identity عند التوسع |
| MESH/UV/IMAGE ON DEVICE | PASS للعرض الأساسي | indexed triangle remap، tangent-space parity والـnormal map الناتج |
| MATERIAL SEMANTICS | OPEN | صور BaseColor sRGB، normal DXT5nm swizzle، metallic alpha/smoothness، UV transforms، tint، mip/filter/wrap/sampler |
| ORIGINAL SHADER SOURCE/CPU | PARTIAL PASS | جميع الـ524 variants، original keyword/pass state/CB/sampler/semantics/register-offset bindings |
| UNITY ANDROID ORIGINAL SHADER | OPEN | ShaderLab GLES3 مكافئ حقيقي مع shader.isSupported وpass/keyword runtime identity وcapture |
| RIG/COMPOSITE MODEL | OPEN | skinned weights/bindposes/bones/parent hierarchy/animations وصحة تجميع M04 وأمثاله |
| PC PIXEL FIDELITY | OPEN | مشهد ثابت وكاميرا وإضاءة وتوازن ألوان ثابتة، تقارير مقارنة GPU/PNG على PC والهاتف |
| OWNER ACCEPTANCE | OPEN للشيدر الأصلي | صور+لوغ وقرار قبول المالك للجهاز على الشيدر الأصلي لا Standard |

## قرار إنشاء عامل الاستعادة العام لاحقًا
لا يُنشأ العميل الآن؛ المالك سيحدد بنفسه تفاصيل إنشائه لاحقًا. قبل ذلك نثبت **موديلًا ممثلًا واحدًا كامل السلسلة Shader48 + Mesh + Texture + Resource binding + Android GPU**، ثم نختبر حالة مادتين M03 وحالة Skinned/Composite M01/M04 وموديل جديد غير مألوف (negative control). بعدها نجمّد وصفة قابلة لإعادة التشغيل توقف التنفيذ عند mismatch، ولا تولّد Shader Dummy أو تُخمن الهوية بالأسماء.

## التجربة التالية المحددة
**GFX-MULTI-014**: فحص binding ضمن Pass واحد من Shader48 الأصلي: DXBC registers ↔ SPIR-V descriptor set/binding ↔ original Unity Material textures + CB offsets + normal/tangent/swizzle، مع تقرير عددي خاص لا يُخرج shader code. فقط بعد اكتمال هذا يُسمح بمختبر Android منفصل، ولا يُدمج شيء في T3/فرع المنتج قبل دليل الهاتف.


## 2026-11-10 — Binding reconstruction stage
GFX-MULTI-019 [CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) links original t/s registers (29 t,27 s) to compiler-generated SPIR-V names and actual descriptor bindings privately with complete 56/56 coverage; **all descriptor numbers differ from original source t/s numbers**. CB 66 names remain unrecognized; no material texture-role → t# register association. GFX-MULTI-020 must check original `SerializedSubProgram` m_TextureParams / name indices / sampler declarations ↔ original `Material.m_SavedProperties.m_TexEnvs`, and CB byte offsets before closing any item shader stage. This diagnostic is not original shader running on Android.


## GFX-MULTI-020 decisive property-to-register blocker
[CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) proved original six-model/seven-material sample has 63 material TextureEnv entries and 21 authentically bound textures; source Shader48 27 serialized properties and per-Pass NameIndices, but **0/14 selected compiled source program rows have `m_Parameters`**. No m_TextureParams Index/SamplerIndex ↔ property-name table available to establish true Shader48 Material→DX11 t/s binding. This is source metadata missing, not lost model colors. Before agent handoff either find same-ShA original shader source/auxiliary compile metadata or define separate PC reference/pixel proof; no guessing based on order, no Android shader parity claim.


## GFX-MULTI-021: source Material properties are genuinely present
[CI42741817991](https://github.com/alwansan/raf/actions/runs/42741817991) 107 tests: all 63 original material TexEnv property labels match original Shader48 27 serialized properties (9 texture-type), 21 bound (7 basecolor+7 normal+7 metallic), 42 source null. Shader48 typed object has no embedded m_Script text, no native HLSL source. Original compiled-stage rows for 14 representatives have no m_Parameters (GFX020), and DXBC variants RDEF absent in 14 representatives (GFX015), so independent property→original t/s bridge not proven. Treat visual parity and original shader recovery OPEN; check alternate source variants before concluding unavailable.


## GFX-MULTI-022 — تغطية كل variants المرتبطة
[CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021) SUCCESS 119 tests: 1,435 linked variant metadata rows valid, 524 exact keyword/tier pairs, 1,275 unique referenced DXBC programs bounded; RDEF 0/1,275، parameters 0/1,435، TextureParams 0، CB binding metadata 0، top-level sampler/CB 0. Source property→DX11 t/s bridge blocked across the referenced set. Unreferenced compiled-table entries were not included. This is ORIGINAL_SOURCE only, not ShaderLab/GPU/Android proof.

## GFX-MULTI-023 planned material fidelity gate
Audit the seven original Materials / 21 bound Texture2D assets: texture format, source color-space metadata, mip/stream/filter/wrap flags, UV scale/offset, tint/color/floats, and per-role channel summaries. Rehydrate only authenticated sparse stream chunks; no public raw assets. Normal channel packing statistics are not DXT5nm semantic proof without shader/PC evidence.


## GFX-MULTI-023 — original Material/Texture2D semantics and channel census (2026-11-10)
[CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) **SUCCESS**, 128 tests. Six models, seven original Materials, 63 TexEnv slots (21 bound / 42 null), seven BaseColor + seven Normal + seven Metallic textures. All 21/21 original Texture2D images decoded with exact dimensions; 53,477,376 pixels examined privately. Only 15 authenticated stream chunks / 707,788,800 selected bytes were hydrated; safe aggregate artifact uploaded and all private source/texture/stream data purged.

Material facts: 14 color slots, 112 float slots, 0 int slots; all seven authored tint slots are identity white; all 21 role-specific UV scale/offset transforms are identity. Texture format code BaseColor 10×5 + 12×2, Normal 12×7, Metallic 12×7; color-space code BaseColor 1×7, Normal 0×7, Metallic 1×7; mip-count code BaseColor 11×3/12×4, Normal 11×3/12×4, Metallic 11×5/12×2; filter-mode code 1×21. Raw codes remain uninterpreted pending Unity 2021.3 enum verification. Texture settings, anisotropy and mip-bias fields were present on all 21; generic `m_WrapMode` unavailable, axis-specific wrap fields still open.

Channels: BaseColor RGB variable 7/7; A variable 2/7 and opaque 5/7. Normal R constant 7/7 while G/B/A variable 7/7; the tested conventional A+G / constant R+B signature candidate is 0/7. Metallic Alpha variable 7/7 (possible extra data only, not proof of smoothness). No original Shader48 execution or GPU pixels.

First attempt [CI42743969290](https://github.com/alwansan/raf/actions/runs/42743969290) planned the 15 chunks but re-read the manifest after sparse checkout excluded it. The correction reused SHA-verified staged owners; [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) passed and purged private data. Artifact [13730562085](https://github.com/alwansan/raf/actions/runs/42744204412/artifacts/13730562085), expires 2026-11-17T02:40:48Z UTC.

Limits: no source names, PPtrs, raw pixels, images, shader bytes or register indices exported; no PC/GPU/Adreno parity, APK or owner acceptance. `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`.


## GFX-MULTI-024 planned gate
Inspect Material float/color semantics and TextureSettings WrapU/WrapV/WrapW; verify Unity 2021.3 enum meanings before interpreting raw texture format/color-space codes. Channel variability remains diagnostic only; do not declare DXT5nm or metallic-alpha smoothness without shader/PC/device evidence.


## 2026-11-10 — GFX-MULTI-024 confirmed
[CI42745536309](https://github.com/alwansan/raf/actions/runs/42745536309) SUCCESS 139 tests. Source six models have **seven Renderer Material slots but six unique Material21 objects**, and **21 Texture2D references but only 18 unique Texture2D objects**. This repairs a source accounting assumption exposed by failed [CI42745345599](https://github.com/alwansan/raf/actions/runs/42745345599). All 112 Float and 14 Color saved-property labels match the original Shader48 27-property declaration; 33 float zeros, 58 ones, 21 between 0 and 1. Colors: seven identity-white (including seven white tints) and seven nonidentity secondary colors (role unknown). Unity 2021.3 official enums show original BaseColor DXT1×5 + DXT5×2, Normal/Metallic DXT5×7 each; BaseColor/Metallic sRGB×7 each and Normal Linear×7. All 21 source texture links have Bilinear, Repeat U/V/W, Aniso=1 and MipBias=0. [Official Unity 2021.3 enums](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs). No source-to-DX11 constant buffer offset mapping or Shader48 Android runtime. No APK. Private source purged.

## GFX-MULTI-025 next
- **P0**: inspect the seven nonidentity secondary Color slots: source property-label matches and safe semantic classification (e.g. emission candidate). No raw property strings or numerical colors in public files. Do not infer emissive GPU effects.
- **P0**: privately map which M00–M05 Renderer Material slots share the same Material21 and which of the 21 Texture role links reference the same Texture2D; publish only anonymized pair/set-size counts, not source PPtrs/GUIDs, and preserve real identities in Unity asset transfer.
- **P1**: establish deterministic import policy that preserves original TextureFormat/ColorSpace, sampler wrap/filter/aniso/mip, and UV/tint/secondary color values without falsely claiming Shader48 parity. Metallic sRGB is *source authored*; don't silently convert data to Linear based on common PBR assumptions.
- **P1**: resolve original shader property→CB offsets/material→DX11 registers via independent authentic PC/reference evidence, not fabricated order. Then decide minimal GPU channel experiment; separate ORIGINAL_SOURCE/UNITY/GPU/OWNER gates.
- **P2**: original rig/skinning, M03 dual materials, water/FFT, smoke/fire remain independent open scopes. T1–T5 and main/zip2 read-only.


## GFX-MULTI-025 — 2026-11-10 original color and asset sharing verified
[CI42746455458](https://github.com/alwansan/raf/actions/runs/42746455458) SUCCESS / 146 tests, private original ZIP2 SHA-pinned source. Material slot identities: 7 Renderer slots → 6 unique Material21 objects (five single-use, one shared across models). Texture links: 21 → 18 unique Texture2D objects (fifteen single-use and three shared twice across models); zero links shared across roles. All fourteen Color saved-property labels are declared in the authentic original Shader48: seven **white base tints** and seven exact `_EmissionColor` property candidates with **black RGB and Alpha=1**. Thus GFX024's secondary nonwhite Color entries were black emission colors, not failed Albedo tint. Names, raw numeric values, object pointers and image/shader data remained private; runner purge complete. No original Shader48 GPU shader or pixel equality. [Safe artifact 13730829715](https://github.com/alwansan/raf/actions/runs/42746455458/artifacts/13730829715).

## GFX-MULTI-026 — current next priority
- Audit exact original Shader48 seven serialized Pass render-state metadata: Cull, Blend, ZWrite, ZTest, ColorMask, effective queue/pass tags, and presence/missing fields using original SHA-pinned source, without inventing unsupported values. Source-only metadata cannot establish runtime GPU state.
- Audit original seven Material slot references' source `m_CustomRenderQueue`, shader keyword fields, instancing flags, and whether shared objects preserve state across slots.
- Return only safe state availability/category counts, never raw proprietary original shader names, material IDs, vectors or code; compare against Unity 2021.3 official enum reference. Maintain `originalShaderRestored=false`, `android_gpu_pixels_verified=false`.
- Later: controlled original-source→Unity→Adreno/PC comparison with genuine original Shader48 inputs and property→register/CB semantics, avoiding guesswork; do not modify T1–T5, main, zip2.
