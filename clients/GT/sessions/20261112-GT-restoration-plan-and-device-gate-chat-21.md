# GT — Chat-21: خطة الاستعادة المرحلية ومنع الادعاء الكاذب بنجاح رسوميات الهاتف

- التاريخ: 2026-11-12؛ الدور GT؛ فرع الكتابة الوحيد `feature/android-native-port`.
- المصدر المقروء فقط: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`، `lfs:false`، لا تغيير للأصول الأصلية أو Unity GUIDs/.meta.
- مدخل الاستكمال السابق: [Chat-20](20261112-GT-CL-device-graphics-failure-chat-20.md).
- طلب المالك: تسجيل المستعاد والمتبقي والخطة، تحديث الاستعادة باستمرار، والاستمرار في التنفيذ.

## النتائج المنفذة

1. راجعت أحدث HEAD وActions: البناء [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) بُني من `5b3ddd67`، وما زال في مرحلة `Unity Editor 2021.3.45f2 Android import and compile` عند الفحص، دون خطوة فاشلة. **لم أعِد تشغيل بناء كامل مكرر**. الحزمة الكاملة السابقة من [43246196803](https://github.com/alwansan/raf/actions/runs/43246196803) مصدّقة المصدر والتوقيع ولكن لا تثبت رسوميات الهاتف.
2. وجدت ثغرة في `scripts/gt_device_graphics_acceptance.py`: غياب إحدى فئات الأخطاء كان يُحسب صفر خطأ، مما قد يعطي false green عند LogRaft ناقص. أصلحتها لتطلب ظهور جميع الفئات الخمس؛ أضفت اختباراً سلبياً لكل فئة في `tests/test_gt_device_graphics_acceptance.py`.
3. نجح [CI 43266159804](https://github.com/alwansan/raf/actions/runs/43266159804) في الاختبارات وفحص جلسة CL الأصلية. السجل الأصلي يبقى **KNOWN_DEVICE_LOG_GATE_REJECTED**: 42,229 UltimateWater invalid pass، 7,263 compute kernel6، 4,668 Cursor RGBA32، 2 OBB GUID.
4. أنشأت مصدر الحقيقة للمتابعة: [RESTORATION_PLAN.json](../RESTORATION_PLAN.json) بتفاصيل 12 workstreams P00–P11، ستة milestones M0–M5، source/export/Unity/package/device proof مفصولة، المهام والعوائق والـRun IDs، و[RESTORATION_PLAN_AR.md](../RESTORATION_PLAN_AR.md) لتوضيح المستعاد والمتبقي للمالك.
5. أضفت `scripts/gt_restoration_plan_check.py` + `tests/test_gt_restoration_plan_check.py` لحراسة الأرقام من `state.json` ودليل CL الحقيقي، ومنع ترقية الحالة إلى device_verified أو اكتمال milestone دون دليل. أضفت [workflow](../../.github/workflows/raft-gt-restoration-plan-gate.yml) سريعاً دون Unity أو تنزيل LFS.
6. يحدث هذا الاستكمال أيضاً [RESTORE_AR.md](../RESTORE_AR.md)، [SUMMARY_AR.md](../SUMMARY_AR.md)، [MEMORY.md](../MEMORY.md)، و[state.json](../state.json)؛ المرجع الأحدث هو خطة الاستعادة وأدلة الاختبارات، لا الفقرات التاريخية الطويلة.

## الحالة الدقيقة التي لا تُنسى

- المصدر: 82/82 serialized owners، 134 graphic files (7,532,909,297 B)، 40 scenes؛ 4,708 Mesh و4,050 Texture2D و1,556 Material و165 Shader و9 ComputeShader.
- Export/source: 9 original Texture2DArray grids، 28 refs، 416 cross-owner Texture PPtrs، 50/50 BC3 top mip source-pixel matches. لا تعمم إلى GPU وmip-chain الكامل.
- Vendor restoration: 16 مستند Material custom أصبح غير Dummy، لكن **770 مستند Material custom ما زال Dummy**. 198 Unity builtin Shader source programs ضمن الترخيص/الأرشيف الرسمي لا تعني استعادة 165 shader لعبة.
- التجريب: Particle108 أصلي 4×(VS,FS)/8 translated stages، private Android Vulkan ShaderLab compiled بسامبلر تقريبية؛ لا original Material/GUID/sample parity.
- الهاتف في CL: اللون الأبيض في الطوف، أخطاء الماء وkernel6 والـCursor. الهوية الحقيقية لرقم kernel6 غير مثبتة، ولا يوجد إثبات Adreno full-game pixels.
- خطر رئيسي: خلط نجاح CI أو ZIP2 extraction أو old XAPK مع استعادة الرسوميات. أي ادعاء device pass يحتاج جلسة هاتف جديدة وفحص الصور والـLogRaft.

## العمل التالي في جلسة GT جديدة

1. اقرأ `RESTORATION_PLAN_AR.md` و`RESTORATION_PLAN.json` أولاً بعد `RESTORE_AR.md`، ثم `state.json` وآخر session.
2. شغّل validator سريعاً واستخرج أحدث Git HEAD وحالة full native [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671). إذا فشل، اقرأ السجل وأصلح أول سبب ثم أعد البناء بناءً على commit حديث. لا تكرر وهو قيد العمل.
3. اختر دفعة أصلية قابلة للاختبار: Spectrum pass المطلوبة، ثم Foam Global 2pass original ShaderLab/GUID وربط نفس Export/Unity. اكشف سبب `Invalid pass` ولا تستبدله بPass اصطناعي.
4. افصل kernel6 عن Spectrum/Foam، وأثبت مصدره قبل FFT patch. استخدم اختبارات Unity/Vulkan المقيّدة وشهادة المصدر، ثم اختبر على Adreno.
5. انقل دليل الدفعة وcommit/CI/ما لا يزال غير مثبت إلى الخطة JSON/العربية وإلى الذاكرة ورسالة الاستعادة في **نفس دورة الكتابة**.

## تشغيل الفحوص

```bash
python3 -m unittest discover -s tests -p 'test_gt_device_graphics_acceptance.py' -v
python3 -m unittest discover -s tests -p 'test_gt_restoration_plan_check.py' -v
python3 -m scripts.gt_restoration_plan_check
# After a fresh phone session:
python3 -m scripts.gt_device_graphics_acceptance --session-summary session-summary.json --strict
```

**تنبيه مهم:** Chat-21 وثّق التغطية وسدّ ثغرة الفحص، **ولم يصلح برنامج ماء/مادة Dummy داخل اللعبة بعد**. تعود الأولوية إلى Shader Material runtime وwater-pass authentic reconstruction فور توفر دليل الاستيراد المعتمد.

## ملحق: تدقيق Spectrum/Unity Editor — بعد بوابة الخطة (نفس الجلسة)

- تأكدت من أصل [B09 original Spectrum topology](../../scripts/b09_spectrum_topology_contract.py): Shader من `sharedassets0.assets`، SHA-authenticated، **7 Passes** و**28 برنامج stage (7×2 VS/FS×2 variants)**، وبوابة المصدر القديمة [41920232173 SUCCESS](https://github.com/alwansan/raf/actions/runs/41920232173). هذه أصالة المصدر، **لا** ShaderLab/Unity Runtime. أصل [B24 Foam Global](../../scripts/b24_original_foam_stage_translation.py) يثبت Passين و4 VS/FS stage programs.
- لذلك أصلحت خطة GT: لا تعتبر شرط `Spectrum >= 6` من invalid-pass-index جهاز قديم بديلاً عن **7 Passes أصلية**. [بوابة خطة GT 43268872421 SUCCESS](https://github.com/alwansan/raf/actions/runs/43268872421) تختبر الفرق وتمنع تبديل 7 إلى 6 أو 28 إلى 24 دون دليل.
- أضفت `android-port/Editor/GTOriginalWaterPassImportProbe.cs`، استدعاء قراءة فقط في `AndroidNativeBuild.ValidateSdkBindings()`. خلال Unity build لاحق سيكتب `GT_WATER_IMPORTED_PASS_DIAGNOSTIC` للـSpectrum وFoam: `exactNamedExportedShaders`، `editorPassesMin/Max`، `importerDummyMarkerCount`، `logRequiredMinimum`، `originalSourcePasses`، `sourceStructureCandidateOnly`. لا يطبع GUID أو كود shader، ولا يعدّل Materials/.meta/Assets؛ لا يقول إن Adreno pixels verified.
- أصلحت probe ليحسب absolute path من `Application.dataPath` بدل directory العمل واحترم حدود `Assets/` ومنع path traversal.
- أضفت synthetic CSharp harness تحت `tests/fixtures/gt_water_probe` وخمسة source tests وworkflow `raft-gt-original-water-pass-import-probe.yml`؛ [CI 43269999662 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43269999662) **جمع ونفّذ C# actual probe مقابل stubs**، كشف one-pass Dummy Spectrum، وتعرف على 2pass Foam ورفض مسار خارجي. هذه اختبارات مصدرية فقط ولا تعني أن Unity Editor الفعلي اجتاز الاختبار.
- أحدث native [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) ما زال snapshot أقدم ويعمل في Unity، فلا يتضمن هذه التجربة ولن نظهر نتائجها حتى يجري بناء حديث آخر.
- تحديثات `RESTORATION_PLAN.json` و`RESTORATION_PLAN_AR.md` تؤكد أن `P06.unity_verified=false` و`P06.device_verified=false`. الخطوة التالية: انتظار نتيجة Unity import/compiled Shader من build لاحق، وتشغيل الدفعات الأصلية Spectrum/Foam/GUID والمقارنة الحقيقية.
