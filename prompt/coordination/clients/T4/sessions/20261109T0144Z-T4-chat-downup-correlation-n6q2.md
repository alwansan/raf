# T4 chat checkpoint — real phone Android DOWN/UP correlation

- **session_id:** `20261109T0144Z-T4-chat-downup-correlation-n6q2`
- **origin:** `chat`
- **worker:** `T4`
- **issue:** `INPUT-005` OPEN
- **base_sha at reservation:** `cf764d7671efb58dc57f5952bd1c2875e97ec504`
- **work reservation:** `prompt/coordination/work/INPUT-005/T4-20261109T0144Z-T4-chat-downup-correlation-n6q2.json` (commit `8f9a3dc691a15240ac1e93c7a48f99d35d9da1fd`)
- **resumed_from_sessions:** `20261109T0036Z-T4-scheduled-capture-evidence-q4m8` (scheduled); `20261108T1958Z-T4-chat-legacy-button-wheel-bridge-y8m2` (chat); `20261108T1945Z-T4-chat-real-cl-mouse-evidence-v9n3` (chat).
- **experiment_key:** `T4-CL-4680f5dc-a0-actionButton0-downup-press-release-same-eventTime-v1`
- **resource_key:** `T4-source-only-CL-immutable-evidence-no-Unity`
- **intended_files:** `scripts/t4_verify_cl_shared_mouse_evidence.py`, `tests/test_t4_verify_cl_shared_mouse_evidence.py`, T4-only report, experiment, event, work and this session. No T5 shared source/testpack or full game code changed.

## Live restoration and team isolation
Read owner RESTORE_AR, CHAT_AND_SCHEDULE_AR and 2026-11-08 shared lab/Arabic Portrait owner directives; most recent T4 scheduled 00:36Z, prior game-stage source success CI42518143297, current shared Mini source, T5/T1/T2/T3 concurrent Actions, CL/test and latest immutable CL mouse evidence. All meaningful T4 gameplay source-stage modifications ended; scheduled T4 at 00:36Z made no source changes. T5 owns shared APK and full build. At start latest Actions contained no running T4 heavy Unity/full game. T5/T1/T2/T3 newer commits unrelated; no force/branch reset.

## New real observed result, not hypothetical
Pinned owner CL `4680f5dc26127938e7696f932b2d9a80dc703937`, raw `test/shared-20261108-223228-464718661/events-20261108-223341-464791801.jsonl`, blob `7c337320a1593ff8d9f9fd63e55ec30ed62cd202`, summary blob `6d702c231aa95386ace9fe85b25e244a6ce8bf8c`.
- 413 original Android physical mouse callback records; 373 distinct Android callback fingerprints; 40 Activity/View duplicates.
- 13 `ACTION_DOWN` and 13 `ACTION_UP` with `actionButton=0`; **all 13/13** paired at matching eventTime/source/captured to 13 explicit LEFT `ACTION_BUTTON_PRESS` / 13 `ACTION_BUTTON_RELEASE` (actionButton=1).
- 0 inferred additional clicks, 0 unpaired ambiguous in **this exact trace**. 55 unique VSCROLL; 0 actual captured callback, capture ON/OFF, right/middle/HSCROLL evidence.
- A representative press at 326202353 and release at 326202556 includes both implicit action and explicit button events; do not double count.
- Android original `eventTime` is only source-clock correlation, not a unique globally trusted gesture/device ID; older JSONL has no deviceId.

## Engineering output
- Commit `f314754a37784a2ae79a162398d0e33cc047131f`: added fail-closed `implicit_down_up_correlation`; correlates only same eventTime+physical source+capture+unique explicit button, validates buttonState and rejects ambiguous, **never synthesizes a click or Unity PASS**.
- Commit `f535f8ac59397d8698344f0f56510034a2d0de38`: four adversarial tests for duplicated real-style edge, different clock, captured mismatch, missing time and invalid state.
- Commit `4fa6e50354c4718584f4b4fceec2d11738ac69a4`: source limitations text now reflects whether captured callback is actually present, without claiming Unity proof.
- Commit `d511887c43f178e8e0189180b75849984d34df16`: prevents regression to false "capture absent" when captured=true.
- Genuine pinned CL replay + unit CI **[42547368125](https://github.com/alwansan/raf/actions/runs/42547368125) SUCCESS** on last exact test/code commit; **13/13 Python tests**, pinned original CL SHA/blob check and real record-count+pair assertions pass. Initial [42547259000](https://github.com/alwansan/raf/actions/runs/42547259000) SUCCESS 13 controls, follow-up [42547355733](https://github.com/alwansan/raf/actions/runs/42547355733) SUCCESS. No proprietary bytecode/assets reproduced.
- Repro report `docs/T4_ANDROID_ACTION_DOWN_UP_CORRELATION_2026-11-09.md` commit `e6a2f873927b577ace1a4515f853ff0c3e5350a1`.
- Experiment `prompt/coordination/experiments/T4/20261109T0144Z-T4-chat-downup-correlation-n6q2.json` commit `02ea026453bd7de07afc099c557150e509e0d093`.
- Event `prompt/coordination/B_TEAM/events/T4/20261109T0149Z-T4-chat-android-downup-real-cl-n6q2.json` commit `53a58876699ae4594516a985c949e65f6cf5aba2`.

## Proof boundary and next-step
Only **uncaptured View/Activity real owner Mini APK 0.2.9 callback correlation** verified. No captured button route, no Unity Legacy Input delivery, no signed next Raft game XAPK, no GPU/visual source changes or Android device replay of new game code. Original latest shared Mini 0.2.13 build CI42519487402 remains appropriate; this T4 Python tool does not warrant new Mini build or modification of T4 NO_BUILD vote. Full-game INPUT-005 remains OPEN, NOT_READY 0/3.

**For next scheduled/chat T4:** re-check CL/test latest. If `T4-02` export has `capture_request=ON`, `route=captured,captured=true`, physically attempt LEFT/RIGHT/MIDDLE and V/H scroll, run updated classifier and inspect same-signed-game Unity reader consumption; otherwise improve independent safe diagnostics without changing known-good camera and no source-only claim of device fix. Preserve Raft camera, keyboard/touch, .rgd, audio, Settings and other workers. No Actions canceled or duplicated heavy game build.
