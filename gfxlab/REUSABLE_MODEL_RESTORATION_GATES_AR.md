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
