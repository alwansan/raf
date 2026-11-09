# T3 — إثبات ربط دلالات DXBC الأصلية لشيدر الدخان (Shader48/34)

التاريخ: 9 نوفمبر 2026، العامل T3. **المشكلة RENDER-002 تبقى OPEN/NOT_READY 0/3.**

## لماذا أجرينا هذه التجربة؟

كانت نتيجة [CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) أن أسماء 13 متغير دخل و9 خرج في SPIR-V المصدر لا تطابق أي اسم في نسخة HLSL الدائرية؛ لذلك لا يجوز ربطها بالأسماء المولدة. للتحقق من هوية مراحل الرسم الفعلية رجعنا مباشرة إلى أقسام DXBC الأصلية للمدخلات ISGN والمخرجات OSGN وقرأنا أسماء Semantic الخاصة بالمصدر في ذاكرة runner خاصة، دون نشرها.

## المصدر والفحص الأصلي

- المصدر: ZIP2 عند SHA ثابت `15964ea8f246b6e076ce26b60931ee2e1a9a2385`، 6 مشاهد و4 owners مثبتة بصماتهم، يثبتون شيدر دخان أصلية واحدًا مرتبطًا بـ17 عارض ParticleSystemRenderer و34 خانة Material.
- `scripts/t3_original_smoke34_dxbc_semantic_join.py` يختار شيدر Shader48 الأصلي بهويته الخاصة وليس Fire34 ولا Particle108 ولا Shader921؛ ثم يربط زوجَي Vertex/Fragment الأصليين وفق نفس keyword/player-bucket.
- استعمل parser آمن موروث من `scripts/t3_original_921_dxbc_semantic_join.py` لقراءة التواقيع وإجراء مقارنة Semantic+Index والـtype وأقنعة قنوات المتجهات.
- [GitHub Actions CI42691211652](https://github.com/alwansan/raf/actions/runs/42691211652) **SUCCESS**: 10 اختبارات T3 جديدة +21 اختبارًا موروثًا لمحلّل DXBC +7 اختبارات قديمة لربط مرحلة الدخان، أي **38/38**.

## الحقيقة الجديدة من DXBC الأصلي

| الفحص | نتيجة المصدر الأصلي |
|---|---:|
| أزواج VS/FS ذات keyword متطابق | 2 |
| برامج DXBC الأصلية المقروءة | 4 |
| روابط Semantic+Index الأصلية المتطابقة | 7 |
| مدخلات Fragment الدلالية | 7 |
| مخرجات Vertex الدلالية | 7 |
| مدخلات Fragment الدلالية بلا مخرج Vertex | **0** |
| قنوات Fragment غير المغطاة من Vertex | **0** |
| اختلاف أنواع البيانات في Semantic المتطابق | **0** |
| قنوات Fragment المعلنة | 28 |
| قنوات Vertex المعلنة | 28 |

هذا يثبت سلامة الربط **بين برامج DXBC الأصلية نفسها** داخل النطاق الذي فُحص. ولكنه لا يثبت وصول هذه الـSemantics إلى Location/Component الصحيح في SPIR-V، ولا عمل ShaderLab/Unity/Adreno أو شكل الدخان فعليًا.

## الأدلة والحدود

Artifact JSON آمن [13707545897](https://github.com/alwansan/raf/actions/runs/42691211652/artifacts/13707545897)، تنتهي صلاحيته 16 نوفمبر 2026 الساعة 20:15 UTC. لا يحوي DXBC/HLSL/GLSL أو أسماء Semantic الأصلية أو GUIDs/PathIDs/bytecode؛ عدادات فقط.

الخطوة التالية: احصر القنوات المستخدمة فعلاً من DXBC Fragment ReadMask، وقارن عددها بصورة مستقلة مع SPIR-V المنبع والدائري، ثم تحقق من اقتران semantic→location دون اعتماد أسماء مترجم غير مستقرة. لا حاجة الآن إلى APK مختبر جديد أو XAPK كامل. احتفظ بالمؤثرات/الصوت/الإعدادات والحفظ وملفات العملاء الأخرى.
