# T3 isolated scope — PNG critical chunk validation

- session_id: 20261109T0533Z-T3-scheduled-png-structure-v8n4
- origin: scheduled
- baseline HEAD: 6ae2ee2b241c4d6d3b45e066d01684066cafb392
- issue: RENDER-002 OPEN / NOT_READY
- hypothesis: PNG parser accepts malformed critical chunk ordering (IHDR not first, duplicate IHDR, noncontiguous IDAT), which could misclassify CL captures as valid evidence.
- files: scripts/t3_cl_png_pixel_audit.py, tests/test_t3_cl_png_pixel_audit.py, this work file and separate session file.
- experiment_key: t3-png-critical-order-sourcefree-v1
- shared_resource: none; no Unity/Android/CI dispatch.
- overlap: T3 chat working on original smoke shader; this scope modifies only PNG audit; T1/T2 water, T4 mouse, T5 delivery/resolution unaffected.
- inherited: 20261109T0425Z-T3-scheduled-rgba-alpha-k5p7; 20261109T0150Z-T3-chat-particle-emitter-3p7k.
- acceptance: malformed order rejected with deterministic ValueError; valid PNG remains accepted; source-only proof, not device or Raft graphics.
