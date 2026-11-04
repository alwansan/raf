# Raft — مرصد الأدلة والتقدم (العميل up)

[اللوحة العربية المستقلة](dashboard/index.html) · [البيانات](dashboard/data.json) · [لقطة 4 نوفمبر](snapshots/2026-11-04T130329Z.json) · [تعليمات up](prompt/UP_AR.md) · [الاستعادة](prompt/RESTORE_UP_AR.md)

## الحالة عند لقطة 2026-11-04T13:03:29Z

**`NOT_READY`** حسب السجل المقروء من `feature/android-native-port` عند SHA `cb9ec39f28db9015c32fe089f83ddf21e04107fe`. ليس هناك مقياس كلي موثوق لاكتمال اللعبة أو استعادة المصدر، والمجهول `null` وليس `0%`. المصدر الجديد المفضل للبيانات الأصلية `zip2` مثبت عند `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

**تجربة W4:** [run41812889049](https://github.com/alwansan/raf/actions/runs/41812889049) وصلت بالفعل إلى خطوة **Unity Editor 2021.3.45f2 Android import and compile** وكانت **in_progress** عند الفحص، بعد نجاح طلب التشغيل والترخيص وتجهيز المشروع. هذه **محاولة تجريبية مصرّح بها مع قيود ماء موثقة** في [build request](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/.github/raft-native-build-request.json)، وليست إعلان جاهزية أو نجاح APK. الاختبار السابق [41808015938](https://github.com/alwansan/raf/actions/runs/41808015938) تجاوز بوابة ملكية built-in (750 refs/11 pointers) ثم أخفق في strict water gate. الإقرار الحالي يحتفظ بالفجوات ولا يحوّل `authentic_water_kernel_identity_verified` إلى true، والمراجعات المستقلة للمرشح ما زالت **0/3**.

## ما تحقق في مصدر اللعبة فعلياً

- [ZIP2 provider](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/docs/ZIP2_SOURCE_PROVIDER.md): قائمة **366 ملفاً أصلياً** مجموع أحجامها **7,789,295,609 بايت**، بينها **22 ملفاً مجزأً**. فحص بنية/أحجام الأجزاء وليس SHA256 لجميع المحتويات أو إثبات كامل Android.
- [W2 original resource census](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/docs/W2_RESOURCE_CENSUS_2026-11-04.md): **82 ملف موارد، 66 صنفاً، 1,209,137 كائناً تسلسلياً** في الأصل، تشمل 4,708 Mesh و4,050 Texture2D و1,556 Material و165 Shader و9 ComputeShader. CI [41831551847](https://github.com/alwansan/raf/actions/runs/41831551847) ناجح. **هذا جرد أصل PC، وليس نسبة الاستعادة في Android.**
- [W2 compute inventory](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/docs/W2_COMPUTE_KERNEL_INVENTORY_2026-11-04.md): **42 kernel row عبر 9 ComputeShader providers** (20 FFT،12 Blur،10 أخرى)، تحقق CPU [41830374791](https://github.com/alwansan/raf/actions/runs/41830374791). لا يثبت أن برامج GPU استُعيدت أو تعمل على Adreno.
- [Spectrum/Foam topology](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/docs/W2_WATER_SHADER_STAGE_BINDINGS_2026-11-04.md): 7 passes لـSpectrum و2 لـFoam مع CB partial؛ CI [41828808987](https://github.com/alwansan/raf/actions/runs/41828808987) ناجح، لكن shader/water source الكامل لا يزال مفتوحاً.
- [A9 أصل FMOD عبر ZIP2](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/docs/A9_ZIP2_MASTERBANK_NO_LFS_2026-11-04.md): MasterBank الأصلي 101,600,960 بايت و36 StreamingAssets بإجمالي 156,555,363 بايت تحققت في CI [41733666911](https://github.com/alwansan/raf/actions/runs/41733666911)، لكن سماع الصوت على الهاتف وOBB النهائي غير مثبتين.
- [A8 حفظ الأصل عبر ZIP2](https://github.com/alwansan/raf/blob/cb9ec39f28db9015c32fe089f83ddf21e04107fe/docs/A8_ZIP2_ORIGINAL_SAVE_NO_LFS_2026-11-04.md): CI [41733872815](https://github.com/alwansan/raf/actions/runs/41733872815) نجح للمصدر/مسارات SaveAndLoad، وليس إنشاء عالم أو حفظ لاعب حقيقي.
- A1 وW1 يحتفظان بنتائج CPU Vulkan محددة (60/60 FFT عددياً و27/27 Depth Copy لون/عمق) لا تعني اكتمال رسوم الهاتف.

## العملاء، الإصدارات واللوغات

**74 مجلد عميل** في المصدر المثبّت: **28 ملف state أُعيدت قراءته مباشرة**، و**46 صفاً تاريخياً** من اللقطة السابقة، مع تمييز ذلك لكل صف. كلمة `active` أو heartbeat قديم لا تثبت جلسة حية. W2 وW3 لهما طوابع تحديث لاحقة لوقت هذه القراءة، فحُفظت كتعـارض زمني لا نشاط مثبت.

**آخر إصدار لعبة مؤكد:** [APK80](https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1) عند SHA `9462f8edd8cdb5becbccb96521f2876ef9924410` (11 assets). **أحدث إصدار لسجل LogRaft:** [lograf-80](https://github.com/alwansan/raf/releases/tag/lograf-80)، منفصل عن اللعبة. ملف [CL القديم](https://github.com/alwansan/CL/tree/main/raft%20log/lf) يحوي أربع جلسات 2 نوفمبر؛ لا قبول هاتف جديد للإصلاحات.

## عرض اللوحة والتحقق

الصفحة HTML مستقلة ومناسبة للهاتف، تضم مسارات source/water/audio/world/input/build/phone قابلة للتوسيع، وقيود كل دليل وSHA، بطاقات أحدث نتائج وتجربة W4، رسوماً لتعداد الأصل وجداول Actions والعملاء وتاريخ snapshots. لتشغيلها نزّل `dashboard/index.html` وافتحه في متصفح بدلاً من معاينته كمصدر داخل GitHub.

```bash
python scripts/update_dashboard.py
python -m json.tool dashboard/data.json >/dev/null
```

فحوص Python المتاحة في هذه الجلسة نُفّذت على **fixture محلي** بنفس سكربت التحقق. البيانات المرحلية الحقيقية فُحصت بمنطق مستقل قبل commit للتطابق والمقامات والروابط واللقطات؛ لم يُنفذ Python على checkout كامل للمستودع لأن الوصول المباشر للشبكة من الحاوية غير متاح. اللقطات السابقة محفوظة دون استبدال.

هذا **عميل تحليل**، لا يغيّر فرع اللعبة أو ZIP2 أو CL أو مهام العملاء أو workflows أو طلبات البناء، ولا يعمل في الخلفية.

---

## README التاريخي

# raf
