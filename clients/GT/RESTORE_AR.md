> **استئناف GT — 28 نوفمبر 2026:** اقرأ [قرار المالك](OWNER_DIRECTIVE_RESTORE_FIRST_AR.md)، [الخطة](RESTORATION_PLAN_AR.md)، [RESTORATION_PLAN.json](RESTORATION_PLAN.json)، [state.json](state.json)، [الذاكرة](MEMORY.md) و[سجل الاستعادة السابق](RESTORE_HISTORY_20261128.md). مرجع علي المثبت: [1a78eb276](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md).

## آخر نتيجة متحققة
[Actual 46128563088](https://github.com/alwansan/raf/actions/runs/46128563088/job/140928500873) و[lint 46128563099](https://github.com/alwansan/raf/actions/runs/46128563099) ناجحان؛ [Plan Guard 46128563095](https://github.com/alwansan/raf/actions/runs/46128563095) فشل بسبب حجم الملفات قبل الاختبارات. [إيصال آمن](sessions/20261128-top-native-bc3-array/actual-46128563088.json).

G5 Particle108: source emitter Actual 46137313462/job 140955391915 PASS, 7/7 controls, guard 46137313348 and lint 46137313365 PASS. Exact six scenes/six owners: 12/12 source reciprocal GameObject/ParticleSystem/Renderer links, 24 selected Material slots, all 12 Billboard mode0, 48 null Mesh fields, VertexStreams/Shape/Emission present 12/12. Source RGB mask, alpha-dependent blend, depth write off; no device/phone emitter identity or geometry drawn. Next actual same-export emitter lineage gate: trace original class1/198/199 and Material21 in one disposable export, verify selected 12 reciprocal component graphs and ordered 24 Material edges, exact vertex stream bytes and serialized billboard settings, module enable flags; classify unmatched values separately; native seven-mip same-export binding admitted again only for same-instance identity, no alpha GPU replay or Unity/player/XAPK. Source vs export field parity is not runtime generated geometry/keyword proof. White mesh G1–G3 open; all G0–G6 open.

## الخطة والحالة
[ledger](ledger/README.md) يحفظ السجلات التاريخية. القراءة الكاملة عبر `scripts.gt_restoration_plan_check._read`؛ الحقول النشطة مباشرة. السجل السابق محفوظ في نفس المجلد مع روابطه النسبية. تحقق من HEAD وActions قبل كل دفعة.

## الحدود
مرشح الإصلاح خاص بمرجع native class187، بلا تغيير للشيدر الأصلي أو GUID/fileID/UV. لا دمج إنتاجي ولا ادعاء رسم أصل أو إصلاح أبيض. لا XAPK قبل الاستعادة الكاملة؛ CL والمختبر للقراءة فقط وBLACK والأنيميشن مؤجلان.

## تحقق تنظيم الخطة
[Plan Guard 46129561453](https://github.com/alwansan/raf/actions/runs/46129561453/job/140931533182) و[lint 46129561451](https://github.com/alwansan/raf/actions/runs/46129561451) نجحا على `c9b239b4`؛ 11 اختباراً وفحص روابط الاستعادة. 12 workstream و6 milestones، 770 Dummy عند لقطة postvendor التاريخية، صفر workstream متحقق هاتفياً. لا تغيّر ذلك إلى ادعاء اكتمال. اختبار المصدر الخاص بمرشح المرجع منفصل، دون Unity أو ZIP2 أو بناء لاعب.

## الدفعة الجديدة — ABI للمسار الأصلي
فشل [اختبار المصدر](https://github.com/alwansan/raf/actions/runs/46129648557/job/140931781926) قبل التنفيذ بسبب sparse-checkout؛ تم تصحيح الاعتماد. أضيف مسار source ABI مستقل دون Unity أو بناء لاعب؛ يجب التحقق من نتيجته ثم تنفيذ الرسم الأصلي. لا تعتبر مطابقة أسماء أو مواقع registers وحدها قبولاً للبكسلات.

**تنفيذ ABI:** [46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) · [اختبار المرجع](https://github.com/alwansan/raf/actions/runs/46130201606/job/140933442964) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46130201658) · [lint](https://github.com/alwansan/raf/actions/runs/46130201615). تحقق من حالات التشغيل الحية.

## تصحيح مخطط TexEnv — 28 نوفمبر
[Actual ABI 46130201775](https://github.com/alwansan/raf/actions/runs/46130201775/job/140933443625) توقف بعد 10/10 Mesh و8/43 قيم الخامة. [الإيصال](sessions/20261128-top-native-bc3-array/actual-46130201775.json). الخطة الخاصة تجهيزها 4 non-null و2 null؛ الكود السابق خلط القائمتين. الإصلاح يبقي التحقق الفعلي من PPtr وUV لكل الستة، ويختبر غياب/زيادة/عدم تجهيز الموارد دون تخفيف التحقق. الاختبار السابق 9/9 وPlan Guard/Lint ناجحان. لا ادعاء لرسم الشيدر الأصلي.

**إعادة الاختبار:** [Actual ABI 46130918208](https://github.com/alwansan/raf/actions/runs/46130918208/job/140935636020) · [10/10 source controls 46130918152](https://github.com/alwansan/raf/actions/runs/46130918152/job/140935635357) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46130918182) · [Lint](https://github.com/alwansan/raf/actions/runs/46130918205). لا استعادة بصرية كاملة بعد.

## ربط ABI الأصلي — نتيجة فعلية
[46130918208](https://github.com/alwansan/raf/actions/runs/46130918208/job/140935636020) و[الإيصال](sessions/20261128-top-native-bc3-array/actual-46130918208.json): 55 موقع CB و8 texture و7 sampler و2 برنامج أصلي؛ ثبت استعمال BC3 في route المختار، و6/6 PPtr/UV و3/3 ضوابط. تعثر فقط تفسير dimension؛ نختبر low nibble مع الاحتفاظ بالبايت وفحص stride، ثم تجميع مرشح HLSL بمدخلين. لا ادعاء رسم أو نجاح Unity. 3 موارد خارج Material و1 null ما تزال بحاجة تحقق الربط الفعلي.

**تنفيذ packed layout + merged pair:** [Actual 46131690207](https://github.com/alwansan/raf/actions/runs/46131690207/job/140938034964) · [Source controls](https://github.com/alwansan/raf/actions/runs/46131690209/job/140938034663) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46131690211) · [Lint](https://github.com/alwansan/raf/actions/runs/46131690217).

## نجاح ABI ومرحلة الرسم المعزول
[Actual 46131690207](https://github.com/alwansan/raf/actions/runs/46131690207/job/140938034964) و[إيصال آمن](sessions/20261128-top-native-bc3-array/actual-46131690207.json). 940 رأساً، 30080 بايت، stride32، 4 قنوات؛ 28 saved numeric و5 ST و22 global/runtime candidates. 2/2 HLSL compiled، 55 CB offsets للمرحلتين قبل الدمج، لا تحقق Unity بعد. مرشح اختبار رسم فعلي خاص بمسار واحد مع الأصل نفسه و3 صور وBC3، وضوابط Dummy وwrong GUID/fileID؛ البيئة التشخيصية ليست المشهد الأصلي. لا إنتاج ولا XAPK.

**تنفيذ الرسم المعزول:** [Actual 46132602361](https://github.com/alwansan/raf/actions/runs/46132602361/job/140940852671) · [Source controls](https://github.com/alwansan/raf/actions/runs/46132602109/job/140940851576) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46132602151) · [Lint](https://github.com/alwansan/raf/actions/runs/46132602087). إضافة إعادة الرسم type2 للتحقق من الثبات؛ ABI المنفصل يدوي لأن مسار الرسم ينفذ بوابته نفسها. لا تشغيل لاعب أو إنتاج أو XAPK.

## الرسم الفعلي — تشخيص عدم اختلاف المرجع
[46132602361](https://github.com/alwansan/raf/actions/runs/46132602361/job/140940852671) و[الإيصال](sessions/20261128-top-native-bc3-array/actual-46132602361.json): Unity نجح بتجميع الشيدر ورسم المجسم، بيانات Mesh وBC3 والـsampler و4/4 refs و6/6 UV و29/29 قيم مقروءة مطابقة. 3/3 زوايا تختلف عن Dummy، لكن صفر فرق أكبر من 1/255 بين type2 وtype3/wrong GUID/fileID. اختبار جديد مستقل عن إعادة فحص المرجع: استبدال BC3 في نسخ Material بمصفوفتين authored red/green، وtap تشخيصي لمواقع العينة في HLSL الأصلي مع معايرة hit/color؛ بوابة البكسلات الأصلية لا تتغير. لا إثبات إصلاح أبيض أو تطابق المشهد أو جهاز.

**تنفيذ causal tap:** [Actual 46133315975](https://github.com/alwansan/raf/actions/runs/46133315975/job/140943060123) · [Source controls](https://github.com/alwansan/raf/actions/runs/46133315939/job/140943060008) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46133316064) · [Lint](https://github.com/alwansan/raf/actions/runs/46133315946). نجاح تشخيص منفصل ليس نجاح بوابة المرجع أو إصلاح الأبيض.

## نتيجة causal tap والانتقال إلى G5
[Actual 46133315975](https://github.com/alwansan/raf/actions/runs/46133315975/job/140943060123) و[الإيصال](sessions/20261128-top-native-bc3-array/actual-46133315975.json): 3/3 source override مطابقة تماماً، red/green صفر فرق تماماً. tap 3 مواقع نجح خارج Unity ولم يكتمل داخله (0 views)، لا نتيجة سببية. لا نكرر الرسم نفسه؛ G5 Particle108 يربط 7 mip/21844 بايت و5 Materials/10 PPtr UV من نفس التصدير بالمسارات الأربعة و8 stage وsample operands الأصلية، ويفصل valid/invalid saved keywords عن اختيار runtime. لا GPU alpha replay ولا إنتاج/XAPK. الأبيض مفتوح.

**تنفيذ G5 Particle108:** [Actual 46134067566](https://github.com/alwansan/raf/actions/runs/46134067566/job/140945349271) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46134067507) · [Lint](https://github.com/alwansan/raf/actions/runs/46134067551). ينتظر إثبات ربط مسار Keywords المحفوظ وsample operands مع target الأصلي، دون تكرار قراءة alpha السابقة.

## G5 — نجاح ربط المصدر ومسار الرسم الأصلي
[46134067566](https://github.com/alwansan/raf/actions/runs/46134067566/job/140945349271) و[الإيصال](sessions/20261128-particle108-native-route/actual-46134067566.json): 7 mip/21844 بايت، 10/10 PPtr+UV، 5/5 Shader وKeywords، 4 routes/8 stages/10 samples. الخامات الخمس تستخدم route محفوظاً واحداً؛ target native في خانة واحدة وخامة واحدة ويُقرأ فعلياً في DXBC الخاص بها. الجديد: Unity explicit route مع Material الأصلية ومرجعي Texture من نفس التصدير، quad مؤلف فقط، force alpha 0/1 مع RGB/sampler ثابتين وclone exact وrepeat على حجمين وخلفيتين. لا ادعاء أصالة الباعث أو اختيار runtime أو إصلاح الهاتف. ABI route المنفصل يدوي لتجنب التصدير المكرر.

**تنفيذ G5 original draw:** [Actual 46134943151](https://github.com/alwansan/raf/actions/runs/46134943151/job/140948020250) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46134943095) · [Lint](https://github.com/alwansan/raf/actions/runs/46134943093). لا ادعاء نجاح الرسم قبل إيصال Unity والبكسلات، ولا إنتاج/XAPK.

## G5 — فصل عائق ضوابط الرسم عن ألفا
[Actual 46134943151](https://github.com/alwansan/raf/actions/runs/46134943151/job/140948020250) و[إيصال](sessions/20261128-particle108-native-route/actual-46134943151.json). Unity compiled، 4/4 refs+meta، 11/11 saved values، companion RGBA 1048576/1048576، 28 draws؛ الأصل مرئي وثابت 4/4، لكن Dummy غير مرئي وclone/zero/one تطابق clear، لذلك causal gate فشل. الجديد: GPU clone parity probe (Load وSampleLevel عند mip0/3)، force alpha RGB controls، command buffer pass0 مع Material الأصلية نفسها وMPB فقط، Dummy clip-space وRenderer baseline مستقل؛ لا تخفيف للقبول. لا إنتاج ولا XAPK.

**تنفيذ G5 clone/control:** [Actual 46135691627](https://github.com/alwansan/raf/actions/runs/46135691627/job/140950375504) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46135691582) · [Lint](https://github.com/alwansan/raf/actions/runs/46135691572). 17 GPU clone probe draws + 36 explicit/renderer diagnostic draws planned; لا قبول قبل النتائج الفعلية.

## G5 — إثبات تأثير Alpha المعزول وبقاء Dummy
[Actual 46135691627](https://github.com/alwansan/raf/actions/runs/46135691627/job/140950375504) و[إيصال](sessions/20261128-particle108-native-route/actual-46135691627.json): 17 GPU probe و36 draw، 4/4 clone RGBA GPU مطابقة تماماً عند mip0/3 وLoad/Sample، zero/one RGB محفوظة وألفا دقيقة. 4/4 source block/clone/renderer/command/repeat مطابقة ضمن 1/255، zero=clear؛ one vs zero: 1859/7459 بكسل للحجمين بالخلفيتين. الأصل ظاهر وقيمه وهويته محفوظة. strict gate فشل بسبب Dummy غير مرئي. الجديد: lifecycle probe للـMaterial المؤقت قبل/بعد NewScene (فرضية لا نتيجة)، إنشاء الضوابط بعد المشهد، منع تجاوز null للأمر المتوقع، 4 direct Dummy + 4 camera Dummy + 28 explicit commands؛ لا تخفيف للشرط أو ادعاء إصلاح اللعبة/الهاتف.

**تنفيذ G5 lifetime/control:** [Actual 46136487398](https://github.com/alwansan/raf/actions/runs/46136487398/job/140952830477) · [Plan Guard](https://github.com/alwansan/raf/actions/runs/46136487390) · [Lint](https://github.com/alwansan/raf/actions/runs/46136487394). تحقق من عمر Material وضابطَي الرسم المباشر والكاميرا؛ لا قبول قبل نتيجة فعلية.

## G5 — معايرة Alpha والانتقال إلى باعث المصدر
[Actual 46136487398](https://github.com/alwansan/raf/actions/runs/46136487398/job/140952830477) و[الإيصال](sessions/20261128-particle108-native-route/actual-46136487398.json): نجاح معزول، NewScene أتلف Material القديم رغم بقاء المرجع المُدار؛ الجديد حي، 4/4 كاميرا و4/4 مباشر، 28 أوامر، 36 draw، 4/4 فرق Alpha و4/4 تطابق GPU clone. [Plan Guard](https://github.com/alwansan/raf/actions/runs/46136487390) و[Lint](https://github.com/alwansan/raf/actions/runs/46136487394) ناجحان. لا إثبات إصلاح النار أو هندسة باعث الهاتف أو اختيار runtime keywords. بوابة جديدة: [source emitter](../../.github/workflows/raft-gt-particle108-source-emitter.yml) لربط الخامة المستهدفة بمرجع Renderer وGameObject وParticleSystem الأصلي، وتصنيف RenderMode ومراجع Mesh ومعلومات VertexStreams وحالة المزج. لا إعادة ألفا أو Unity/Player/XAPK. لا قبول قبل إيصال Actions. الأبيض وG0–G6 مفتوحة.

## G5 — الباعث الأصلي: 12 Billboard و24 مرجع Material
[Actual 46137313462](https://github.com/alwansan/raf/actions/runs/46137313462/job/140955391915) و[الإيصال](sessions/20261128-particle108-native-route/actual-46137313462.json): 7/7 ضوابط، 12/12 روابط أصلية reciprocal، 24 خانة Material، 48 مرجع Mesh فارغاً، 12/12 VertexStreams/Shape/Emission، RenderMode 0 لجميعها. [Plan Guard](https://github.com/alwansan/raf/actions/runs/46137313348) و[Lint](https://github.com/alwansan/raf/actions/runs/46137313365) ناجحان. الخطوة الجديدة [same-export emitter](../../.github/workflows/raft-gt-particle108-emitter-same-export.yml): class1/198/199 من نفس export وMaterial21، مراجع الخامات وترتيبها، بايتات VertexStreams وإعداد Billboard وأعلام الوحدات، دون Quad اصطناعي أو إعادة Alpha. لا إثبات هندسة runtime أو إصلاح النار على الهاتف. الأبيض وG0–G6 مفتوحة.
