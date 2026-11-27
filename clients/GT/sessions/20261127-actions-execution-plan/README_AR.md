# GT — تنفيذ فعلي مؤلف داخل GitHub Actions وتحديث الخطة | 27 نوفمبر 2026

حفظنا توجيه المالك الجديد في MEMORY وRESTORE والخطة العربية والآلية وstate. الرأس الحي عند بدء هذه الدفعة `1fd0565f8f7cb926a5d9143f3216e88ba31c70b5` متقدم باثنين من commits عن نقطة ربط الإيصال السابقة؛ وجدنا تجربة Unity القائمة ولم نكررها أو نلغها. وضع next23b-receipt في workflow الحالي يجهز مشروعاً مؤلفاً فارغاً ويستعمل تنشيط CI المأذون دون كشف بياناته. لا خطوات ZIP2 أو game assets، لا APK/OBB/XAPK. [Run 45929964298](https://github.com/alwansan/raf/actions/runs/45929964298) اكتمل SUCCESS، جميع خطوات job140280068547 المطلوبة ناجحة، وضع material-alpha skipped عمداً.

## القبول المحدد

- Unity2021.3.45f2 فعلي، مرشح C# schema2، checkpoint=verified، 4Pass، 1156 route، errors0، AssetBundle Android Vulkan حجم 48712 B. [الإيصال الخام](gt-next23b-unity-safe.json).
- UnityPy1.23.0 فعلي على runner، platform18، 4 LightMode و27 raw flag bytes للكلمات المطلوبة، رفض تحريف الحزمة والـmanifest، [receipt-verified.json](receipt-verified.json).
- البوابة المنشورة الكاملة وفك SMOL-V وentrypoint verification: VS وFS [512,4,128,512] لكل مرحلة، لا مجرد تسجيل SVC. [full-verified.json](full-verified.json).
- ZIP artifact15168725743 (117766 bytes) نُزّل وتطابقت بصمته مع API وفُحصت CRC والأعضاء الثمانية، الملفات المؤلفة الثلاثة مطابقة محلياً بالبايت، وإعادة verifier للإيصال وعقد المصدر نجحت على هذه البايتات. لم يتوفر UnityPy/SMOL-V محلياً لإعادة فك الحزمة. [artifact-review.json](artifact-review.json)، [stage.json](stage.json)، [evidence.json](evidence.json). المرفق الكامل موجود على Actions حتى 11 ديسمبر 2026؛ لم ننشر نسخة binary/zip إضافية في Git، لأنه ناتج مؤلف قابل لإعادة الإنشاء. احتفظنا بالإيصالات الأربع الأصلية كاملة وبصمات كل عضو، والأداة المثبتة.
- تحقق موازٍ محلي من HLSL المؤلف المتولد باستخدام cpp، 1156 مجموعة و2312 علامة VS/FS، empty indices 511/3/127/511، لا fallback إلى route0. [marker-proof.json](marker-proof.json). هذا مصدر وليس تشغيل بكسلات.

## إعادة الإنتاج

من checkout مأذون للرأس المثبت 1fd0565f8f7cb926a5d9143f3216e88ba31c70b5:
```sh
python3 -B tools/synthetic_material_alpha/next23b_receipt_probe.py stage --project /tmp/gt-authored-check --out /tmp/gt-authored-stage.json
python3 -B clients/GT/sessions/20261127-actions-execution-plan/check_authored_route_markers.py --project /tmp/gt-authored-check --out /tmp/gt-authored-markers.json
```
أداة marker في commit التوثيق الجديد (احصل عليها من هذا السجل عند إعادة التشغيل على الرأس المثبت). مسارات /tmp جديدة. مسار CI المأذون هو workflow raft-gt-synthetic-material-alpha.yml بوضع next23b-receipt؛ راجع الرأس/الأعمال النشطة، أعد التشغيل عند الحاجة فقط. لا تستخدم مسار الأصل الثقيل دون إذن. التحقق من النتيجة الفعلية موضح في workflow وnext23b_receipt_probe.py verify ثم gt_verify_921_shader_bundle --next23b. بصمة ZIP مع الأعضاء في artifact-review. لا يعتمد الاستئناف على sandbox. اختبار marker محلي وليس إعادة Unity.

## الخطوة التالية النشطة A2

نفذ اختبار Unity Vulkan مؤلف فعلي لاختيار Material/keyword runtime: علامات بكسل مميزة، empty route ليس route0، global/local وoff/on/off، ضوابط سلبية وإيصال فعلي. لا تكرر اختبارات المصدر كبديل عن التنفيذ. بعده عند توفر مصدر مأذون مثبت أثبت scope/PassType واختيار الكلمات الأصلي لـNEXT23b ودمج GUID/SAME-EXPORT، ثم عمّم على الدفعات العشر. أكمل FFT/Foam/Depth والموارد والنار والمجسمات وبقية G0–G6، لا Dummy بديل أو XAPK مبكر أو هاتف جزئي. جرد 688/786 Custom و98 Dummy/37 GUID تاريخي دون تغيير. لم يثبت أي بكسل جديد في هذه الدفعة أو إصلاح داخل اللعبة. لا clone كامل هنا بسبب DNS المباشر؛ تحققنا من الملفات الستة بالمطابقة مع Git blobs، لا تغييرات على ملفات العمل السابقة. تحديث التوثيق [skip ci] لتجنب تكرار تشغيل ناجح، لا تقييد لتفويض Actions.
