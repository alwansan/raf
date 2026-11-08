# T4 — first relative packet CI verification
session_id: 20261108T0540Z-T4-scheduled-ci-proof-v8m2
origin: scheduled
resumed_from_sessions:
- 20261108T0442Z-T4-scheduled-first-relative-m7q2
- 20261108T0336Z-T4-scheduled-ci-verified-h8p3
base_sha: 1ea871e42bbfc562ddd787306e2d726884037ce1
scope_commit: d419727beeaaa1c2d4340257ebb3c10c64a3ddba
issue_id: INPUT-005
status: completed (verification scope only)

## Owner phone evidence
Owner confirmed playable world, save, exit and reopening on run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source e9c358eda01785b65e4eb14f18723da426635628. Package publication failed separately. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. This older APK does not establish newer mouse telemetry or device success.

## New verified result
Read current HEAD and checked Actions status. [CI42447922773](https://github.com/alwansan/raf/actions/runs/42447922773) completed SUCCESS on exact source 125efe37c834fa521cfabc289c01d72b6e42757c, **after** the new first-relative-packet test was committed. Its classifier-source-only job and 'Verify source-only classifier regression suite' step both completed SUCCESS. Earlier [CI42447918736](https://github.com/alwansan/raf/actions/runs/42447918736) and [capture bridge CI42447918743](https://github.com/alwansan/raf/actions/runs/42447918743) also completed SUCCESS at earlier 8d52dd6e source. No need to duplicate CI. This resolves the previous waiting_ci uncertainty; it does not prove Android physical pointer capture, authored Raft cursor, camera edge behavior or native Unity acceptance.

## Scope/coordination
Registered own isolated work prompt/coordination/work/INPUT-005/20261108T0540Z-T4-scheduled-ci-proof-v8m2.json before verifying job steps, expected SHA lease without force. No gameplay code, .meta, GUID, .rgd, keyboard, touch, audio or Settings changed; T5 continues button placement and Resolution. No Actions canceled or started. INPUT-005 and LOCAL-005 remain OPEN, full game NOT_READY.

## Next
On newly installed APK that contains physical_mouse_capture_retry and first relative movement diagnostics, collect full device log for gameplay -> Escape/menu -> gameplay, mouse detach/focus loss, keyboard retained, cursor state. Correlate capture intent/epoch/request/retry/first relative/release with screen edges. Fix only demonstrated runtime cause and test phone; preserve owner save/reopen success and T5 scope.
