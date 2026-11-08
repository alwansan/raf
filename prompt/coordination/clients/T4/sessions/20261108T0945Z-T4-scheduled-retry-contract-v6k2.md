# T4 — Retry telemetry CI regression contract repair

session_id: 20261108T0945Z-T4-scheduled-retry-contract-v6k2
origin: scheduled
branch: feature/android-native-port

## Owner/device evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner-confirmed world enter/save/exit/reopen on artifact run 42058825739 is retained, despite package publication failure. CL immutable snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 shows native black pointer and edge system bars; no fresh device confirmation of mouse fix. T5 owns right-side buttons, Resolution, and delivery. Keyboard, original .rgd, audio and Settings remain untouched.

## Live evidence
Starting HEAD 4450a5bb58f0251083762455d3e44761fe9f100b. T4 classifier CI [42463928346](https://github.com/alwansan/raf/actions/runs/42463928346) FAILED on source 2bcb9bc, whereas bridge [42463928344](https://github.com/alwansan/raf/actions/runs/42463928344) SUCCESS. Read failure log job 128678984206: 19 classifier tests passed, retry telemetry 3/4 passed; test_retries_are_power_of_two_throttled expected old source text `attempt > 1 && (attempt & (attempt - 1)) == 0`. New production code uses `if (attempt == 1)` then `else if ((attempt & (attempt - 1)) == 0)`, equivalent for integer attempts >=1, and now includes epoch. This is a stale source-contract assertion, not proof of an Android runtime defect.

## Scoped change
Work record: prompt/coordination/work/INPUT-005/T4-20261108T0945Z-scheduled-retry-contract-ci-failure-v6k2.json, scope commit 1001920465b429e480389cab0267beafb4a6ab1b. Implementation commit 08a3f0a92cfce05ff1f30e592e7ad8f29252898c modifies only tests/test_t4_mouse_retry_telemetry_contract.py: asserts first-attempt branch and power-of-two else-if branch, preserves expected sequence [2,4,8,16,32,64,128,256,512]. No Unity runtime, JNI, mouse behavior, keyboard, save, meta, or content changed. No equivalent CI dispatched manually.

## Limits and next
Verify a new CI run at or after 08a3f0a containing updated test; source-only regression cannot prove physical mouse capture or Raft cursor on phone. Then inspect first-device log with request/retry/relative epoch and focus/release events, test edge movement and Escape/menu/reentry while preserving keyboard and world .rgd. INPUT-005 OPEN; LOCAL-005 phone-success scenario preserved but other issues open. Do not claim READY or device mouse success.
