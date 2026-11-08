# T2 independent scope — GLES device JSONL evidence integrity
session_id: 20261108T2120Z-T2-scheduled-gles-evidence-q6m2
origin: scheduled
baseline_head: c957dcf4e0312df2fea28adfdeb742b8e519f3be
issue: WATER-001 (device synthetic controls only)
experiment_key: T2-GLES-JSONL-EVIDENCE-INTEGRITY-20261108
resource: CL shared mini JSONL, read-only
resumed_from: clients/T2/sessions/20261108T2015Z-T2-scheduled-cl-gpu-evidence-v8q2.md and clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md
files: scripts/t2_gles_device_jsonl_gate.py, tests/test_t2_gles_device_jsonl_gate.py, own session/work only
hypothesis: a summary PASS alone can hide mismatched, duplicated or missing per-case GL observation. Validate one bounded device JSONL stream, strict case identity and exact auto/GL agreement without leaking device log details.
non_overlap: independent of T2 chat original Cecil scanner, T3 materials and T5 shared app; no APK/Unity or workflow edits.
acceptance: negative tests for wrong case, mismatch, duplicates, absent context, malformed JSON and spoofed OK; report only safe pass status and case id. This does not validate original water shaders.
status: SOURCE_IMPLEMENTED_TESTS_NOT_EXECUTED
commits: 3f7063fb92200f2135edc65956a29ef2a34ce9e4; b9ae1c0ae79c76c7298904d34b0b672f9ddc3a08; 37973a7e6549494b39508e969b5f16e7e1293be2
verification: actual CL CASE01 JSONL structure inspected; local test fetch blocked by DNS, no claim of passing tests or Raft pixels.
next: run source-free Python tests, validate four real CL case streams; compare only matching version/pack/session; continue original CFG and CB0 in separate chat scope.
