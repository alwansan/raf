# T3 scheduled — isolate 921-source shader IO reflection drift

- identity: T3; origin: scheduled; session_id: `20261105T1526Z-T3-scheduled-iosem-6c42`; status: completed (diagnostic helper only).
- baseline HEAD: `ef29c202aad740ced71fac943b574ae9232a40df`.
- resumed_from: `20261105T1459Z-T3-chat-921-4pass-translation-c7d2`, `20261105T1428Z-T3-scheduled-a7c9`.
- issue: RENDER-002 OPEN; NOT_READY.
- registered work before code: `prompt/coordination/work/RENDER-002/T3-20261105T1526Z-T3-scheduled-iosem-6c42-stage-io-classification.json`.
- unique experiment key: `T3-921-Shader48-4pass-8stage-DXBC-SPIRV-HLSL-roundtrip-IO-decoration-type-builtin-categorization-v1`.
- inherited authentic [CI42052605123](https://github.com/alwansan/raf/actions/runs/42052605123): 8/8 real D3D11 stage SPIR-V and HLSL-roundtrip validation, 8/8 numeric binding equality, **0/8 original-to-roundtrip IO list equality**; 4/4 internal V/F pairs structurally compatible. Cause unknown. Do not equate numeric slot equality with semantic binding equivalence.
- created `scripts/t3_stage_io_drift.py` at `92d35ce9f376b2ffedc43bac43c7b9b893828d4b`; added `tests/test_t3_stage_io_drift.py` at `51fd7e83f14abc85e4967319c0c722b19cd857e2`. The independent helper classifies per-side missing/added locations, same-location type changes and multiset-preserving relocation candidates, returns integer aggregates only. It rejects duplicate locations, malformed schema and oversized interface lists. No original code, type strings, paths, hashes or game resources published.
- local synthetic validation (same algorithm in isolated Python module): `python -m unittest -v test_t3_stage_io.py` **5/5 PASS**. GitHub CI for repository test is **not yet verified**; no genuine shader re-export, Vulkan or Unity phone test was run by this session.
- checked current branch `ef29c202`, recent Actions T1 FFT success #42054085947 and T4 original save producer success #42053882300; no equivalent IO classification run identified in inspected recent runs. Other T3 chat owns full original four-pass translator; this session deliberately did **not** modify it or dispatch equivalent heavy CI.
- rejected inference: 0/8 location/type mismatch alone cannot distinguish relocation from semantic loss; existing data only supports ambiguity. No ShaderLab or device graphics repair asserted.
- next: add opt-in call to `classify_stage_io` inside T3 four-pass translator after reading its latest version and checking active chat scope; accumulate aggregate counters only. Add test for input/output asymmetric drift. Then one original run only when it asks a distinct question and CI resources are clear; if all types preserved with relocated locations, investigate semantics/builtin decorations before any shader installation.
- preserved all .meta/GUID/scene/.rgd, audio, Settings, deferred touch. No Action cancelled. T1/T2/T4/T5 files untouched.
