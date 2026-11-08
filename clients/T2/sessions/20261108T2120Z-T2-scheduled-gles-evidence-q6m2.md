# T2 scheduled — independent GLES JSONL provenance gate
session_id: 20261108T2120Z-T2-scheduled-gles-evidence-q6m2
origin: scheduled
branch: feature/android-native-port
initial_head: c957dcf4e0312df2fea28adfdeb742b8e519f3be
owner_device_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 phone world/save/reopen confirmed for that artifact only; water unresolved.
resumed_from: clients/T2/sessions/20261108T2015Z-T2-scheduled-cl-gpu-evidence-v8q2.md and clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md
experiment_key: T2-GLES-JSONL-EVIDENCE-INTEGRITY-20261108
issue: WATER-001 OPEN
scope: source-free device JSONL evidence consistency; independent of original-Cecil chat scanner and T3/T5 app code.
source_reference: alwansan/CL/test/shared-20261108-230157-466487336/t2-gles-20261108-230235-466525434.jsonl (read only); actual source stream includes startup, gl_context, surface, case_start, gl_observed, shared_auto_result, export, pause/stop.
source_commits: 3b8fb2134c30d8a8f0dab3ab3afd3bde7d266c5d (scope); 3f7063fb92200f2135edc65956a29ef2a34ce9e4 (gate); b9ae1c0ae79c76c7298904d34b0b672f9ddc3a08 (tests).
result: Implemented independent strict per-case JSONL gate with exact session/worker/case, ordered unique GL events, matching auto vs GL observation, bounded schema, duplicate-key rejection and fixed per-case measurement markers. Seven adversarial unit tests added. No private device data copied into repository; output only case/synthetic consistency/original-water-false.
verification: source and actual CL sample inspected via connected GitHub. Attempted to execute local tests but container DNS could not resolve raw.githubusercontent.com; tests NOT EXECUTED and no CI triggered. Does not validate actual GL pixels or game shader.
next_step: execute python -m unittest tests.test_t2_gles_device_jsonl_gate (or discover); then python -m scripts.t2_gles_device_jsonl_gate CASE01 <CL CASE01 JSONL> and similarly cases 02–04. Only after independently checking actual files can mark device JSONL integrity validated. Continue original pass1 CFG/CB0 with chat scanner, coordinate T3 effects; do not duplicate shared mini APK.
