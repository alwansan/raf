# T4 INPUT-005 — signed-game mouse evidence boundary

session_id=20261109T2335Z-T4-scheduled-mouse-game-boundary-v3k8
origin=scheduled
identity=T4
branch=feature/android-native-port
base_sha=a7a58cd330f19a24e242014457ffac195cc77c20

## Scope and hypothesis
Read-only original game mouse runtime provenance and next acceptance decision; files: this independent work record and matching clients/T4/sessions file only. No shared resource; no Unity, T5 Resolution, testpack or game-source edit. Hypothesis: the remaining blocker is signed-game physical captured callback -> Unity getter -> gameplay action provenance, not Python gate unit tests.

## Evidence
Owner's 5 Nov Artifact 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, entered local world, saved, exited and re-entered; release/publish failed. Do not generalize to newer APK. 8 Nov CL physical mouse mini events were uncaptured; original game source fallback was staged but no phone signed-game confirmation. Existing source CI 42704145152 SUCCESS at 3a8faa8777f83ffcadb1d769db8c1c93e5aedee0. T5 offline integration CI 42715257606 FAILED at f03af6c3c4f2e0aad2cee5862787932d6e1c52da; not proof of mouse regression or Unity game runtime. Branch HEAD on read a7a58cd330f19a24e242014457ffac195cc77c20.

## Acceptance experiment (not executed)
Require one signed Raft candidate fingerprint, exact APK/OBB manifest, single process-local chronological JSONL with session/sequence, pointer capture requested/accepted, captured button press/release and vertical/horizontal scroll callbacks, same-epoch original Unity getter per-channel positive fallback/native counters, actual gameplay response, keyboard continued and focus loss/reacquire. Test LEFT/RIGHT/MIDDLE separately; distinguish unattempted buttons from failures. Preserve old .rgd, save/reopen, audio and Settings. Do not claim device_pass from source-only gate; do not launch redundant full build or alter T5 scope.

## Decision
INPUT-005 OPEN; LOCAL-005 owner-confirmed only for original artifact; NOT_READY. Next T4 step is signed-game evidence correlation or isolated real game runtime instrumentation only if needed; first check current T5 integration failure before requesting build. This cycle does not establish a code fix.
