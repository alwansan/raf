# T3 — وجود برامج D3D11 الأصلية لشيدر الدخان 34 وإمكان استعادتها

**9 نوفمبر 2026 · RENDER-002 OPEN · NOT_READY 0/3**

## التسلسل المثبت
1. [CI42679312674](https://github.com/alwansan/raf/actions/runs/42679312674) SUCCESS: شيدر أصلي Shader48 محدد بهوية المصدر من 17 ParticleSystemRenderer و34 خانة Material، مختلف عن شيدر النار الذي له الرتبة نفسها. Pass أصلي واحد: Alpha-dependent Color/Alpha Blend، ColorMask RGB، ZWrite OFF.
2. [CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) SUCCESS: تتبع مصدر الشيدر نفسه عبر W1+B02 إلى نفس تصدير AssetRipper، ثم ملف ShaderLab الأصلي المحدد من GUID الخاص. النتيجة الفعلية ACTUAL_DUMMY_SHADER_TEXT_EXPORTER؛ الفقد مؤكد في التصدير المقيد، لا APK الهاتف.
3. [CI42683328646](https://github.com/alwansan/raf/actions/runs/42683328646) SUCCESS على commit 0a59489bc7c027a1e0a8515b9c559e1b911e77ea: إعادة قراءة الهوية من مصدر ZIP2 الأصلي وتعداد برامج D3D11 داخل Shader48 وربط Varianten Vertex/Fragment اعتمادًا على مراجع Pass ومفاتيح permutations الحقيقية. [الأثر الآمن 13703831211](https://github.com/alwansan/raf/actions/runs/42683328646/artifacts/13703831211).

## الأرقام الموثقة من المصدر الأصلي SHA-pinned
| الخاصية | القيمة |
|---|---:|
| المشاهد الأصلية المفحوصة | 6 |
| ملفات Shader/Material المحققة SHA | 4 |
| سجلات D3D11 في الشيدر | 8 |
| نسخ Vertex Shader الأصلية المرتبطة | 2 |
| نسخ Fragment Shader الأصلية المرتبطة | 2 |
| أزواج VS/FS متطابقة بالـkeyword permutation | 2 |
| برامج D3D11 أصلية مميزة مرتبطة | 4 |
| نسخ مراحل تحتوي Keywords | 2 |
| نسخ Vertex غير مطابقة | 0 |
| نسخ Fragment غير مطابقة | 0 |
| Pass طبيعي مع زوج مطابق | 1 |
| Pass بدون زوج مطابق | 0 |

حالة CI المصدر: SOURCE_SHA_ORIGINAL_SMOKE34_D3D11_STAGES_CLASSIFIED؛ مؤشر وجود زوج D3D11 يساوي TRUE، لكن يظل تحقق البرنامج المترجم إلى Android FALSE.

## لماذا هذه النتيجة مختلفة؟
البرامج الأصلية موجودة رغم أن نفس Shader48 أُخرج من AssetRipper كملف Dummy. يمكن الآن التحقيق في سلسلة DXBC → SPIR-V → GLSL/HLSL مع الحفاظ على زوجين وKeywords حقيقيين، بدل إنتاج shader بديل بصريًا. إن حصلت ترجمة صحيحة إلى ShaderLab ودعم Unity 2021، يمكن إجراء اختبار أصلي شفاف مع نفس بيانات المصدر والـPass.

## الحدود
- 8 سجلات جدول D3D11 ليست 8 برامج مترابطة؛ ما ثبت هو 4 برامج مميزة مرتبطة مقسمة إلى زوجين VS/FS.
- لا يتضمن التقرير أي كود DXBC أو hashes فريدة أو GUID/PathID أو أسماء GameObject، ولا يمكن استخلاص البرنامج الأصلي منه.
- D3D11 الأصلي ليس Vulkan أو GLES ولا يثبت نجاح برنامج مترجم. لم تُختبر الدقة البصرية، texture alpha، vertex streams، ترتيب Pass النهائي أو جهاز Android.
- اسم smoke-like تلميح دلالي من GameObject؛ ليس إثبات أن الهاتف يعرض هذا الشيدر وراء المربع الذي شاهده المالك.
- لم يغيّر T3 ملفات Raft/Unity أو .meta/OBB/APK/XAPK.

## ملفات التجربة
- scripts/t3_original_smoke34_dxbc_program_inventory.py
- tests/test_t3_original_smoke34_dxbc_program_inventory.py
- .github/workflows/raft-t3-original-smoke34-dxbc-inventory.yml
- prompt/coordination/clients/T3/sessions/20261109T1924Z-T3-chat-smoke34-dxbc-source-p9n2.md

## الخطوة التالية
تجربة معزولة على زوجي برامج DXBC الأصليين إلى SPIR-V/GLSL، مع فحص عناوين/مكوّنات Stage I/O واختبار linker/variants والحفاظ على تعليمة ColorMask RGB وZWrite Off وAlpha blending. لا تتجاوز source→Unity→device acceptance ولا تنتج APK قبل إثبات مرحلة الترجمة. **RENDER-002 OPEN NOT_READY 0/3.**
