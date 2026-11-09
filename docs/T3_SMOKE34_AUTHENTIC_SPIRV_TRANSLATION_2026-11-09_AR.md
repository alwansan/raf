# T3 — تحويل شيدر الدخان الأصلي (Shader48/34) إلى SPIR-V: دليل CPU وليس إصلاح صورة Android

التاريخ: 2026-11-09 UTC. العامل: T3. الفرع الوحيد للكتابة: `feature/android-native-port`.
الحالة العامة: `RENDER-002 OPEN / NOT_READY 0/3`. لا تعديل على ملفات اللعبة/الشيدرات التشغيلية، ولا APK/XAPK/OBB جديد في هذا المسار.

## المصدر الأصلي المثبت

[CI42679312674](https://github.com/alwansan/raf/actions/runs/42679312674) أثبت الربط الداخلي الدقيق لـ17 ParticleSystemRenderer باسم دخان و34 خانة Material إلى Shader48 واحد، مميّز عن Shader48 آخر لآثار النار يحتوي العدد 34 نفسه. Pass أصلي NORMAL واحد: Alpha-dependent لوني/ألفا، ColorMask RGB، ZWrite OFF، Cull OFF.

[CI42681908313](https://github.com/alwansan/raf/actions/runs/42681908313) أثبت أن مُصدّر W1+B02 بنفس الهوية ونفس جلسة التصدير يخرج `ACTUAL_DUMMY_SHADER_TEXT_EXPORTER` بدل برنامج أصلي متكافئ، ولا يعرض ColorMask RGB في نص ShaderLab. لا يعني ذلك أن هوية الدخان المربّع بهاتف المالك قد حُسمت.

[CI42683328646](https://github.com/alwansan/raf/actions/runs/42683328646) أثبت SHA الأصل ZIP2 الثابت `15964ea8f246b6e076ce26b60931ee2e1a9a2385` وستة ملفات مشاهد وأربعة owners، وداخل Shader48 الأصلي جدول D3D11 بعدد 8 records و2 vertex و2 fragment و**زوجان متطابقان في keyword/player-bucket**، دون unmatched stage.

## تجربة التحويل الأصلية الجديدة

- ملفات التنفيذ: `scripts/t3_original_smoke34_spirv_translation.py`، `tests/test_t3_original_smoke34_spirv_translation.py`، `.github/workflows/raft-t3-original-smoke34-spirv-translation.yml`.
- [CI42687117806](https://github.com/alwansan/raf/actions/runs/42687117806) **COMPLETED SUCCESS** على `40ed30bd352eb37661e3f93f0891b59ee8bf38dd`؛ 10 اختبارات Python مصدر-حر + 7 اختبارات جرد سابقة نجحت، ثم SHA المصدر الحقيقي، وتحويل 4/4 مراحل DXBC أصلية خاصة إلى Vulkan1.1 SPIR-V صالح، واستعادة HLSL خاصة 4/4، وإعادة تحويل SPIR-V صالح 4/4.
- توافق واجهات Vertex/Fragment بين الزوجين الأصليين =2/2، وبعد إعادة التحويل =2/2. انعكاس `spirv-cross` ناجح 4/4 بالمصدر وبإعادة التحويل. مقارنة مورد stage shape =4/4.
- **عدم تطابق ترتيب/نوع/مواقع stage I/O في المقارنة الأصلية مقابل الدائرية =4/4** (`original_roundtrip_io_equal=0/4`). هذا لا يساوي عدم توافق VS/FS؛ يتطلب تصنيفاً مستقلاً للمواقع والأنواع قبل كتابة ShaderLab. بناءً على هذه الفجوة أضيفت فحوص aggregate `classify_stage_io` في [commit 7bc1b54](https://github.com/alwansan/raf/commit/7bc1b5430ca29eb5578bc8fb284e17b6107c3d4f) مع اختبارين سلبيين جديدين؛ [CI42687834153](https://github.com/alwansan/raf/actions/runs/42687834153) بدأ بمدخلات أصلية مثبتة البصمة لتحديد نوع الاختلاف، والنتيجة التفصيلية غير متوفرة عند كتابة هذه الفقرة.
- Artifact الأول الآمن [13704513572](https://github.com/alwansan/raf/actions/runs/42687117806/artifacts/13704513572)، يحوي JSON aggregate فقط، ولا يحتوي DXBC ولا shader source ولا private GUID/PathID/hash ولا ملفات لعبة. تنتهي صلاحية artifact بتاريخ 16 نوفمبر 2026 UTC.

## حدود النتيجة والإصلاح المقبل

المثبت هنا **CPU stage translation feasibility** لشيدر دخان أصلي محدّد وبزوجَي keywords، وليس ShaderLab مجمعاً في Unity ولا إثبات binding/alpha texture/vertex stream/Adreno. بقاء اختلاف stage IO بعد SPIR-V/HLSL roundtrip يعني عدم اعتماد shader الناتج أو تحوير أصل اللعبة. تحقّق أولاً من التصنيف الآمن (location-only remap vs actual type/slot drift)، ثم أنشئ mapping stage location وإصلاحًا قابلًا للفحص يضمن توافق Pass، Keyword permutations وColorMask RGB وblend والعمق وtexture alpha قبل تجربة Unity معزولة. يلزم تصوير لعبة Raft من المالك لاحقاً للحسم البصري؛ لا تتعامل مع Mini GLES المختبري على أنه إصلاح للدخان الأصلي.

لا تغيّر حفظ العالم/الصوت/Settings/touch، ولا تصدر Trial XAPK أو Mini APK لهذا الاختبار دون حاجة هاتف فعلية ومراجعة الفريق. تصويت XAPK/جاهزية 0/3 مستقل.
