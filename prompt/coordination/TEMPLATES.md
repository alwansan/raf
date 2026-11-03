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
