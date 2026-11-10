# GFX-MULTI-040 — دليل اختبار الاستيفاء على أندرويد (نسخة تشخيصية مستقلة)

**الدور:** GFX-LAB — `experiment/android-graphics-rootcause`  
**المشروع:** `alwansan/raf`  
**الحالة:** نسخة اختبار اصطناعية فقط. لم تُستعد شذرات Shader48 ولا خريطة ربط Material/CB الأصلية.  
**الاختبار:** دعم محرك GPU على الهاتف لثلاثة أنماط من نقل قيم القنوات من Vertex إلى Fragment.

## ماذا نختبر؟

تتبع Shader48 الأصلي في GFX-MULTI-039 المصدر 1275 برنامجاً مرتبطاً، واكتشف في تعليمات Fragment الأصلية 3405 إعلانات `linear`، و76 `constant` و16 `linear_noperspective`. هذه **عدادات تعليمات** وليست صوراً من اللعبة أو اختباراً على Adreno. لذلك يتضمن APK ثلاثة **شيدرات اصطناعية جديدة**:

| المعاينة | التوقع التشخيصي | معنى الإخفاق |
|---|---|---|
| Linear | التدرج يتأثر بقيمة W المختلفة في كل رأس | اختلاف النتيجة المتوقعة عن GPU، أو فشل شيدر |
| Flat | لون ثابت داخل وجه المثلث | قد لا يكون `nointerpolation` مدعوماً في الترجمة أو يختلف سلوك التجسيد |
| NoPerspective | تدرج يختلف عن `Linear` على المثلث ذي W المتفاوت | قد لا يكون `noperspective` مترجماً أو مدعوماً |

**البرنامج لا يحتوي موديلات أو ملفات Raft الأصلية، ولا يحاول استنتاج تقييد `t#/s#/b#` أو ConstantBuffer.**

## اختبار على الهاتف

1. حمّل ملف `GfxLab-Interpolation-GPUProbe.apk` من Artifact الخاص بتشغيل GFX-MULTI-040 الناجح. التطبيق مستقل، ومعرّف حزمته `com.alwansan.raft.graphicslab.interpolation`، ولن يحل محل تطبيق النماذج الستة `com.alwansan.raft.graphicslab.autologs`.
2. ثبّته وافتحه بالوضع الأفقي. ينتقل تلقائياً إلى فحص GPU ويعرض معاينات ثلاث: Linear وFlat وNoPerspective.
3. انتبه لحقل `Status`. الحالة `DIAGNOSTIC_INTERPOLATION_PASS` **تعني أن المعايير التشخيصية الاصطناعية مرّت فقط**؛ لا تعني استعادة Shader48. الحالات `INCONCLUSIVE` تعني عدم اكتمال قياس GPU أو عدم دعم الاختبار؛ `MISMATCH` تعني أن القياسات لم تطابق عتباته المحددة.
4. يمكنك الضغط على `RERUN GPU TEST` لتكرار التجربة، ثم `EXPORT ALL LOGS ZIP` لحفظ **كل** السجلات والجلسات والصور. لا حاجة لنسخ Logcat يدوياً.
5. اعثر على ملف ZIP داخل المسار:

`/storage/emulated/0/Download/Games/cl/test/g/`

ارفع ملف ZIP في الدردشة عند رغبتك بمراجعته. ملف ZIP يحتوي على أحداث Unity مع Stack Traces، والـsnapshots المتعاقبة، وملفات summary، وثلاث صور PNG للـRenderTexture بحجم 256×256 ضمن `sessions/<id>/gpu-interpolation-*.png`.

## آلية الحسم والأدلة

- يُحسب PASS فقط عندما تكون الواجهة GLES3 ويكتمل ReadPixels لجميع الحالات وتوجد عينات ملونة، ويظل `Flat` ثابتاً عبر مواقع القياس (حد اختلاف اللون 0.06)، وتظهر بين `Linear` و`NoPerspective` فروق على الأقل 0.018 في متوسط فرق RGB.
- هذه الحدود **اختبار تحسس** مختار لتشخيص دعم qualifiers، وليس اختباراً فيزيائياً مكتمل الدقة، ولا إثبات سلوك rasterizer الأصلي لـShader48. المعيار الأقوى يعتمد على مرجع PC وبيانات موارد أصلية.
- تشفير الصور وكتابة السجلات تحدث داخل التطبيق، ثم تصدير MediaStore ضمن `Download/Games/cl/test/g/`. إذا رفض نظام الهاتف الوجهة أو اكتشف اختلاف الحجم فلا ندعي نجاح التصدير، ونحتفظ بنسخة ZIP خاصة بالتطبيق.
- يمكن فحص ZIP محلياً (في Termux مثلاً) عبر الأداة:
  `python3 -m gfxlab.tools.interpolation_owner_zip_audit --zip /path/to/owner.zip --out /path/to/safe.json`
  وهي تنتج **أعداداً وحالات عامة فقط**؛ لا تطبع أسماء الجهاز أو الصور أو تفاصيل Stack Trace.

## ما الذي يبقى لإغلاق المرحلة الأولى؟

`GFX-MULTI-037` أثبت أن 1275/1275 DXBC الأصلية تحتوي `ISGN/OSGN/SHDR` فقط، بدون `RDEF` أو Debug Reflection. لا نملك حتى الآن رابطاً موثوقاً `Shader48 Material property → DX11 t/s/b register → SPIR-V sampler/CB byte offset`. كذلك لم نثبت سلوك حالات الرسم الديناميكية الأصلية، أو استعادة Rig/Animation، أو مطابقة صور Windows PC مع Adreno.

يُطلب أصل ShaderLab/HLSL المملوك أو Capture مشروع وموثوق من نسخة PC مستقبلاً فقط إذا توافر بالفعل؛ **لا نحتاج من المستخدم إلى كمبيوتر لتشغيل فحص GFX-MULTI-040 على هاتفه**.

## روابط المصدر

- `gfxlab/unity/Assets/Shaders/GfxLabInterpolation*.shader`
- `gfxlab/unity/Assets/Scripts/GfxInterpolationProbe.cs`
- `gfxlab/unity/Assets/Editor/GfxInterpolationAndroidBuilder.cs`
- `.github/workflows/gfxlab-multi040-interpolation-gpu-apk.yml`
- `gfxlab/tools/interpolation_owner_zip_audit.py`
- `memory/sessions/20261110-GFX-chat-android-interpolation-probe-14.md`

**إخلاء مهم:** أي APK أو تقرير من هذا الاختبار يظل `originalShaderRestored=false` و`originalPcPixelParityVerified=false`، حتى لو اجتاز كل الشيدرات الاصطناعية.
