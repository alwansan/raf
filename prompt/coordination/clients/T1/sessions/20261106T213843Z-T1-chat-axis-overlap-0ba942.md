# T1 — bounded original FFT coordinate-axis overlap diagnosis

- session_id: `20261106T213843Z-T1-chat-axis-overlap-0ba942`; origin: `chat`.
- resumed_from: `20261106T2114Z-T1-scheduled-axis-coverage-p7m2`, `20261106T2052Z-T1-chat-actual-variant-comparator-e28c`.
- base_sha: `1d608192634db991e246b812f84ead1ec422810c`; writable branch only `feature/android-native-port`.
- state: active, scoped source-only mathematical/test guard; work: `prompt/coordination/work/WATER-001/20261106T213843Z-T1-chat-axis-overlap-0ba942.json`.
- Baseline actual original Vulkan vs Unity OpenGLCore 42289238865: coordinate mismatches [63,252,64]; X-zero [63,252,63], Y-zero [0,0,64]. Integer-source 42290211798: [0,252,64], X-zero [0,252,63], Y-zero [0,0,64]; output still unequal.
- Hypothesis: site2 x/y zero-collapse intersection is **exactly 63**, since there are 64 mismatches and y-zero count is 64; site1 is x-only zero collapse. This is only an aggregate necessary bound, not proof of shared per-invocation cause, FTZ, integer-source fix of site2, original authored kernel mapping or Android water.
- Collision check: prior T1 scheduled axis-coverage work completed and CI42295226507 succeeded; no change to its files. Native build 42296450023 active; no new Unity/ZIP2/native job.
- Intended paths: `scripts/t1_fft_coordinate_axis_overlap_gate.py`, `tests/test_t1_fft_coordinate_axis_overlap_gate.py`, own work/experiment/event/session only.
- Next: implement and execute adversarial source-only gate; record actual verified limits and follow-on original private Butterfly site2-Y reaching-store/CFG evidence before a numeric Unity/Vulkan replay.
