# T2 independent scope
session_id: 20261109T0020Z-T2-scheduled-7c4d
origin: scheduled
issue_id: WATER-001
status: in_progress
baseline_head: 8fe2ba6c4804c8f676fd8b2abb081beb4b328a84
experiment_key: t2-gles-jsonl-duplicate-rgba-readback-v1
intended_files:
  - scripts/t2_gles_device_jsonl_gate.py
  - tests/test_t2_gles_device_jsonl_gate.py
  - prompt/coordination/clients/T2/sessions/20261109T0020Z-T2-scheduled-7c4d.md
hypothesis: CASE02 parser searches first occurrence of each RGBA marker and can accept a second contradictory occurrence, allowing a misleading PASS text. Fail closed on duplicated readback markers.
resource_key: none
shared_resource: none
resumed_from: 20261108T221725Z-T2-scheduled-6c91 and 20261108T1956Z-T2-chat-pass1-source-kind-4d6a
source: CL read-only; no original assets, shader modifications, T3 files, APK, or Unity.
validation: local unittest if source accessible; otherwise CI/source-only explicit unverified.
