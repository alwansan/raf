# T3: إثبات DummyShaderTextExporter في تصدير الشيدر الأصلي للدخان (9 نوفمبر 2026)

**RENDER-002 OPEN · NOT_READY 0/3 — هذا إثبات فقدان التصدير، وليس إصلاحًا للهاتف.**

## أصل الدليل
- [CI42679312674](https://github.com/alwansan/raf/actions/runs/42679312674) SUCCESS: المصدر الأصلي SHA المثبت بستة مشاهد وأربعة ملفات Material/Shader؛ 17 كائن ParticleSystemRenderer ذات تلميحات smoke-like تربط 34 خانة Material بشيدر واحد أصلي Shader48، مختلف الهوية عن شيدر fire آخر ذي رتبة 34. الأصل له SubShader واحد/Pass واحد: Color Blend وAlpha Blend يعتمدان على Alpha، وColorMask RGB، وZWrite OFF.
- [CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) SUCCESS على SHA 78826ae4333b0b401c7170350a7aeaa67b13583d، [أثر آمن 13702312921](https://github.com/alwansan/raf/actions/runs/42681908313/artifacts/13702312921). استُخدم ZIP2 الأصلي المثبت عند commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385، وAssetRipperCLI عند 036098ab525a3f9f693dc101edeb21faad4d32d8، وتم التصدير الخاص مرة واحدة بتتبّع W1 Shader48 وB02 Texture2D28 من نفس export_instance.

## نتيجة الربط الفعلي
| المقياس | النتيجة |
|---|---|
| اختيار الهوية | Shader48 أصلي واحد مرتبط بـ17 Renderer و34 Material slots |
| سلامة المصدر | ستة مشاهد وأربعة مالكي Shader/Material ثبتت SHA |
| هوية التصدير | نفس W1/B02 export_instance، والتحويل من أصل Class48 إلى GUID وملف shader.meta محدد |
| مصدر Original Pass | Pass واحد، Color/Alpha Blend يعتمدان على Alpha، ColorMask RGB، ZWrite OFF |
| الشيدر الناتج | Custom ShaderLab موجود، لكنه ACTUAL_DUMMY_SHADER_TEXT_EXPORTER |
| علامة DummyShaderTextExporter | TRUE |
| ShaderLab Pass | Pass واحد وأقواس متوازنة، برنامج شكلي واحد؛ هذا لا يثبت أصالة البرنامج |
| ColorMask RGB بالنص المصدّر | غير موجود في الفحص المعجمي (lexical، ليس إثبات Pass فعّال) |
| تطابق bytecode/variants أو إصلاح الصورة على الهاتف | غير مثبت |

**الخلاصة المحددة:** التصدير المقيد الحالي لشيدر الدخان المرشح ينتج ملف Dummy رغم ثبوت سلسلة المصدر وGUID. هذا لا يثبت أنه هو الشيدر نفسه لمربع الدخان في لقطة المالك، ولا أن نسخة APK الموجودة على هاتف المالك تحوي التصدير ذاته. لا يجوز تعويضه بشيدر نار 108/34 أو وصفه بأنه PASS داخل اللعبة.

## ملفات إعادة الإنتاج
- scripts/t3_smoke34_sameexport_shaderlab.py
- tests/test_t3_smoke34_sameexport_shaderlab.py
- .github/workflows/raft-t3-smoke34-sameexport.yml
- prompt/coordination/clients/T3/sessions/20261109T1913Z-T3-chat-smoke34-sameexport-v5m8.md

## استكمال هندسي
الخطوة التالية: اختبر ما إذا كان مسار الاستعادة الحالي للشيدرات يغير الـDummy **للهوية الأصلية نفسها** إلى برنامج صحيح، مع مقارنة المصدر والـPass وColorMask/Alpha ومراجع البرنامج. بعد ذلك فقط نفّذ تحقق Unity/Android فعلي من مؤثر الدخان. لا تنشر الأصول الأصلية أو أسماء المراجع الخاصة أو PathID/GUID، ولا تخلط بين نتيجة هذا التصدير وإصلاح اللعبة. لم يعدل T3 أي أصل Unity/OBB/APK في هذه الدورة.

**القرار:** source→same-instance export classified SUCCESS / exported ShaderLab is DUMMY / Android game pixels UNKNOWN / RENDER-002 OPEN NOT_READY 0/3.
