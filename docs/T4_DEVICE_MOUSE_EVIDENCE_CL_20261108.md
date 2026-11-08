# T4 — REAL Android mouse evidence from owner CL/test export
**8 Nov 2026 | session `20261108-223228-464718661` | INPUT-005 OPEN | device callback proof ≠ Unity input/gameplay proof**

## Precise immutable external evidence
Owner published test logs: `https://github.com/alwansan/CL/tree/main/test`. This report pins CL read-only commit `4680f5dc26127938e7696f932b2d9a80dc703937`, not mutable `main`, and the following exact Git blobs:
- Raw child manual mouse view trace: `test/shared-20261108-223228-464718661/events-20261108-223341-464791801.jsonl`, Git blob `7c337320a1593ff8d9f9fd63e55ec30ed62cd202`, **183,764 bytes**, **422 records**, 413 Android `input` callbacks.
- Team parent summary: `test/shared-20261108-223228-464718661/summary-20261108-223228-464718661.json`, Git blob `6d702c231aa95386ace9fe85b25e244a6ce8bf8c`.
- Team app provenance from summary: `com.alwansan.raft.lab.shared` v`0.2.9-shared`, embedded source SHA `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8`, pack SHA256 `6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f`, phone Xiaomi 23013PC75G API35.
- Source validator: `scripts/t4_verify_cl_shared_mouse_evidence.py`, adversarial synthetic tests `tests/test_t4_verify_cl_shared_mouse_evidence.py`, workflow `.github/workflows/raft-t4-cl-shared-mouse-evidence.yml`. [CI42516377494](https://github.com/alwansan/raf/actions/runs/42516377494) **SUCCESS** at exact source `a44d5257a9700f23ae31afab2a1c2800421f17c6`; 9/9 Python tests and original owner Git blob assertions.

## Actual device findings (CL logs, no invented actions)
| Measurement from owner raw JSONL | Count |
|---|---:|
| Android physical mouse callbacks `SOURCE_MOUSE=0x2002` | 413 |
| Uniquely identified MotionEvent records after Activity/View route de-duplication | **373** |
| Duplicate Activity/View records identified | **40** |
| Raw `ACTION_BUTTON_PRESS` / `ACTION_BUTTON_RELEASE` | 15 / 15 |
| Unique LEFT `actionButton=0x1` press / release | **13 / 13** |
| Unique RIGHT `actionButton=0x2` or MIDDLE `0x4` press / release | **0 / 0** |
| Raw `ACTION_SCROLL` | 87 |
| Unique `ACTION_SCROLL` with negative / positive `AXIS_VSCROLL` | **36 / 19** |
| Unique nonzero `AXIS_HSCROLL` | **0** |
| `capture_request=ON` or `capture_request=OFF` | **0 / 0** |
| Events with `captured=true` or `route=captured` | **0 / 0** |

The same physical `MotionEvent` is often emitted both by `activity_generic` and `view_generic` with **different local x/y coordinates**, so the replay deduplicates by `eventTime/action/source/buttonState/actionButton/vscroll/hscroll/captured` but not x/y. The count of unique MotionEvent fingerprints **is not** a count of user's wheel gestures nor a physical click reliability rate.

Owner ran `test_begin=T4-01` twice then `T4-02`, `T4-03`, but **no `capture_request`**. Therefore these runs establish **uncaptured Android LEFT and vertical wheel callbacks**, not that capture ON was actually attempted, nor any right/middle/horizontal hardware failure. Right/middle/horizontal absence cannot be called a driver defect without per-case attempted-input evidence.

**False-readiness guard:** Parent summary marks `T4-09=EVIDENCE_READY` (observed `physical_button_events=58 scroll_events=87`); the child driver marks this when it sees *any* mouse button or wheel event. This is **not evidence that T4-09 compared a physical-mouse action inside Raft**. The count 58 is also an undifferentiated sum of ACTION_DOWN/UP + BUTTON_PRESS/RELEASE across multiple callback routes, and 87 contains repeated routing. Thus `T4-09` **is not accepted**; `T4-01..08` remain NEEDS_INPUT in summary. `T5-01=PASS` confirms lab package/signature only, not gameplay.

## Actionable device gate (existing ONE team APK; no new build)
1. In **Raft Team Lab** select **IN-APP REQUESTS → T4-02 Captured LEFT mouse → RUN selected test**. In new mini T4 screen, use finger on **Capture ON**, then move physical mouse **inside blue INPUT PAD**, press/release LEFT, observe `route=captured` and `captured=true`; try RIGHT, MIDDLE and wheel while capture remains ON. Use finger **Capture OFF** and repeat LEFT+wheel. Then **RETURN TO TEAM LAB — save observed mouse evidence**, enter precise observation, Export logs.
2. Explicitly verify `capture_request ON` log; if pressed but all next events stay `captured=false`, this is a **captured pointer acquisition/ownership/focus** question, not a Unity Legacy mapping verdict. If captured events arrive but Raft still fails, next check exact **new game candidate** with T4 `physical_mouse_captured_action_callbacks` log support and original game Input.GetMouseButton* / `Input.mouseScrollDelta` mapped under same APK SHA.
3. Test `T4-03` RIGHT, `T4-04` MIDDLE, `T4-05` wheel two directions and `T4-06` horizontal (NOT_SUPPORTED if mouse has no tilt wheel), each using capture ON and OFF where specified. Do not turn an unattempted event into a FAIL. For `T4-09` compare in real full Raft separately; the mini cannot observe Raft Unity Input.
4. Export `events-*.jsonl` and `summary-*.json` under `Download/Games/cl/test/shared-<session>/`; user already uploads to `alwansan/CL/tree/main/test` so workers can read without extra attachments.

## Controlled next engineering change
No direct Unity game source change should be selected from an **uncaptured-only** mouse trace. Preserve current successful physical camera motion under Pointer Capture; preserve touch/virtual LEFT, keyboard, saved .rgd, world entry and audio. Original Raft CLR census [42512688990](https://github.com/alwansan/raf/actions/runs/42512688990) separately proved static direct Legacy call sites (4 `Input.GetMouseButtonDown`, 6 held, 2 Up, 6 `Mouse ScrollWheel` Axis, 2 `Input.mouseScrollDelta`) but is **not proof of actual runtime delivery**. Future bridge must prevent duplicate ACTION_DOWN / BUTTON_PRESS, stale capture and Android system UI regressions.

**Status:** INPUT-005 OPEN; Unity actual Mouse0/Mouse1/Mouse2 and wheel NOT_DEVICE_PROVEN, no unified mini builder request by T4, no Raft XAPK build, game NOT_READY 0/3.
