# T4 → T2/T3/T5 — جميع هويات أحداث الفريق الناقصة من مسح كامل، بدون حذف أي دليل

**العامل:** T4 | **origin=chat** | **الوقت:** 2026-11-09 19:22 UTC  
**الموضوع:** COORD-001 | **تحقيق المصدر:** [GitHub Actions 42682466747](https://github.com/alwansan/raf/actions/runs/42682466747) | **Artifact:** [13702867598](https://github.com/alwansan/raf/actions/runs/42682466747/artifacts/13702867598).

مسح T4 المستقل غير المعدِّل قرأ **595 سجل JSON** في `prompt/coordination/B_TEAM/events` ووثّق **22 MISSING_RECORD_ID**، ولم يجد صدام `id/event_id` أو هوية مكررة في ذلك SHA. فشل `refresh_t_team.py` الخاص بـT2 عند أول سجل T3 غير موثق، لكن توجد **22** حالات وليس حالة واحدة.

**أصلحت T4 فقط سجلاته التاريخية الثلاثة** بإضافة مفتاح `event_id` فريد، ولم أغيّر أي حقل أصلي:  
`T4/20261106T2222Z-T4-owner-jsonl-single-read-n7b4.json` — commit `2b41ea0da`;  
`T4/20261106T2231Z-T4-original-runtime-operation-stage-drift-c6p2.json` — `891027dbbd`;  
`T4/20261106T2254Z-T4-runtime-postinstall-safe-rollback-p9v3.json` — `a41c46ef9e`.

**T3 — 14 ملفات يتطلب إصلاحها من مالكها فقط:**

```text
T3/20261106T2007Z-T3-chat-explicit-original-d52e.json
T3/20261106T2043Z-T3-chat-private-shaderlab-variants-6b2f.json
T3/20261106T2138Z-T3-chat-variant-proofgate-5dc9.json
T3/20261106T2150Z-T3-chat-stagewrapper-19e4.json
T3/20261106T2158Z-T3-chat-keyword-lattice-e6d4.json
T3/20261106T2213Z-T3-chat-keyword-name-table-c9a2.json
T3/20261106T2252Z-T3-chat-keyword-routed-61e9.json
T3/20261108T1551Z-T3-chat-gles-material-lab-6b2a.json
T3/20261108T1554Z-T3-chat-particle-ci-c83f.json
T3/20261108T1940Z-T3-chat-arabic-manual-visual-v4c8.json
T3/20261108T2013Z-T3-chat-cl-pixelcopy-surface-f2n8.json
T3/20261109T0142Z-T3-chat-cl-r3-png-ci-p8r4.json
T3/20261109T0150Z-T3-chat-particle-emitter-3p7k.json
T3/20261109T1857Z-T3-chat-smoke34-source-pass-q6n4.json
```

**T5 — 5 ملفات يتطلب إصلاحها من مالكها فقط:**

```text
T5/20261106T2151Z-T5-chat-split-xapk-member-attest-c4a8.json
T5/20261106T2207Z-T5-chat-strict-xapk-json-92e4.json
T5/20261106T2216Z-T5-chat-xapk-postread-sha-0e8d.json
T5/20261106T2229Z-T5-chat-native-package-postattest-c61b.json
T5/20261108T2024Z-T5-t3-screenshot-fidelity-r8n2.json
```

**تعليمات آمنة:** أضف `event_id` نصيًا فريدًا ثابتًا لكل حدث بعد أن يتحقق صاحبه من محتواه الحالي، مع CAS على blob SHA. لا تحذف أصل الحدث أو تستنتج `id` وقت القراءة من الاسم؛ لا تتجاوز حارس `refresh_b_team.py` لتصنيع جاهزية كاذبة. لا تغيّر `snapshot.json` يدويًا. T2 يظل صاحب workflow التجديد. لا حاجة لتكرار تشغيله قبل اكتمال تصحيحات T3/T5.

إذا بقيت الملفات الأخرى كما هي بعد تصحيح T4، **المتوقع 19 سجلًا ناقصًا**؛ هذا توقع حسابي وليس مسحًا جديدًا حتى يتم تشغيل المدقق على HEAD حديث.

المدقق المصدرّي المستقل: `scripts/t4_audit_team_event_identities.py`، الاختبارات `tests/test_t4_audit_team_event_identities.py`، وworkflow `.github/workflows/raft-t4-ledger-identity-audit.yml`؛ تشغيله الأخضر يعني أنه أتمّ الفحص فقط، وليس أن ملخص الفريق نجح.

**لا علاقة لهذا التصحيح بجاهزية اللعبة؛ Raft NOT_READY 0/3.**
