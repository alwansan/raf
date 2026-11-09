# T3 — حالة Pass الأصلية لشيدر الدخان ذي 34 خانة (9 نوفمبر 2026)

**الدليل:** [GitHub Actions 42679312674](https://github.com/alwansan/raf/actions/runs/42679312674) — **SUCCESS** على commit `e7494f1e07a9bca158e95a394986087e47c3b2ed`. [الأثر الآمن 13702410264](https://github.com/alwansan/raf/actions/runs/42679312674/artifacts/13702410264). **المصدر:** ZIP2 الملتزم SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، ستة مشاهد وأربعة مالكي Shader/Material تحققوا بــSHA مستقل.

## ماذا أثبتنا بالبيانات الأصلية؟
- جرى المرور الحقيقي عبر `GameObject.m_Name → ParticleSystemRenderer → Material21 → Shader48` داخل الرسوم البيانية للمشاهد الأصلية. **17** Renderer ذات مؤشرات أسماء smoke-like تربط **34** خانة مادية بشيدر أصلي واحد خاص، رغم وجود شيدر آخر للـfire له **رتبة 34 ذاتها**. لا يعتمد الاختيار على الرتبة وحدها.
- قرأ UnityPy==1.23.0 الـ`m_ParsedForm` للشيدر الأصلي المحدد من أصل Shader48 وأعاد **SubShader واحدًا وPass أصلي عادي واحدًا**.
- حالة الـPass الأصلية كما سُجلت (تصنيفات عامة لا أسرار):

| الحقل | نتيجة المصدر المثبتة |
| --- | --- |
| rtSeparateBlend | `false` |
| Color Blend | `ALPHA_DEPENDENT` |
| Alpha channel Blend | `ALPHA_DEPENDENT` |
| Blend operation | مُعرّفة للألوان والألفا |
| ColorMask | `RGB` — bit mask انتقائي (Unity ABGR semantics) |
| ZWrite | `OFF` |
| ZTest | `ENABLED_NUMERIC`؛ القيمة العددية المحددة لم تُصدّر |
| Cull | `OFF` |
| AlphaToMask | `OFF` |
| W1 fixed render_state without opt-in | **غير مقبول** `false` |
| W1 `allow_selective_color_mask=True` | **مقبول** `true` |

### الدلالة الهندسية
**ملاحظة قابلة للاختبار:** إهمال `ColorMask RGB` أو رفض الحالة عند التصدير قد يغيّر الشفافية/القنوات في نسخة Android. هذا **احتمال** وليس سببًا مُثبتًا للمربع في لقطة الهاتف. نموذج الحالة الحقيقي يعتمد على Blend للألوان والألفا، ولا يكتب قناة alpha في هدف الرسم، ويعطّل كتابة العمق. لذلك لا يجوز تطبيق Pass مع `ColorMask RGBA` أو `ZWrite On` افتراضيًا دون فحص الـShaderLab الناتج الفعلي. قد يكون اختلاف القنوات مقصودًا للمؤثر.

### حدود لا يجوز تجاوزها
- أسماء GameObject مجرد **تلميح دلالي**؛ الهوية الوحيدة المستخلصة أصلية لكنها ليست إثبات هوية مؤثر مربع الدخان الظاهر على الهاتف.
- **لم تُفحص بعد** حالة `ShaderLab` المصدّر للشيدر نفسه في تصدير AssetRipper الواحد، الـcompiled variant/keywords، محتوى Alpha في Texture2D، مكونات الـParticleSystemRenderer vertex streams أو Pixel من اللعبة.
- نجاح هذا الـCI لا يساوي قبول Raft Android، ولا يصلح `EVIDENCE_READY` في المختبر المصغر ليكون `PASS` في اللعبة.
- لا تتضمن التقارير أسماء أصلية، GUID/PathID أو bytecode، ولا جرى رفع أصول أو تعديل Unity/ملفات اللعبة أو إنتاج APK/XAPK.

## كيفية إعادة الإنتاج
1. `scripts/t3_original_smoke34_pass_probe.py` يصادق المصدر ويختار مرشح الدخان عبر روابط private actual source.
2. `tests/test_t3_original_smoke34_pass_probe.py` يغطي الحالات السلبية (رتبتان متماثلتان، تكرار Renderer، نقص/غموض الرابط، Pass غير عادي، تسرب أسماء).
3. `.github/workflows/raft-t3-original-smoke34-pass-probe.yml` يجهز المشاهد الستة والملفات الأربعة SHA-pinned ثم ينشر **JSON آمنًا فقط**.
4. راجع CI42679312674 ومقارنة التصنيفات؛ لا تستخرج بيانات خاصة خارج runner.

## التجربة الهندسية التالية
نفّذ **تصديرًا خاصًا واحدًا محدودًا** للشيدر المحدد بالهوية الأصلية نفسها مع AssetRipper ثم احسب هل يتضمن `Blend SrcAlpha/OneMinusSrcAlpha` / separate alpha / `ColorMask RGB` / `ZWrite Off` وما إذا خرج DummyShaderTextExporter أو سقطت Varianten. قارِن الآن source→same-export بدلاً من مقارنة أسماء متشابهة. عند اختلاف مثبت، جرّب تصحيح `ColorMask` المحدد ثم تحقق من Unity/Android Pixel على Raft نفسها. إذا كان مطابقًا، انتقل إلى texture alpha، renderer streams والـvariant لا إلى فرضية ColorMask كسبب.

**الجاهزية:** `RENDER-002 OPEN`، اللعبة `NOT_READY 0/3`، لم يصدر APK جديد.
