# GFX-LAB — GFX158 ربط مكونات الماء بالمشاهد

`session_id=20261112-GFX-chat-water-scene-links-118` · `origin=chat`

GFX158 [نجح على ZIP2 الأصلي](https://github.com/alwansan/raf/actions/runs/43146220517): 40 ملف level، 64772 MonoBehaviour؛ 64771 مرجعاً حُلّ إلى MonoScript في مالكه ومؤشر واحد فارغ. 134 مكوّناً مرشحاً للماء عبر 13 مشهداً. المطابقة اللفظية بعد حل المراجع رصدت 80 مكوّناً للشاطئ/الماء المحلي عبر 4 مشاهد، و6 للتأثيرات تحت الماء عبر مشهد واحد، و2 للطفو/الاستعلام عبر مشهدين. نتائج الصفر خاصة بالأسماء داخل ملفات level. افحص prefabs والإنشاء وقت التشغيل وتداخل الفئات قبل تعميمها. [الدليل](../../gfxlab/evidence/20261112_gfx158_water_scene_links_safe.json).

T1 سبق أن أثبت تسجيل 20/20 ملفاً مشتقاً في Unity Editor في [42014120625](https://github.com/alwansan/raf/actions/runs/42014120625). مسار native عند f59d7096 يضيف trace لأول 16 Dispatch ويقرن الاستدعاء بنتيجته ويطبع instance ID محلياً. يلزم ربط ذلك بمعرف أصل Unity المستورد والـbackend وتسجيل kernels في Android Player. لا تستنتج النجاح من عودة Dispatch؛ قارن الخرج بعد ثبوت التسجيل.
