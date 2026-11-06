# T2 source-only exported Foam .mat completeness guard

- session_id: 20261106T2138Z-T2-chat-foam-matdoc-82bd
- origin: chat
- status: active
- base_sha: afa18e3371c882f2b0842111ef6ea61aa78b71fc
- updated_at: 2026-11-06T21:38:01Z
- resumed_from_sessions: 20261106T2117Z-T2-scheduled-foam-ci-reconcile-k6m2; 20261106T2044Z-T2-chat-field-consumer-trace-d4a6
- issue_id: WATER-001
- work: prompt/coordination/work/WATER-001/20261106T2138Z-T2-chat-foam-matdoc-82bd.json
- observed gap: scripts/t2_foam_export_binding_probe.py accepts a %YAML .mat with no Material (!u!21) document and reports a clean inventory, unlike the inherited broad W1 auditor. This can hide a malformed Material asset while the test falsely reports complete GUID pointers.
- scope: read-only probe + synthetic tests only; no private bytes/Unity/GUID/game modifications; existing path-filter source-only CI.
- active native: https://github.com/alwansan/raf/actions/runs/42296450023 (independent T5/owner build; don't cancel or duplicate).
- plan: add red/green malformed .mat document guard while preserving legitimate no-.mat dynamic Material case; run existing synthetic CI; document verified limits.
- next_step: edit two isolated files, validate by source-only CI, close work and record result.
