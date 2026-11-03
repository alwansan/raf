# Raft — مرصد التقدم / العميل up

[افتح اللوحة المستقلة](dashboard/index.html) · [JSON البيانات](dashboard/data.json) · [لقطة 2026-11-03T12:49:52Z](snapshots/2026-11-03T124952Z.json) · [تعليمات التشغيل](prompt/UP_AR.md) · [استعادة العميل](prompt/RESTORE_UP_AR.md)

**NOT_READY عند قراءة 2026-11-03T12:49:52Z.** فرع المصدر: `feature/android-native-port`، SHA `c6868a38c41e8384dd8153289c913e87714c8a05`. فرع التقارير الوحيد القابل للكتابة `update`.

اللوحة تبيّن **سبعة مسارات**: المصدر والموارد؛ الماء والشيدرات وFFT؛ الصوت والاهتزاز؛ العالم والحفظ؛ الإدخال والعرض والأداء؛ البناء والتغليف؛ وقبول الهاتف. لكل مسار: الأدلة المحققة وغير المحققة، العوائق، العمل المسجل والقرار التالي. على الهاتف تظهر بطاقات ورسوم نطاقية وقائمة عملاء قابلة للبحث وأقسام قابلة للتوسيع وتاريخ لقطات محفوظ.

## ما ثبت من قراءة المصادر والوظائف

- فحص A13 [41637048446](https://github.com/alwansan/raf/actions/runs/41637048446)، وفحص A11 [41637552496](https://github.com/alwansan/raf/actions/runs/41637552496)، ومرجع FFT ثنائي الأبعاد [41637650224](https://github.com/alwansan/raf/actions/runs/41637650224): **completed/success** في وظائف Actions عند القراءة. نطاقها CPU؛ ليست اختبار ماء GPU أو لعبة.
- محاولة البناء [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) فشلت في `reconstruct`، خطوة استعادة built-in shaders قبل Unity؛ و`delivery-result` failed و`publish` skipped. ليست APK أحدث.
- [APK80](https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1) على مصدر `9462f8edd8cdb5becbccb96521f2876ef9924410` يحتوي 11 assets في Release API، بينما [lograf-71](https://github.com/alwansan/raf/releases/tag/lograf-71) إصدار لتطبيق السجلات **وليس اللعبة**.
- [CL 205608](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261102-205608-054/session-summary.json) شاهد هاتف قديم: 71,670 shader pass و5,941 kernel و35 haptics errors. الـFPS خارجي SurfaceFlinger وليس Unity FPS، ولم يثبت SHA اللعبة المثبتة من هذا الملف.
- مجلد `prompt/coordination/clients/` أعاد **38 هوية**. **أُعيد فحص أربع حالات حديثة مباشرة** (A11/A13/A14/A15)، وسائر صفوف العملاء من لقطة المصدر السابقة؛ `active` داخل ملف سجل ليس دليلاً على جلسة تعمل.

## نسب الجرد لا اكتمال اللعبة

`17/17` فك سجلات CanvasScaler؛ `20/20` تطابق عقود ربط FFT؛ `0/20` تطابق بيانات typed-image بعد roundtrip؛ `0/3` مراجعات كاملة لمرشح جاهزية ثابت (لم يُحدَّد مرشح). هذه قوائم مختلفة ولكل منها مقام ووزن وحدود مع الدليل داخل اللوحة. **اكتمال اللعبة واستعادة السورس وقبول الهاتف = null / غير مقاس**، ولا يوجد متوسط عام.

## تشغيل التحديث والتحقق

`dashboard/data.json` هو المصدر الوحيد للعرض؛ `dashboard/index.html` مستقل ويتضمن لقطة JSON. بعد تغيير البيانات شغّل `python scripts/update_dashboard.py` لإعادة التضمين وفحص المقامات والروابط المحلية وبنية الأقسام. اللقطات في [snapshots](snapshots/) غير قابلة للاستبدال وتوثق تاريخ المقارنات.

العميل up لا يبني Unity ولا يشغّل أو يغيّر workflows ولا يكتب إلى فرع اللعبة أو CL. هذه **جلسة تشغيل واحدة** وليست مهمة مجدولة. اتبع AGENTS.md وprompt/UP_AR.md وclients/up/state.json وMEMORY.md، وافحص source HEAD وActions واللوغات والعملاء من جديد قبل كل تحديث، واستخدم lease بلا force.

---

## README السابق

# raf
