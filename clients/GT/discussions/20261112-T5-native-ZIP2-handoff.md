# GT → T5 وT3: تغيير مسار مصدر الرسوميات في إنتاج Raft

- **owner:** GT
- **date:** 2026-11-12
- **origin:** chat
- **write scope:** `feature/android-native-port` فقط
- **shared workflow modified:** `.github/workflows/raft-unity-editor-android-import.yml`
- **source:** read-only ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- **T-team native build gates:** لم تُغيّر `TRIAL_BUILD_READINESS.md` أو بوابات `[raft-native-build]`، ولم يُطلق GT بناء XAPK
- **T5's StreamingAssets verifier:** `scripts.stage_original_streaming_assets` بقي بلا تعديل؛ مدخل `--verified-external-master-bank` الموجود مستعمل من ZIP2

## ما أُضيف فعلياً إلى الإنتاج

في [GT native integration commit](https://github.com/alwansan/raf/commit/c9bcfce4d2cb214c2a155146c8538a4e734f874c) استُبدلت خطوة `hydrate_render_payloads --apply` المعتمدة على LFS fallback بخطوة `scripts.gt_zip2_export_resources --profile full` بعد PIN + SHA256 check. تحصل أداة AssetRipper الآن على **134 أصلاً رسوميّاً** (7,532,909,297 byte) من ZIP2 دون LFS، بعد SHA256+size check مرتين في `$RUNNER_TEMP/input/Raft_Data`. تدقيق Texture وMesh وCompute/W1 depth wrapper انتقل إلى هذا المدخل نفسه. استرجاع Mesh ranges يستخدم مصدر `.resS` كاملًا ومحليًا ومُعتمدًا بدل تنزيل LFS. الرقم 134 يخص input graphics، لا Managed/StreamingAssets العامة.

في [GT audio bank bridge commit](https://github.com/alwansan/raf/commit/a058d37635611591d61f49c97fc80cec2274cdb8) أصبح مورد `MasterBank.bank` يُجمع من ZIP2 مباشرةً مع SHA256 ثم يُمرر إلى أداة T5 الأصلية؛ [43125353255 PASS](https://github.com/alwansan/raf/actions/runs/43125353255)، 101,600,960 byte. لا تعديلات FMOD runtime أو إحداثيات الملفات.

**إثبات الإنتاج الأولي:** [GT 43124662931 PASS](https://github.com/alwansan/raf/actions/runs/43124662931) تحقق من اكتمال كل 134 SHA256 أصلاً وفحص جميع Texture source streams، و[GT native guard 43125034578 PASS](https://github.com/alwansan/raf/actions/runs/43125034578) و[GT real full AssetRipper 43125542125 PASS](https://github.com/alwansan/raf/actions/runs/43125542125) أثبتا 40 مشهداً + 1,536 .mat + 4,003 texture images + 8,372 .asset + 18,368 .meta، مع 151 Managed providers و0 Mono layout mismatches.

## ما بقي وأولوية التنسيق

- `scripts.verify_exported_material_texture_links` على full ExportedProject أعاد exit 2 في GT smoke رغم نجاح AssetRipper. GT يستعيد كود الخطأ الآمن من [43126735391](https://github.com/alwansan/raf/actions/runs/43126735391) ثم يعالج source→export Texture GUID. **لا تنسب نجاح source export إلى سلامة shader أو material كامل.**
- أضيف Opt-in فقط `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE=1` إلى `android-port/Experiments/ExportLineage/RaftExportLineage.cs` ليشمل texture object mappings في GT isolate؛ الإنتاج الذي لا يفعّل البيئة يحتفظ بمواد/شيدرات السجل السابق. Private trace لا يرفع إلى artifacts.
- طلب المالك استعادة الرسوميات بالكامل، لكن الإنتاج الأصلي Unity/Android full XAPK يتطلب T5 policy و5/5 trial votes عند اللزوم. لا تطلق native workflow بسبب هذا التسليم وحده؛ ضع إصلاحات GT في مرشح البناء حين تكتمل بوابات المصدر.
- **مطابقة كاملة لمظهر الماء/FFT/Foam/shader variants/kernels/Adreno GPU لم تثبت**. T1–T3 يظلون أصحاب أدلة هذه المكونات؛ GT يأخذ Source→Export material, texture and mesh lineage.

## تصحيح روابط Material/Texture + إشارة T3 المهمة (تحديث GT)

- [43126735391](https://github.com/alwansan/raf/actions/runs/43126735391) أعاد AssetRipper الحقيقي إلى 40 scene كما سابقاً، وفشل B46 قبل التحقق من PPtrs بسبب **`empty_or_unrecognized_texenv`** فقط (اختلاف تمثيل `m_TexEnvs` بين list وmapping في YAML). عُدّل `scripts/verify_exported_material_texture_links.py` ليدعم الشكلين و`{}` الفارغة مع حماية duplicate/missing/bad PPtr؛ [43128041580 — PASS](https://github.com/alwansan/raf/actions/runs/43128041580) للاختبارات الاصطناعية، ويجب فحص actual export بعد التعديل قبل القول أن B46 pass.
- [43127697656 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43127697656) استخدم `RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE=1` في GT فقط ونجح B05 `sharedassets6.assets` بمطابقة أصل→Export `m_TexEnvs`/UV الدقيقة (`exit_code=0`). تقرير أمان فقط. أداة `scripts/gt_full_original_export_texenvs.py` توسع المقارنة إلى **82 original owners / 1556 Materials**؛ اختبارها الاصطناعي [43128570586 PASS](https://github.com/alwansan/raf/actions/runs/43128570586)، والعمل الحقيقي يُختبر في [43128711194](https://github.com/alwansan/raf/actions/runs/43128711194).
- **إلى T3/W1:** فحص `scripts.t3_audit_exported_material_programs` على **AssetRipper الخام قبل شيدرات الاستعادة** في [43127697656](https://github.com/alwansan/raf/actions/runs/43127697656) كشف **786 Material documents تستخدم local custom dummy shaders** (من أصل 1536، و750 builtin)، **140 shader files كلها فيها `//DummyShaderTextExporter`** و64 Shader targets فريدة مستخدمة ضمن 786. هذه مرحلة RAW فقط ولا تقيس نتائج Restorers أو Vulkan/Adreno؛ يجب إبقاء/تقوية اختبارات post-restorer قبل بناء الهاتف وعدم اعتبار أصل Shader موجوداً هو نجاح Pixel.
