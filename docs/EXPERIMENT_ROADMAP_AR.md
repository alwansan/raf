# خارطة تجارب GFX-LAB — فصل الأسباب قبل تعديل لعبة Raft

**حدّ الفرع:** تجارب مستقلة مصدرية/وصفية من main. لا توجد هنا أصول اللعبة، ولا يُشغّل XAPK جديد. أعمال الفريق T1–T5 قائمة، نستخدم نتائجها ونسلّم إصلاحات مثبتة للمالك المناسب بدلاً من مزاحمته.

## ترتيب التنفيذ (تجربة صغيرة واحدة في كل دورة)
| تجربة | السؤال | عينة A/B والقياس | نتيجة تمر | فشل/تعليق |
|---|---|---|---|---|
| GFX-01 **shader identity frontier** | هل الشيدر الذي يخدم Renderer أبيض حقيقي ما زال `Dummy` **بعد كل مراحل restore**؟ | سجل الأصل → same-export GUID → current native post-restorer ShaderLab → Unity compiled pass/variant. ابدأ بالهدف الأصلي 921-slot وقطعة يد/طوف فقط إن ثبت الربط | نفس Shader48/Material/renderer وprogram غير Dummy مع مصدر/variant صحيح | Unknown إذا لا يوجد exact source identity؛ لا تستبدل based on names |
| GFX-02 **smoke/fire split** | هل مربع الدخان ناتج عن Dummy وBlend/ColorMask/alpha؟ | ربط smoke34 (17 renderer/34 slots) منفصلاً عن fire108 وfire34؛ compare original one-pass alpha state with postrestore + optional synthetic Unity transparent quad | source/export match + Unity RGBA alpha test ثم هاتف Raft بنفس المؤثر | لو أصل emitter مختلف → ابحث actual runtime identity أولاً |
| GFX-03 **lighting material** | هل الأبيض من برنامج PBR أو color-space/normal/lightmap؟ | Mesh static known material: unlit diagnostic vs actual shader؛ toggles ثابتة للضوء/normal/sRGB/emission مع capturing API+shader.isSupported+passCount | يتم عزل أول عنصر مفقود (program / binding / texture / lighting) | لا تغيّر ProjectSettings أو كل المواد دفعة واحدة |
| GFX-04 **water/compute** | هل kernel index 6 وPass IDs ما زالا مفقودين في native الحالي؟ | قراءة gate after restorer + actual Unity shader kernel/import list + pass selector; مقارنة T1 original Vulkan traces | نقل أصلي faithful kernel/pass مع تكافؤ GPU في fixture | نجاح source/Unity synthetic لا يثبت الماء داخل اللعبة |
| GFX-05 **device release difference** | هل بناء أحدث تغيّر البكسلات مقارنة APK89؟ | manifest/signature/OBB hash + نفس scene/time/quality/GPU API + screenshots+short bounded Unity log على POCO F5 Pro | before/after PNG حقيقي بهوية renderer shader والبيانات الفعلية | بلا manifest = INCONCLUSIVE، لا نخلط mini lab أو LogRaft |

## GFX-01: أول خطوة عملية مقترحة
1. **بدون Unity جديد**: اقرأ [تقرير Native T3](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_NATIVE_POSTRESTORER_DUMMY_EVIDENCE_2026-11-05.md) ثم راجع أي CI أحدث موثّق على الفرع العامل؛ لا تعيد نفس الـcensus.
2. كوّن سجل `shader_identity_result` خاصاً داخل runner بربط `original owner+PathID` إلى `same-export GUID` إلى `actual ShaderLab` بعد restorers. احفظ المعرفات الخاصة داخل scratch، وانشر فقط: `source_join=true/false, pass_matches, dummy_marker, stage_pairs_verified, shader_is_supported`. لا تُجبر `source_join=true` بسبب الاسم.
3. إن خرج هدف الـ921 Dummy → قصّر البحث إلى برنامج هذا Shader48، 4 original passes و33 linked VS/FS pairs، بما فيه keywords/CB/sampler/render states. إن خرج غير Dummy → اختبر Unity import/GPU تحت المقاييس نفسها ولا تعِد النص أصيلاً بلا compare.
4. لا تبدأ بناء لعبة، ولا تكلف المالك بصور إضافية قبل اكتمال خطوات المعمل التي يمكن تشغيلها بدون الهاتف. عند الحاجة الفعلية لهاتف استخدم T5 unified mini lab أو لقطة للعبة الأصلية بعد توافق الفريق.

## فصل الاحتمالات المرئية
- لون مسطح أبيض مع textures/Materials موجودة: ابحث `Shader.isSupported` وDummy/Pass وdynamic variant قبل Gamma.
- مربعات نار/دخان: اختبر `Blend`, `ColorMask`, `ZWrite`, `Cull`, alpha texture، Particle vertex streams والربط الحقيقي لا fake particle sprites.
- إضاءة مشوهة: افصل BaseColor/Normal/Emission ثم Light/Shadow/Depth/PostFX؛ ليس كل `Graphics.Blit Invalid pass` مرتبطاً بجسم أبيض.
- ماء مفقود: Compute+FFT kernel identity ومخرجاته وSpectrum/Foam/Blur multipass؛ لا تكفِ نتيجة OpenGLCore synthetic للتكافؤ.
- عمر الأدلة: phone 2026-11-05 مقابل source-only 2026-11-09 يجب أن يُذكر في أي قرار.

## شروط الانتهاء/التسليم إلى T3 أو T1/T2
تسليم أصلي بأدلة متسلسلة **source identity → same export → Unity variant → measured GPU → Android game pixels**. يُسمح بتعديل موضعي في ShaderLab فقط إذا ثبت فقد مطابق دلالياً، مع اختبار regression وعدم لمس GUID/meta/scene/saves. قبل ذلك لا إصلاح shaders على فرع الفريق ولا APK/OBB/XAPK. إن وجدنا خلاصة تقنية جديدة، نحفظها في جلسة جديدة ونرسل الرابط إلى T3 (شيدرات/لون/نار)، أو T1/T2 (ماء) أو T5 (بناء/مختبر).


## 2026-11-10 — GFX-MULTI-022 completed; next GFX-MULTI-023
- GFX022 [CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021): 1,435/1,435 linked variant rows valid; 524 matched keyword/tier pairs; 1,275 unique referenced DXBC stage programs; all 1,275 RDEF-absent and all 1,435 parameter/sampler/CB metadata absent. Material property→source t/s mapping remains blocked. No Android/GPU claim.
- GFX023: source Material/Texture2D semantics and pixel-channel census for seven Materials / 21 bound textures, including UV/tint and original format/color-space/mip/stream metadata; use authenticated sparse source chunks; publish safe aggregates only.


## GFX-MULTI-023 — original Material/Texture2D semantics and channel census (2026-11-10)
[CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) **SUCCESS**, 128 tests. Six models, seven original Materials, 63 TexEnv slots (21 bound / 42 null), seven BaseColor + seven Normal + seven Metallic textures. All 21/21 original Texture2D images decoded with exact dimensions; 53,477,376 pixels examined privately. Only 15 authenticated stream chunks / 707,788,800 selected bytes were hydrated; safe aggregate artifact uploaded and all private source/texture/stream data purged.

Material facts: 14 color slots, 112 float slots, 0 int slots; all seven authored tint slots are identity white; all 21 role-specific UV scale/offset transforms are identity. Texture format code BaseColor 10×5 + 12×2, Normal 12×7, Metallic 12×7; color-space code BaseColor 1×7, Normal 0×7, Metallic 1×7; mip-count code BaseColor 11×3/12×4, Normal 11×3/12×4, Metallic 11×5/12×2; filter-mode code 1×21. Raw codes remain uninterpreted pending Unity 2021.3 enum verification. Texture settings, anisotropy and mip-bias fields were present on all 21; generic `m_WrapMode` unavailable, axis-specific wrap fields still open.

Channels: BaseColor RGB variable 7/7; A variable 2/7 and opaque 5/7. Normal R constant 7/7 while G/B/A variable 7/7; the tested conventional A+G / constant R+B signature candidate is 0/7. Metallic Alpha variable 7/7 (possible extra data only, not proof of smoothness). No original Shader48 execution or GPU pixels.

First attempt [CI42743969290](https://github.com/alwansan/raf/actions/runs/42743969290) planned the 15 chunks but re-read the manifest after sparse checkout excluded it. The correction reused SHA-verified staged owners; [CI42744204412](https://github.com/alwansan/raf/actions/runs/42744204412) passed and purged private data. Artifact [13730562085](https://github.com/alwansan/raf/actions/runs/42744204412/artifacts/13730562085), expires 2026-11-17T02:40:48Z UTC.

Limits: no source names, PPtrs, raw pixels, images, shader bytes or register indices exported; no PC/GPU/Adreno parity, APK or owner acceptance. `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`.


## Next GFX-MULTI-024
Audit Material float/color property categories and axis-specific texture wrap settings; ground raw TextureFormat/color-space enum meanings in Unity 2021.3 references. Then decide whether a minimal Android GLES texture-channel viewer is needed for actual device proof.
