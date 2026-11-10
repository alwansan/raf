# T4 INPUT-005 — device capture/gameplay boundary
session_id: 20261110T0042Z-T4-scheduled-capture-device-boundary-p7x4
origin: scheduled
baseline_sha: 9ee4ba027df6e968370f942eafc7ab19b412bcde
branch: feature/android-native-port
scope: independent device-evidence acceptance protocol; no Unity, T5 Resolution, touch, keyboard, .rgd, or shared mini source modifications.
experiment_key: T4-CAPTURE-GAME-BOUNDARY-20261110
shared_resource: none; no CI/native build requested.

## Hypothesis and evidence gate
Owner world/create/save/reopen is OWNER_CONFIRMED only on Artifact 42058825739, source e9c358ed; delivery publication failed. The 2026-11-08 CL/test mini trace proved 13 LEFT press/release and 55 vertical scroll callbacks with captured=false, not captured gameplay. T4 source bridge staged 20 original Unity Legacy button/wheel call sites; CI42518143297 proves source tests, not device behavior. CI42704145152 source success. Latest checked branch HEAD 9ee4ba027df6e968370f942eafc7ab19b412bcde; CI42728727179 T3 synthetic success, not mouse.

## Distinguishing experiment (next signed game, not mini)
Record build artifact ID, signed APK hash/versionCode, OBB hash/version and logger session ID. In one process-local log, collect pointer capture requested/accepted, ACTION_BUTTON_PRESS/RELEASE and ACTION_SCROLL, and Unity legacy getter counters with same capture epoch and session. For each LEFT/RIGHT/MIDDLE independently demand physical press+release, Unity down/held/up evidence, and visible in-game reaction. For vertical and horizontal wheel require nonzero captured callbacks, matching Unity getter slot and gameplay reaction; if hardware does not emit horizontal, mark NOT_TESTED not FAIL. Verify camera continues past screen edges, cursor belongs to Raft in menus, capture releases on focus loss/disconnect and reacquires on return, keyboard still works. Compare to original artifact world/.rgd without mutating original saves. Distinguish callbacks seen, Unity getters seen, and game action confirmed; never promote source-only/mini proof to game PASS.

## Next action
When T5 has a new authorized signed game build, use same-process original JSONL (not concatenated mini logs) and scripts/t4_correlate_mouse_runtime_epochs.py, then map missing channel to Android listener, JNI bridge, original Legacy getter, or Raft gameplay consumer. Preserve existing successful save and Settings/audio. Do not duplicate existing CI.
