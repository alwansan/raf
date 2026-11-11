# إغلاق المرحلة الأولى واختبار الهاتف الموحّد

النطاق هو العينات والأبواب في [وثيقة إغلاق المرحلة](SHADER48_MODEL_PHASE_CLOSURE_AR.md). نتيجة GFX120 تغلق تجربة Forward المضبوطة للمجسم M02 على Adreno. متوسط خطأ الصورة المضاءة مقابل Mesa هو 0.102 من 255 لكل قناة مع تطابق التغطية، واستجابت اختبارات الضوء والنتوء والمعدنية. شغّل GFX121 أيضًا DXBC الأصلي في D3D11 WARP. تطابقت أقنعة التغطية في الحالات الأربع مع Adreno، وتطابقت صورة حالة إطفاء الضوء بالبايت. اختلفت بصمات الصور الثلاث الأخرى، وقياس مقدار فرق اللون مع Windows ما زال مفتوحًا.

أربع حزم عمل ما زالت مفتوحة. الحزمة قد تحتوي أكثر من حالة رسم، لذلك لا يوجد عدد ثابت للتجارب الفردية قبل حسم اختلافات مراجع Windows.

| الحزمة | العمل قبل تسليم الهاتف | الحالات التي تدخل الاختبار الموحد |
|---|---|---|
| برامج Shader48 وحالات الرسم | تجهيز حالات Pass/keywords المستخدمة في نطاق المرحلة، والتحقق من مدخلات Unity وموارد كل Pass وأثر العمق والقص والمزج والظلال بحسب استخدامه | عينات ممثلة لحالات الرسم المطلوبة، مع تسجيل الزوج والـPass والقيم المطَبقة |
| المجسمات والخامات | إعادة استعمال الربط على مجسم بسيط ومجسم بمادتين، والتحقق من مشاركة الخامات والـUV وملفات mip الأصلية | المجسم البسيط، مادتا M03 كل على حدة ومعًا، وعينة جديدة لإثبات قابلية إعادة الاستعمال |
| الحركة | إكمال العرض عبر الزمن، مع مقارنة الحركة الأصلية والتحويلات بالمرجع، واستكمال حالات الهياكل المعقدة ضمن النطاق | مقطع متحرك مضبوط، لقطات عند أزمنة مثبتة، وحالات الهيكل المطلوبة |
| المرجع والقبول | تشغيل DXBC الأصلي على Windows، ثم مقارنة صور Windows وAndroid بنفس الأصول والكاميرا والإضاءة والحركة. توثيق الأصل والإصدار والفرق. مقارنة مشهد PC الأصلي ضمن نطاق المرحلة | تشغيل تلقائي واحد لكل الحالات الجاهزة، صور وملخص واحد، ثم مراجعة المالك |

ترتيب العمل: اختبار أصغر حالة مكافئة على Windows أولًا، ثم تجهيز بقية الحالات والتحقق منها خارج الهاتف. عند جاهزية مراجع الحالات، تُجمع في APK تشخيصي واحد ويصدّر ملف ZIP واحد إلى `Download/Games/cl/test/g/`. الاختبارات التي نجحت بالفعل تُستخدم كأدلة، ويعاد تشغيل حالة منها فقط عند الحاجة إلى التحقق من الدمج. ظهور اختلاف حقيقي في الحزمة قد يستدعي إصلاحًا وإعادة فحص الحالة المتأثرة قبل الإغلاق.

قبول كل حالة يتطلب صحة مدخلاتها الفعلية، وعدم فشل الرسم، ونتيجة مقارنة مرتبطة بمرجع معروف. نتيجة WARP في مشهد المختبر إثبات لمسار DXBC الأصلي في مشهد مضبوط. اختبار تطابق مشهد اللعبة على PC يحتاج مدخلات ولقطات اللعبة نفسها.

جهّز GFX124 تشغيل خمس حالات Forward في دفعة واحدة مع 17 صورة مرجعية. جرى بناء التطبيق التشخيصي وفحص قراءة سجلّ كامل وآخر بفشل جزئي بإعادة تشغيل صور Mesa. اختبار Android الفعلي وتوسيع الدفعة لحالات الرسم والحركة ومراجع اللعبة ما زالت مفتوحة.

أضاف GFX125 مرجع Windows لكل حالات Forward الجاهزة في الدفعة. تطابقت تغطية 13 لقطة جديدة مع Mesa، وتطابقت ثلاث صور إطفاء الضوء بالكامل. أعطى جرد GFX126 اختيارات مصدر لحالات ForwardAdd وDeferred ومرشحات لتمرير الظل تحتاج إثبات اختيار Unity وحالات الرسم الفعلية.

أضيفت حالة ForwardAdd لـM02 إلى الدفعة، فأصبحت ست حالات و20 لقطة. نجحت تجربة المزج والعمق المضبوطة على Mesa وبناء تطبيق Android. اختبار Windows لهذه الحالة واختيار Unity الفعلي للحالات والأدوار ما زال مفتوحًا.

نجح مرجع Windows لحالة ForwardAdd. أضيفت 15 عينة حركة لـM02 إلى تشغيل Android الموحّد وأصبحت الدفعة سبع حالات و35 لقطة. عينات الحركة تستخدم مواضع وتشوهات محسوبة من منحنيات المصدر، وتشغيل Unity الأصلي ما زال مفتوحًا.

تطابقت تغطية عينات الحركة الـ15 على Windows وMesa. نجح أيضًا اختبار ShadowCaster الأول على Mesa بقراءة مخزن العمق، وبقي إدخال حالاته في التطبيق وتشغيل Windows وإثبات اختيار Unity الفعلي.

أصبحت دفعة Android ثماني حالات و39 لقطة بعد إضافة ShadowCaster. تطابقت أقنعة عمق ShadowCaster الأربعة على Windows وMesa. نجح Deferred في أربعة مخازن مضبوطة على Mesa، وبقي Windows وإضافته للدفعة والتحقق داخل Unity.

## GFX137 — فحص سلامة Deferred قبل اختبار الهاتف

أضيف مدقّق مستقل لجميع لقطات Deferred الاثنتي عشرة قبل قبول نتائج الهاتف: تطابق غطاء RT0 مع المرجع بالبايت، ثبات الغطاء بين اختبارات الخامة، منع تغير مخازن MRT التي لا يفترض أن تتأثر، وإثبات تأثر RT2 بتسطيح النورمال وRT0/RT1 بإلغاء المعدنية. تُحسب فروق كل قناة مقارنة بمرجع Mesa، مع الحفاظ على حقيقة أن الاختلاف الطفيف بين التعريفات ممكن. العدد المخطط للحزمة أصبح **9 حالات و51 لقطة**. لم يُنتج هذا التطوير APK موقّعًا جديدًا، ولم يُشغّل على هاتف المالك بعد. إثبات Unity runtime والمرجع الأصلي للعبة لا يزال مفتوحًا.

### GFX137 VERIFIED CI addendum — 11 Nov 2026
[GitHub Actions 43062691619](https://github.com/alwansan/raf/actions/runs/43062691619) COMPLETED SUCCESS at commit `91fce78d05da873e8cd2a596b77f1d773b48813f`. Inspected actual job log: all 13 source-free tests passed, including full GFX124 ZIP integration and forged-yet-self-consistent readback counter/hash rejection. No private source assets built/published. This verifies the new audit software, **not** an Adreno Deferred render or original Unity gameplay/G-buffer semantics. `phase_closed=false`.


## 11 Nov 2026 — GFX138 original Windows Forward versus Deferred mask gate

Session `20261111-GFX-chat-original-pass-mask-96`, `origin=chat`, writing only to `experiment/android-graphics-rootcause`. Base `239808dbc7390c323f6aa0aac9884b258d0f1ea7`.

GFX136's actual original Windows D3D11 WARP Deferred result recorded 2,008 coverage pixels, and its RT0 mask SHA256 `539a7b7685e303394c783b9a9b88deeda9bc775cd3df041263f51e6a4f1b7f91` exactly equals the prior source-pinned original GFX121 Forward mask SHA256. A matching count alone could hide displaced pixels, so GFX138 adds an independent source-free fail-closed exact per-pixel alpha comparison across four original Windows Forward controls and three Deferred RT0 controls, checks prior safe Forward SHA and Mesa coverage count, rejects bad-length/nonbinary images and shifted coverage with unchanged pixel count. The pinned GFX136 Windows workflow now reruns original DXBC Forward and Deferred using the same stage/source texture preparation in one private job, runs GFX138 unit tests and uploads only aggregate safe JSON. Original assets/readbacks are purged with the existing `if: always()` cleanup. **CI new workflow result is pending**; no phone test or signed owner APK produced. Actual Unity shader/pass selection and native G-buffer formats, original game scene parity, inter-driver RGB differences, original animation playback and final Android acceptance remain open. `phase_closed=false`.

