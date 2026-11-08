# T4 INPUT-005 evidence reconciliation — 20261108T2140Z-T4-scheduled-device-evidence-v6q9

origin: scheduled
scope: independent device-evidence reconciliation only; no runtime, T5 UI/Resolution, shared mini pack, or Unity build edits.
base_head: 2ecd1f03ecfa593ab9705a333bdf406f982d725e
experiment_key: T4-device-evidence-20261108-230157-v6q9
resource: GitHub API read-only; CL read-only
hypothesis: unified pack NEEDS_INPUT statuses are not evidence of button failure or success; only captured physical callbacks paired with actual Raft legacy consumers can close INPUT-005.

## Verified inputs
- Owner 5 Nov report: artifact 42058825739 successfully entered, saved, exited, and reopened world; publication failed, so retain limited phone acceptance and original .rgd compatibility.
- CL/test/shared-20261108-230157-466487336/summary JSON: source 93e32950c521d9890ce845eb8213cd6704cd7f98, pack SHA 6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f; T4-01..09 NEEDS_INPUT, not FAIL.
- CL/test/t4-builtin-mouse-20261108-191456-452866288/events JSONL: startup, T4-01..03 begin, pause and exports only; no captured-button/scroll events in that file.
- T4 MEMORY latest chat: original ZIP2 20 Legacy Input call sites bridged; CI42518143297 source-only SUCCESS; authentic CL uncaptured 13 left press/release pairs and 55 vertical scroll; no captured=true owner proof.
- Current GitHub Actions last 8 listed completed success; no equivalent CI launched.

## Acceptance boundary
Need same-device physical SOURCE_MOUSE, requestPointerCapture ON, captured=true, epoch-matched BUTTON_PRESS/RELEASE and ACTION_SCROLL, focus transitions, then signed game build using staged bridge with actual gameplay LEFT/RIGHT/MIDDLE and wheel observed. Verify keyboard, camera, menus, and .rgd save/load regressions. Source-only CI cannot prove this. T5 owns unified mini and UI/Resolution.

Next: inspect fresh CL/test after actual captured test; classify by capture epoch and source, compare to game logs from a SHA-matched signed artifact. Do not request redundant mini or change .rgd.
