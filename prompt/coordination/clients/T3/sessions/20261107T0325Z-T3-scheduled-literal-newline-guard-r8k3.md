# T3 scheduled — literal newline syntax repair

- session_id: 20261107T0325Z-T3-scheduled-literal-newline-guard-r8k3
- origin: scheduled; identity: T3; RENDER-002 OPEN / NOT_READY.
- Owner source: docs/DEVICE_FEEDBACK_42058825739_AR.md; device artifact 42058825739 is limited phone proof of world enter/save/exit/reenter, not graphics repair. CL source pin 520c4cf409aa20a4db54ff80ed87d8807d9cba57. White hand/raft, lighting and square smoke still OPEN.
- Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM operating model, coordination, T3 state/memory and latest scheduled session 20261107T0227Z-T3-scheduled-schema-extra-fields-a8d4.
- Registered isolated work BEFORE edit: prompt/coordination/work/RENDER-002/20261107T0325Z-T3-scheduled-literal-newline-guard-r8k3.json, commit 2c1193e8.
- Exact source blob c00ab5e5fb53a31c9ed95aca40fd6929569fa1c5 had literal `\\n` characters embedded in Python comment and subsequent for-loop in `check_contract`. As committed, Python treats the whole first physical line as comment and the following code is not executable; earlier CI42318375479 on SHA 55b39631 does not prove this latest source valid.
- Replaced only literal escapes in this block with real line breaks, preserving namespace guard and validation semantics; source commit 0e0d02ddb621111432fad6c54483203df8b404c1; resulting blob f932f0b64270f64430a259f48b4a05982b733a5c.
- No new Unity/CI or phone test. Attempted to acquire raw source for local Python tests; environment DNS failed with `URLError [Errno -3] Temporary failure in name resolution`. Thus source patch is published, **not test-confirmed**; run `python3 -m unittest discover -s tests -p 'test_t3_dxbc_spirv_contract_join*.py' -v` on new SHA when runner available.
- Next: check live branch HEAD and CI for test result, then map authentic Shader48 RDEF/SPIR-V reflection and material/particle provenance; do not repeat synthetic-only work instead of authentic integration. T4 mouse and T5 resolution/button scopes untouched. No game resources, shaders, .meta/GUID/.rgd, FMOD or Settings changed.
- Trial build vote unchanged: لا يحتاج. RENDER-002 OPEN / NOT_READY.
