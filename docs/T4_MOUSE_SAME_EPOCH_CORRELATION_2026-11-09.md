# T4 — تحقق مستقل من تطابق جيل Android Pointer Capture مع Unity Legacy Input

**التاريخ:** 2026-11-09 UTC 19:00  
**العميل:** T4؛ **origin=chat**؛ **session_id:** `20261109T1858Z-T4-chat-epoch-evidence-p6m4`  
**المشكلة:** INPUT-005 مفتوحة؛ لا يوجد قبول جهاز كامل.

## السؤال الهندسي

يعرض كود المصدر الأصلي المعدّل لـ Raft عدّادات `physical_mouse_captured_action_callbacks` من `OnCapturedPointerListener`، وعدّادات `physical_mouse_legacy_reader_evidence` من استدعاءات `Input.GetMouseButton*` و`Input.GetAxis("Mouse ScrollWheel")` و`Input.mouseScrollDelta` في مواضع المصدر الأصلية المصادق عليها. كون كل مؤشر غير صفري في سجل طويل **لا يثبت** أنهما متعلقان بمحاولة التقاط واحدة: إعادة الطلب ترفع `epoch`؛ تحرير الالتقاط ينهي محاولة؛ وكل تشغيل جديد يمكن أن يبدأ عدّاد الأجيال من الصفر.

## التنفيذ المحصور

- `scripts/t4_correlate_mouse_runtime_epochs.py`: يقبل سجلاً نصياً أو JSONL بترتيب زمني **لعملية لعبة واحدة فقط**، ويقسمه عند `physical_mouse_capture_requested/retry` و`physical_mouse_capture_released`. يقبل مؤشرات `epoch` المتطابقة وحدها، ولا يدمج أحداثاً قبل الطلب أو بعد التحرير. يرفض العدّادات غير الصالحة، والعدّادات الراجعة، وحالة `captureObserved=false`، ويشترط حارسَي المصدر `countersAreGetterCallsNotClicks=true` و`unityGameplayVerified=false`.
- `scripts/tests/test_t4_correlate_mouse_runtime_epochs.py`: أربعة عشر فحصاً لمطابقة الجيل، اختلافه، تغيير ترتيب الطباعة داخل Unity Update، مصدر JSONL، التحرير، إعادة الطلب، أحداث callbacks فقط، getters فقط، fallback صفر، capture=false، العدّادات المستحيلة، التراجع العددي، فقد معرف الجيل والحدود.
- `.github/workflows/raft-t4-mouse-epoch-correlation.yml`: CI خفيف باسم T4، Python فقط، Ubuntu 24.04، مهلة خمس دقائق، دون Unity player أو إنشاء APK، و`cancel-in-progress: false`.

## الدليل

- **CI [42679181503](https://github.com/alwansan/raf/actions/runs/42679181503) SUCCESS** على SHA `14a5d794ee5409d0f1ba32fb0436e480b4467230`؛ خطوة `Validate source-only capture epoch correlation fail-closed controls` نجحت (14 unittest).
- تجربة المصدر الأسبق **CI [42549986761](https://github.com/alwansan/raf/actions/runs/42549986761)** أثبتت على مستوى المصدر فقط ربط 20 قارئاً أصلياً، وعدّاد `PhysicalMouseLegacyReaderEvidence`، ونجاح compile في Android/Editor؛ هذا لا يساوي تجربة الهاتف.
- سجل المالك CL/test المقروء حتى `alwansan/CL@24a677fc8fa4749c0bcf8a3cac01fa80b1641c86` يحوي جلسات 8 نوفمبر؛ أحدث `shared-20261108-232759-468049775` يركز على T3 ولا يضيف دليلاً جديداً لـ T4 capture=true. سجل T4 الأصلي `CL@4680f5dc` لا يحتوي `capture_request ON` أو `captured=true`؛ كانت أزرار LEFT وعجلة V في مسار uncaptured فقط.

## معيار الحسم وحدود الدليل

حالة `SAME_EPOCH_CAPTURED_CALLBACK_AND_FALLBACK_GETTER` تعني أن سجل عملية اللعبة احتوى **مؤشر Android captured** و**استدعاء Unity Legacy getter استعمل fallback** في `epoch` نفسه؛ لا تثبت أن الحدثين نفس الضغطة، أو أن واجهة اللعبة استجابت، أو أن اختبار الهاتف ناجح. `device_pass=false` و`unity_gameplay_verified=false` دائماً.

**لا تمزج ملفات عمليات أو تشغيلات مختلفة**: يمكن تكرار epoch بعد إعادة تشغيل التطبيق، ولا يمكن للفاحص إثبات توقيع APK أو التطابق بين artifact المصدر والهاتف من النص وحده. يجب تثبيت APK SHA والتشغيل وسجل العملية الواحد خارجياً. لا تمرر سجلات mini APK إلى هذا الفاحص على أنها سجل Unity الأصلي.

## التسليم

عند وجود XAPK موقّع من T5 يتضمن إصلاح T4، يشغّل المالك Raft بماوس فعلي ويسجل LEFT/RIGHT/MIDDLE وعجلة V/H مع حركة الكاميرا وحالة focus، ثم يُحلّل **سجل Raft نفسه من عملية واحدة** باستعمال:

```bash
python3 scripts/t4_correlate_mouse_runtime_epochs.py /path/to/one-raft-process-log.txt
```

يُقارن بعدها المصدر المرتبط بتوقيع APK مع `physical_mouse_captured_action_callbacks` و`physical_mouse_legacy_reader_evidence` ويراجع السلوك داخل اللعبة والحفظ/فتح العالم. لا تبنِ mini جديداً أو XAPK بناءً على نجاح هذا السكربت. T5 يحتفظ بملكية المختبر المشترك، والفريق يعمل فقط على `feature/android-native-port`.

**INPUT-005 OPEN | full game NOT_READY 0/3.**
