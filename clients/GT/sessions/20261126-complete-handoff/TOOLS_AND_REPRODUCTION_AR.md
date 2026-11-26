# الأدوات والتجهيز وإعادة التشغيل

## الأدوات داخل المستودع

| الوظيفة | المسارات |
|---|---|
| مصدر NEXT23b وتركيبه | scripts/gt_next23b_private_stage_translation.py،gt_next23b_source_topology_census.py |
| route/layout/property/CB | gt_original_921_all_variants.py،gt_original_921_keyword_routes.py،gt_original_921_shaderlab.py،gt_original_921_cb_hlsl.py،t3_particle108_source_propstate.py |
| Vulkan bundle | gt_verify_921_shader_bundle.py،gt_decode_smolv.cpp |
| مصدر وتحكم FFT Utilities | gt_fft_utilities_restore.py؛ CLI --compiler-control dxc أو hlslcc؛ defaultDXC محفوظ |
| تثبيت FFT | gt_install_fft_utilities_original.py؛ يتطلب source-receipt و unity-receipt و bundle-receipt مستقلة،original و project و trace و candidate و backup و out |
| C# المعزول | android-port/Experiments/GT/Editor/FFTUtilitiesShaderValidation.cs و Next23bShaderValidation.cs |
| مصدر ZIP2 | gt_stage_serialized_owners.py،gt_zip2_export_resources.py،w1_stage_zip2_owners.py |
| مصفوفات/لون/alpha | gt_repair_array_flipbook_importers.py،b44_verify_material_colors.py،gt_particle108_export_alpha_diagnostic.py |
| تجارب مؤلفة اصطناعياً | gt_synthetic_material_alpha.py و tools/synthetic_material_alpha/ |
| أدوات التأليف التاريخية | tools/gt_handoff/20261126/run-tests-isolated.py و port_post23_native.py؛ ليستا أوامر تطبق عميانياً |

المسارات غير المسبوقة في الجدول تحت scripts/. ملفات الاختبار المطابقة تحت tests/. workflows تحت .github/workflows/raft-gt-fft-utilities-source.yml و raft-gt-next23b-original-shader-unity.yml و raft-gt-next23b-private-stage-translation.yml و raft-gt-synthetic-material-alpha.yml. Native في raft-unity-editor-android-import.yml؛ لا تعدّل request JSON لأجل الاستعادة أو الحفظ.

## بيئة قابلة لإعادة التجهيز

Python المستعمل محلياً3.12.3،PyYAML6.0.3،Pillow13.0.0،Unity2021.3.45f2. بقية freeze التاريخي وبصمات حزم arm64 والأرشيف الرسمي UnityPy1.23.0 في toolchain/. هذه إصدارات تاريخية، لا ادعاء أن apt اليوم يعيد البايتات نفسها.

للفحوص المصدرية الاصطناعية:

```bash
python3 -m venv work/gt-handoff-venv
work/gt-handoff-venv/bin/python -m pip install -r clients/GT/sessions/20261126-complete-handoff/toolchain/source-free-requirements.txt
PYTHONPATH=tests work/gt-handoff-venv/bin/python -B -m unittest test_gt_next23b_unity_gate test_gt_next23b_private_stage_translation test_gt_original_next23b_source_pass_modes test_gt_next23b_source_property_flags test_gt_fft_utilities_restore test_gt_fft_utilities_unity_contract test_gt_fft_utilities_bundle test_gt_install_fft_utilities_original test_gt_original_921_bundle -v
```

لإعادة الفحص الواسع، شغّل كل test_*.py في subprocess مستقل كما فعل runner التاريخي، مع repo/output/python محدثة. لا تجمع discovery كله وتفترض أن خطأ الاسم المكرر دليل تغيير إنتاجي جديد. قد تحتاج اعتمادات إضافية؛ freeze محفوظ وليس وعداً باجتياز 740 اختباراً في بيئة نظيفة.

داخل Ubuntu24.04 تستعمل workflows vkd3d-compiler و spirv-tools و spirv-cross و glslang-tools؛ فحوص spirv-val تستهدف vulkan1.1. source مؤقت فقط بعد التحقق SHA. مصدر smol-v مثبت عند 6303e979b59153ee7007fd14e06d3fed8687b64c؛ راجع curl والمسارات في workflows، ولا تغيره بصمت.

محلياً استُخرجت debs arm64 إلى work/debs/root، واستُعمل PATH نحو usr/bin و LD_LIBRARY_PATH نحو usr/lib/aarch64-linux-gnu. فشل pip install UnityPy بسببغياب aarch64-linux-gnu-gcc؛ لم يكن ذلك فشل فك المصدر. الحل المستعمل: الاعتمادات في venv و PYTHONPATH إلى شجرة مصدر UnityPy1.23.0 المطابقة للأرشيف الرسمي؛ sha256396e2bf8dea49b2bfd6309f5c790b2a5838613be037094bb55e6076c4852a890. مصدر التنزيل وبصمات جميع debs في versions-and-checksums.json. لا تنسخ binaries لعمارة مختلفة ولا تتجاهل التحقق.

## إعادة توليد النواتج الخاصة

المرشحات HLSL/ShaderLab و DXBC و SPIR-V والأصول المصدرة لا تُنشر هنا. لكل مرشح وصفة مصدر في script/workflow، وإيصال آمن وبصمة مرشح حين كانت متاحة. أعد توليده في scratch منفصل من ZIP2 المصرح والمثبت 15964ea8 فقط، دون GitLFS ودونتعديلالأصل، ثم افحص SHA والحزمة الفعلية. الوصول إلى license/keys يتم بالإعدادات الموجودة خارج Git؛ لا تحفظها في الحزمة.

الـ workflows الجديدة يمكن أن تعمل على push للمسارات المحددة. commit التسليم يحمل[skip ci] ولا يعد نجاح CI. قبل إعادة تفعيلها في جلسة تنفيذ راجعإذنالمالكالحالي والأسرار والـ concurrency وحالةأي job قائم؛ لا تعيد تشغيلشل سابق لمجردتأخرالملاحظة.

## مدخل الجرد المقبول بعد انتهاء مرفقاتActions

تستهلك NEXT23b quality JSON من run43929698985. نسخته الفعلية محفوظة في evidence/actions/43929698985/14264742322/gt-twentythree-shader-postrestore-quality.json. افحص MANIFEST وartifact-provenance.json ثم هيئ نسخةscratch للمدخل إذا احتاجworkflowتعديلخطوةالتنزيل؛ لا تغير هويات المصدر أو تتعامل مع ملف من export آخر كأنه نفسالتصدير. بقية مراحل9/13–23محفوظةبمعرفاتartifactالمجاورة.
