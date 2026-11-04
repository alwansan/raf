> **توجيه المالك الأحدث — فريق B01–B50 / 2026-11-04:** العملاء السابقون متوقفون بحسب المالك؛ حافظ على إصلاحاتهم وأدلتهم، وتجاوز حجوزاتهم القديمة دون انتظارهم. المرجع الحالي [فريق B](B_TEAM/TEMPLATES.md). الأسماء معروفة في الجلسات ولا تُغيّر. الأولوية للماء/FFT والشيدرات والألوان والخامات ودخول العالم المحلي؛ الصوت وSettings يعملان بحسب تجربة المالك، والتاتش/الأزرار/layout مؤجلة بلا تطوير الآن. المصدر ZIP2 مثبت، والأرشيف الخاص متاح لكن يلزم تحقق payload: metadata الحالية تختلف عن manifest. لفريق B إذن التجارب اللازمة بما فيها Unity/رسوميات وفق التنسيق والميزانية والأصالة؛ حدود CPU-only التاريخية ليست قيداً على هذا الفريق. الاختبارات/النسخ التشخيصية لا تعني READY ولا تبرر dummy أوfake flags. راجع أحدث السجلات: Steam StoreStats يفشل داخل SaveGame بعد WorldHasBeenLoaded فيAPK86. لا تغيّر جداول ولا تُفعّل العملاء السابقين ولا تلغِjobs. ما يلي من تعليمات متعارضة تاريخي؛ تفاصيل التوجيه الحي في ملفات B_TEAM.

# قوالب السجلات

الوقت UTC بصيغة ISO8601؛ الحقول غير المعروفة null، لا تختلق SHA/run.

## clients/<username>/state.json

```json
{"schema_version":1,"username":"REPLACE","session_id":"REPLACE","resumed_from":null,"status":"active","updated_at":"REPLACE_UTC","base_sha":null,"current_work":[],"last_commit":null,"next_step":"","memory_path":"prompt/coordination/clients/REPLACE/MEMORY.md"}
```

## work/<issue>/<username>-<id>.json

```json
{"schema_version":1,"owner":"REPLACE","issue_id":"WATER-001","status":"planned","updated_at":"REPLACE_UTC","base_sha":null,"hypothesis":"","intended_files":[],"related_work":[],"experiment_ids":[],"evidence":[],"result":null,"next_step":""}
```

حالات العمل: planned/active/blocked/paused/completed. لا تغيّر سجل عميل آخر؛ اكتب رداً مرتبطاً.

## experiments/<username>/<id>.json

```json
{"schema_version":1,"owner":"REPLACE","status":"planned","hypothesis":"","input_hashes":[],"commands":[],"expected_signal":"","negative_controls":[],"workflow_path":null,"concurrency_group":null,"artifact_prefix":null,"budget":"","run_url":null,"source_sha":null,"result":null,"limitations":[],"next_step":""}
```

## MEMORY.md

اكتب الهدف، آخر مصدر راجعته، الأدلة وروابط commits/runs، الفرضيات المرفوضة، الملفات التي غيرتها، الرسائل المقروءة، نقطة الاستعادة، والخطوة التالية. لا تضع أسراراً أو سورس مفككاً.

## رسالة/عطل

حقول Markdown: المؤلف، الوقت، المشكلة، الرد على، المصدر، الدليل، الحالة، الأثر، المطلوب/الإجراء، الخطوة التالية. لا تنتظر الرد إن كان هناك عمل مستقل ممكن.
