# Raft — مرصد أدلة المشروع / العميل up

[اللوحة العربية](dashboard/index.html) · [JSON](dashboard/data.json) · [لقطة 2026-11-04T23:42:00Z](snapshots/2026-11-04T234200Z.json) · [UP instructions](prompt/UP_AR.md) · [استعادة up](prompt/RESTORE_UP_AR.md)

## النتيجة عند قراءة المصدر

**المشروع `NOT_READY`، و0/3 مراجعات كاملة للمرشح الثابت.** المصدر المقروء من `feature/android-native-port` SHA `58047d3b293f04547e36536518fd936ad328f4d1`، وفرع `zip2` المثبت `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. لا نسبة كلية موثوقة للعبة أو استعادة المصدر أو قبول الهاتف؛ قيمها **`null`**.

### أول نجاح بناء تجريبي حديث: APK86
[W4 run41812889049](https://github.com/alwansan/raf/actions/runs/41812889049) **completed/success** في خمس وظائف: request/license/reconstruct/publish/delivery result. [Game Release APK86](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1) بتاريخ 4 نوفمبر 13:59 UTC، source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`، يحتوي12 assets:
- APK: **672,894,330 B**، SHA256 `b6e6ca15f039b4640381bc7cf10b4dd1774fea36d4bdf3183696d82374587077`.
- OBB: **2,301,202,061 B**، SHA256 `72db0510ef8dde20a4a8efef946c2bd7d8a7cf9be96d633aa9b7c158ac9c23a5`.
- XAPK: **2,974,097,643 B**، SHA256 `89090c451b0f0c0f81bd8f6d74f671481ac6b8bcf9cc07ee7e36d168234e10a9`.
- تشمل SHA256SUMS و`RECORDED_LIMITATIONS.json` وأجزاء النقل. لا تجمع XAPK وأجزاءه كنُسخ لعبة إضافية. [APK80](https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1) تاريخي منفصل؛ [lograf-88](https://github.com/alwansan/raf/releases/tag/lograf-88) يخص تطبيق تسجيل اللوغات لا اللعبة.

**نجاح التسليم ليس قبول اللعب.** حزمة APK86 تحمل خمس فجوات ماء وشيدرات معلنة. مصدر اللعبة الحالي أحدث بكثير من source SHA للبناء. لم يُقرأ SHA256 للـAPK المثبت على الهاتف، وإن كان B_TEAM راجع versionCode86.

### نتائج الهاتف — 4 نوفمبر
ظهرت **6 جلسات CL جديدة** (أصبح المجموع10). قرأت5 ملفات `session-summary.json` حديثة؛ جلسة 17:38:23 لها مجلد لكن بلا summary. [أحدث جلسة 22:57:57](https://github.com/alwansan/CL/blob/main/raft%20log/lf/LogRaft-20261104-225757-156/session-summary.json) تسجل في final: **40,327** `ultimate_water_invalid_pass`؛ منها Spectrum12,557/Foam22,216/Blur5,554؛ و**5,555** `water_fft_invalid_compute_kernel` index6. ظهر `World has been loaded` مرة، وFMOD startup، وتحذيرات cursor، OBB GUID مرتين، MonoScript/EventSystem وSteam API.

[فريق B حلل Logcat الأصلي](https://github.com/alwansan/raf/blob/58047d3b293f04547e36536518fd936ad328f4d1/prompt/coordination/B_TEAM/REVIEW_2026-11-04.md): بعد رسالة تحميل العالم وقع `DllNotFoundException steam_api64` في `SteamUserStats.StoreStats → SaveAndLoad.SaveGame → GameManager.OnWorldRecieved`. هذا **عائق حقيقي للحفظ/الدخول** وليس إثباتاً أنه السبب الوحيد لشاشة Connecting. لا يجوز تزوير نجاح world flag. تظهر صور المالك مجسمات شاحبة وبيضاء. `SurfaceFlinger FPS` ليست Unity FPS، وبعض `PSS` يشمل GPU allocations لا يقارن مباشرة بـVmRSS. لا تجمع counts الخاصة بـlast_sample مع final ولا تجمع جلسات مختلفة على أنها معدل واحد.

**ملاحظة المالك الأحدث:** الصوت وSettings يعملان ضمن التجربة المكتملة، مع حماية عدم التراجع. التاتش والأزرار وlayout **مؤجلة**. الأولويات P0: WATER-001/RENDER-002/LOCAL-005، ثم اكتمال موارد/دمج المصدر. آخر Game APK من قبل تحسينات B الجديدة، ولا يصح وصف اختبارات B على أنها موجودة في APK86.

### عملاء فريق B والدليل
[TEAM.json](https://github.com/alwansan/raf/blob/58047d3b293f04547e36536518fd936ad328f4d1/prompt/coordination/B_TEAM/TEAM.json) يسجل **50 اسماً مؤهلاً**، عند SHA المقروء يوجد **36 مجلداً مستقلاً** قرأت جميع حالات `state.json` لها، و14 اسماً لا يوجد له مجلد. **74 عميلاً قديماً متقاعداً** وفق توجيه المالك، أبقيت حالاتهم كمرجع تاريخي. لا تعتبر `active` أو heartbeat ضمان استمرار جلسة. [B_TEAM/SUMMARY](https://github.com/alwansan/raf/blob/58047d3b293f04547e36536518fd936ad328f4d1/prompt/coordination/B_TEAM/SUMMARY.md) مصدر فهرس القضية، وليس مصدراً مستقلاً لنجاح الاختبارات.

أدلة مصدرية حديثة محددة النطاق: B03 فحص1,635/1,635 مراجع target Material لستة مشاهد أصلية؛ B21 تطابق Light value/owner لـ2/2 في export محدود؛ B20 جهّز private Foam 2-pass/4-stage packet ووجد CB size اختلافاً في7/8 مراجع يحتاج تفسيراً؛ B17 namebridge لـSpectrum. نجاح GitHub CI source أو private Vulkan/Unity دون تكامل الجهاز **لا يعني تصحيح الماء أو ألوان الصور**.

### المقاييس ومبدأ القراءة
اللوحة بها **7 مسارات** منفصلة، **11 مقياس جرد/حالات محددة**، جداول Actions، ملخص W4، رسوم تعداد الأصل وجلسات الهاتف، حالات B والقدامى، تاريخ snapshots. `3/3` لصيغ APK/OBB/XAPK يعني **تغطية تسليم الصيغ فقط**، و`0/3` مراجعات الجاهزية الحقيقية بقيت. لا تجمع المقامات إلى نسبة إنجاز وهمية.

### التحديث والتحقق

```bash
python scripts/update_dashboard.py
python -m json.tool dashboard/data.json >/dev/null
```

السكريبت يفحص SHA المصدر والمقامات، الروابط، حالات unknown، سجل اللعبة، وسجل الهاتف، وجود snapshot منفصل وتساوي JSON المضمن. في هذه الجلسة تمت اختبارات مستقلة على blob GitHub الحقيقي؛ لا أدعي تشغيل Python على checkout كامل لم يُتاح للحاوية. اللقطات القديمة محفوظة.

عميل up يكتب **فقط** في فرع `update`؛ لم يغيّر كود اللعبة أو ZIP2 أو CL أو build request أو أتمتة أو ملفات عملاء آخرين، ولا يعمل بين الرسائل.

---

## README السابق

# raf
