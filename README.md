# Raft — مرصد التقدم / up

[اللوحة](dashboard/index.html) · [البيانات](dashboard/data.json) · [لقطة 17:18Z](snapshots/2026-11-03T171814Z.json) · [تعليمات up](prompt/UP_AR.md) · [استعادة العميل](prompt/RESTORE_UP_AR.md)

**المصدر المقروء:** `feature/android-native-port` عند `571dbbcd9e6aa43ab4cc727b127d76523b0f0d53`، في 2026-11-03T17:18:14Z. **NOT_READY**، ولا candidate جاهز أو مراجعات 3/3. هذا تحديث على `update` فقط، وليس بناء لعبة.

## تقدم جديد مدعوم بدليل

- **A1 FFT:** [CI41660159285](https://github.com/alwansan/raf/actions/runs/41660159285) وظيفتان SUCCESS؛ الأصل20 × ثلاث حالات = **60/60** تطابقاً عددياً وكتابة على CPU Mesa Vulkan بنمط RGBA32F. لا يثبت half formats أو ماء Adreno/Unity.
- **W1 Depth Copy:** [CI41675980141](https://github.com/alwansan/raf/actions/runs/41675980141) SUCCESS، **27/27** صورة color/depth و**36/36** negative controls. [CI41663393724](https://github.com/alwansan/raf/actions/runs/41663393724) يثبت Unity Android Vulkan compilation لشيدر **منفصل**، لا full APK ولا تكامل shader الأصلي مع GUID.
- **W2:** [CI41676717657](https://github.com/alwansan/raf/actions/runs/41676717657) SUCCESS لتفصيل خصائص **514 مادة ضمن ownerين**؛ تقارير المصدر تصف Linear الأصلي وانقسام sRGB/linear. ليس إصلاح الألوان على الهاتف.
- **W3:** [جرد 82 owner و1,556 Material→Shader references](https://github.com/alwansan/raf/blob/571dbbcd9e6aa43ab4cc727b127d76523b0f0d53/docs/W3_FULL_MATERIAL_SHADER_INVENTORY_2026-11-03.md): 437 محلياً و1,103 cross-owner و16 engine transports مصنفة. هذه بيانات أصلية اختُبرت محلياً، دون ادعاء CI للبيانات الفعلية.
- **حالة اللعبة:** WATER-001 وRENDER-002 وFFT-FORMAT-009 مفتوحة. [native41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) فشل في استعادة builtin shader قبل Unity، ولم ينتج APK جديد. [APK80 القديم](https://github.com/alwansan/raf/releases/tag/android-early-test-41448086401-1) منفصل عن [LogRaft-76](https://github.com/alwansan/raf/releases/tag/lograf-76) الذي يخص logger.
- **CL:** أربع جلسات 2 نوفمبر فقط؛ لا دليل هاتف أحدث بعد الإصلاحات. لا تحول SurfaceFlinger FPS إلى Unity FPS.

## المقامات والقيود

اللوحة تحتوي 7 مسارات عمل، 7 **مقاييس جرد محدد**: 17/17 CanvasScaler؛ 20/20 FFT bindings؛ 0/20 typed-image declarations؛ 60/60 FFT CPU Vulkan؛ 27/27 Depth raster cases؛ 1,556/1,556 reference classification؛ 0/3 readiness reviews. **ليست نسبة اكتمال اللعبة**، ولا يتم جمعها أو حساب متوسط منها. إجمالي اكتمال السورس واللعبة وقبول الهاتف **unknown=null**.

**52** سجلاً للعملاء قُرئت من المصدر المقيد بـSHA. طابع W2 `active/18:50Z` وW3 `paused/18:25Z` يتجاوزان وقت القراءة 17:18Z؛ لا تدّع جلسة نشطة بناءً على حالة محفوظة أو توقيت متعارض.

## التشغيل

افتح `dashboard/index.html` بعد تنزيله للعرض المستقل على الهاتف. لتحديث JSON والتحقق من الحدود والتضمين:

```bash
python scripts/update_dashboard.py
python -m json.tool dashboard/data.json >/dev/null
```

اللقطات السابقة محفوظة دون استبدال. لا يُنشئ هذا العميل مهام مجدولة ولا يكتب في فرع اللعبة، ولا يبدأ Unity/APK أو يعدّل workflows.

---

## README السابق

# raf
