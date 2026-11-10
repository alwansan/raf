# سجل دفعات التحقق من الأنماط الأصلية Shader48 (GFX-LAB)

**المصدر المثبت:** `alwansan/raf`, ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. فرع العمل الوحيد `experiment/android-graphics-rootcause`.

## اختيار العينات
تعيد الأداة تحليل 524 زوج VS/FS أصلياً، وتبني **157 فئة مستقلة عن اسم الخاصية** داخل الـPass من اتحاد توقيع (1) سجلات `b/t/s` وأطوال Constant Buffers و(2) أزواج Texture/Sampler المستخدمة فعلاً في تعليمات DXBC. ترتيب الممثلين الأصليين يُحسب فقط داخل CI Runner ويُختار بشكل حتمي عبر Pass Round Robin. **لا نحفظ معرّفات Variants أو بَصمات التواقيع أو السجلات في Git العام.** الدفعات ذات النطاقين المنفصلين لا تكرر عينات المصدر الخاصة ما دام SHA وخوارزمية الاختيار ثابتين.

| التجربة | نطاق الفهرس الخاص [البداية، النهاية) | عدد الممثلين | GitHub Actions | النتيجة |
|---|---|---:|---|---|
| GFX-MULTI-056 | [0,24) | 24 | [42857815446](https://github.com/alwansan/raf/actions/runs/42857815446) | SUCCESS، 24/24 |
| GFX-MULTI-057 | [24,48) | 24 | [42859754233](https://github.com/alwansan/raf/actions/runs/42859754233) | SUCCESS، 24/24 |
| GFX-MULTI-058 | [48,72) | 24 | [42861618032](https://github.com/alwansan/raf/actions/runs/42861618032) | SUCCESS، 24/24 |
| GFX-MULTI-059 | [72,96) | 24 | [42863853554](https://github.com/alwansan/raf/actions/runs/42863853554) | SUCCESS، 24/24 |
| GFX-MULTI-060 | [96,120) | 24 | [42865341763](https://github.com/alwansan/raf/actions/runs/42865341763) | SUCCESS، 24/24 |
| GFX-MULTI-061 | [120,144) | 24 | [42866819484](https://github.com/alwansan/raf/actions/runs/42866819484) | SUCCESS، 24/24 |
| GFX-MULTI-062 | [144,157) | 13 | [42870125986](https://github.com/alwansan/raf/actions/runs/42870125986) | SUCCESS، 13/13 |

- **تغطية CPU البنيوية المؤكدة لممثلي الفئات: 157/157 فئة أصلية**، **0 فئات ممثلة غير مفحوصة** (ليس 524/524 برنامج Variant).، ولا توجد اختبارات CPU لكل واحد من الأزواج الـ524 منفرداً.
- GFX056: **48/48** مراحل تساوى فيها استخدام t/s، **46/46** مرحلة ذات CB تؤكد هوية b وبنية UBO، **662/662** نطاقات CB ثابتة مدعومة لديها قراءة SPV، و**81** وصولاً ديناميكياً غير محسوم.
- GFX057: **48/48** مراحل تساوى فيها استخدام t/s، **47/47** مرحلة ذات CB تؤكد هوية b وبنية UBO، **645/645** نطاقات CB ثابتة مدعومة لديها قراءة SPV، و**187** وصولاً ديناميكياً غير محسوم.
- الدليل الحالي مستوى **ORIGINAL_SOURCE + CPU COMPILER SPV structural checks**. يظل `originalShaderRestored=false`: لا رابط أصلي مثبت بين خصائص Shader48 في Unity وDXBC t/s/b، ولا إثبات شامل لتعليميات كل Variant أو استيراد Unity أو اختبار GPU Adreno/هاتف المالك.

### استئناف مضبوط
اكتملت الدفعة الأخيرة [144,157) بنجاح، بفحص 13 زوجاً VS/FS أصلياً دون تعديل T1–T5، وسجّل كل زوج غير مطابق ضمن العدادات الآمنة. إذا فشل أي فحص، لا ترفع عدد الفئات المجتازة باعتبار تشغيل CI فقط ناجحاً. أبقِ المصدر الأصلي وDXBC/SPV في CI المؤقت مع التطهير النهائي، وحدث `prompt/graphics-lab/RESTORE_AR.md`, `memory/STATE.json`, `memory/MEMORY.md`, ملف جلسة مستقل وذاكرة خطة العمل.

- GFX058: **48/48** مراحل تساوى فيها استخدام t/s، **48/48** مرحلة CB تؤكد الاسم والبنية، **645/645** نطاقات Vec4 الثابتة المدعومة طابقت القراءة، و**240** وصولاً CB ديناميكياً/ممتداً غير محسوم. CI42861618032 نجاح/Source purge مؤكد؛ artifact 13785685895 يضم عدادات آمنة فقط. **المجموع الآن 72/157**؛ لا يُعد ذلك استعادة كاملة أو اختبار هاتف.

- GFX059: **48/48** مراحل مصدرية حقيقية تطابق فيها استخدام t/s، **48/48** مرحلة ذات CB تؤكد الاسم والبنية، **725/725** نطاقات CB الثابتة المدعومة لديها قراءة SPV، و**251** وصولاً ديناميكياً/ممتداً غير محسوم. CI42863853554 نجاح وsource purge مؤكد؛ artifact13786102979 آمن للعدادات فقط. **96/157** ممثلاً مجتازاً، **61** لم تُترجم بعد؛ ليست مساواة بكسلات أو استعادة كاملة.

- GFX060: **48/48** مراحل DXBC/SPV استخدمت أزواج t/s نفسها، **48/48** مرحلة CB ذات الاسم والبنية الأصلية، **793/793** نطاقات Vec4 ثابتة مدعومة لها قراءة SPV، و**224** وصولاً ديناميكياً/ممتداً غير محسوم. CI42865341763 SUCCESS، source purge مؤكد وartifact13787081871 آمن؛ **120/157** ممثلاً اجتاز CPU، **37** غير مختبر، ولا يعد ذلك تكافؤاً بصرياً أو استعادة كاملة.

- GFX061: **48/48** مرحلة أصلية تطابقت فيها أزواج استخدام Texture/Sampler، **48/48** مرحلة CB ذات اسم SPV Uniform الأصلي وبنية vec4، **865/865** نطاق Vec4 ثابتة ضمن التعليمات المدعومة لها قراءة SPV، و**129** وصولاً ديناميكياً/ممتداً إلى CB غير محسوم. [CI42866819484](https://github.com/alwansan/raf/actions/runs/42866819484) SUCCESS وprivate-source purge مؤكد، artifact13788440771 آمن للعدادات. التقدم الآن **144/157** فئة ممثلة مجتازة لفحوص CPU البنيوية، **13** غير مختبرة. ليست استعادة كاملة أو تكافؤ بكسلات.

- GFX062: **26/26** مرحلة Vulkan1.1 SPV واستخدام t/s الأصلي، **26/26** مرحلة CB لها SPV Uniform global/vec4 layout، **476/476** نطاق CB ثابت مدعوم قرئ في SPV، **78** وصول CB ديناميكياً غير محسوم. [CI42870125986](https://github.com/alwansan/raf/actions/runs/42870125986) SUCCESS، 432 اختبارات، source purge مؤكد، safe artifact13788687447.
- **الإجمالي النهائي لنطاق الفئات الممثلة:** **157/157** عبر سبعة تشغيلات مستقلة، **314/314** مرحلة SPV ومطابقة استخدام t/s، **311** مرحلة ذات CB و**3** مراحل بلا CB، **4811/4811** استعمال نطاق CB ثابت ضمن التعليمات المدعومة، **1190** استعمال CB ديناميكي/ممتد غير محسوم. العدّ لظهور استعمال ضمن فئة ممثلة، لا لكل برامج الـ524 أو البرامج المميزة؛ `originalShaderRestored=false`. لا توجد دفعة ثامنة. المرحلة التالية فك الفهرسة الديناميكية وإثبات الرابط الأصلي Material→GPU على حدة.

## GFX-MULTI-065 — source-private [0,24) extended literal CB SPV range test (CI_PENDING, 2026-11-10)
- Session 20261110-GFX-chat-extended-literal-batch0-24-39; origin=chat; base c3e8df433b3c521d467672fe17a6e8e9069c73e7; only experiment/android-graphics-rootcause writing.
- New independent first 24 authentic Pass-joint representative source pairs, 48 stage SPV validation, real b global/vec4 UBO and source modifier-literal range→actual SPV OpLoad observations. Recheck GFX063/064 763/427/6800 source operand partition and 656 distinct source stage-local ranges; no source-private identifiers published. CI link/status must be confirmed after push; source purge always.
- This expands earlier GFX064 7-Pass pilot. Matching only a distinct range does not prove source operand identity/numeric modifier semantics, 427 dynamic-index expression parity, GFX054 Material property bindings, full Shader48 GPU runtime, Adreno pixels. originalShaderRestored=false, phase_closed=false.
