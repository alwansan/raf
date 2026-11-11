# T4 INPUT-005 scope 20261111T0040Z-T4-scheduled-marker-guard-v4q8
origin=scheduled
base_head=6698b0dc40a0909a7b712d179efdc28142839459
scope=mouse boundary trace parser integrity only, no Android/Unity gameplay modifications
files=scripts/t4_mouse_boundary_trace.py; scripts/test_t4_mouse_boundary_trace.py; this work file; separate session file
hypothesis=the current parser accepts marker substring within other words and reads key/value fields outside marker, permitting false stage correlations.
experiment_key=INPUT-005-marker-boundary-20261111
shared_resource=none; no CI or Unity build requested
owner_device=42058825739 world create/save/reopen proven on phone; no regressions to .rgd, keyboard, Settings, audio.
coordination=distinct parser integrity work, no T5 Resolution changes, no T1-T3 graphics changes. Last T4 session 20261110T2336Z-T4-scheduled-ci-result-m8q2.md confirms CI 42916987581 source-only success.
next=reject false markers and ambiguous duplicate fields, add source-only regressions, preserve legacy log format; then instrument real Android/Unity/Raft path separately.
