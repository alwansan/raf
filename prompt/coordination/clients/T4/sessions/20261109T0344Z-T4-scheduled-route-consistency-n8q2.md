# T4 scheduled checkpoint — 20261109T0344Z-T4-scheduled-route-consistency-n8q2
origin: scheduled
issue_id: INPUT-005
base_sha: 3f3fbf7214fbe98f8b9ab92c2fd099617e218f3c
resumed_from_sessions: 20261109T0237Z-T4-scheduled-analyzer-comment-v3q7; 20261108T1958Z-T4-chat-legacy-button-wheel-bridge-y8m2
scope_commit: a105bda140c146e0386018955c499111fc834984
fix_commit: 301fa001114f5fe17504ed94c63d1b04d7ade3bd
test_commit: 7fe3ff379399d5ad06463a79679ef7e8d8f6c2cb

## Result
The T4 lab JSONL analyzer previously counted `captured=true` events even if `route=activity_generic` or other noncaptured route. Added explicit rejection and a separate `capture_route_conflicts` counter. Added regression asserting an inconsistent left press is rejected while a real `route=captured` right press remains counted. This is diagnostic integrity only; not a Unity mouse repair or proof of captured input on the phone.

## Owner phone baseline
Artifact run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628: owner entered world, saved, exited and re-entered. Package publishing failed independently. Original .rgd schema, keyboard, audio, Settings and gameplay source untouched. 8 November owner mouse camera improved, left/right/middle/wheel still not proven functional.

## Evidence and limits
Reviewed AGENTS, owner requirements, STATUS, T_TEAM coordination and device report; T4 memory confirms authentic original Legacy Input source adapter CI42518143297 SUCCESS, not device proof. CL/test previous mouse upload shows uncaptured callbacks; no confirmed captured=true game-to-Unity evidence. This session did not download private original data, run a phone, launch Unity, or repeat shared mini APK. New Python regression has not been executed in CI or locally because repository network access from container failed DNS; GitHub connector allowed source review and commit. Source change is intentionally narrow.

## Next
Run `python -m unittest tests.test_t4_analyze_mouse_lab_routes` in available CI without duplicate build, compare new captured=true/route=captured real CL/test export against signed game bridge logs, preserve T5's shared mini ownership. INPUT-005 OPEN, full game NOT_READY 0/3.
