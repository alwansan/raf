# T2 scheduled — synthetic CFG stack-height safety

- session_id: `20261105T1821Z-T2-scheduled-stackjoin-b4e9`; origin: `scheduled`; resumed_from_session: `20261105T1723Z-T2-scheduled-rtcfg-a72e` and read chat `20261105T1736Z-T2-chat-ret-reason-28ce`.
- baseline_sha: `d00af305e157a4d49f2815afac75cb201ebdc2db`; plan: `prompt/coordination/work/WATER-001/T2-20261105T1821Z-scheduled-cfg-stack-join.json` (actual path uses `stack-join`? verify plan below).
- Plan commit: `15b5a5fe8e48b8fe9babf833117350c4a8bafce0`; work path: `prompt/coordination/work/WATER-001/T2-20261105T1821Z-scheduled-cfg-stack-join.json` (verify exact repository path against commit).
- Source fix `0eca55b8e2f3632970960415193d599148aca6ab`: fail closed if CFG predecessor states disagree on evaluation stack height; prevents later store from erasing malformed join.
- Regression test `73c5061d71be64dba08443938ac732e954129565`: two incoming stack heights (1 and 2), both with a store then new RT allocation, expected `unknown`.
- Verification: source review and test case committed, **not executed** in this run. No original DLL/Unity/GPU/device proof. No new Actions requested; latest checked CI `42081799249` success for unrelated runner guard.
- Original evidence remains [42078263113](https://github.com/alwansan/raf/actions/runs/42078263113): single original return-local writer immediately preceded by call, typed dataflow not proved. Next: execute synthetic tests and authenticate call signature + typed stack provenance on original pinned DLL without publishing source.
- WATER-001 OPEN; NOT_READY 0/3. No ShaderLab or original assets, .meta, sound, Settings, touch or other clients' work modified.
