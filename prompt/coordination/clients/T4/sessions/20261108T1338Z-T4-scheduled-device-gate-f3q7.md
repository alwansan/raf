# T4 scheduled — physical mouse device evidence gate (2026-11-08)

- session_id: 20261108T1338Z-T4-scheduled-device-gate-f3q7
- origin: scheduled
- resumed_from_session: 20261108T1240Z-T4-scheduled-classifier-audit-r5n8
- initial HEAD: 389825143647a7768f84020b0033e4962a915739
- scope registration commit: 924700093ca698d0fba66b174dbcedc84aa01f16
- work: prompt/coordination/work/INPUT-005/20261108T1338Z-T4-scheduled-device-gate-f3q7.json
- experiment key: INPUT-005-T4-device-gate-20261108

## Evidence checked

Owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md: phone artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 successfully entered, saved, exited and reopened local world; publishing failed separately. This is owner-confirmed for that artifact only, not a new device test. CL pinned snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 includes Nov 5 screenshots and log directories; no proof it contains later epoch telemetry. Do not reinterpret previous APK86 failures as current world behavior.

Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM CHAT_AND_SCHEDULE_AR, PROMPT_AR, OPERATING_MODEL_AR, T4 state/MEMORY, latest session, trial readiness and current classifier. T4 vote needs phone trial; T5 build coordination owns packaging and Resolution/buttons. Trial round is not unanimous and owner-direct request is independent. No duplicate native request authorized.

Live branch HEAD 389825143647a7768f84020b0033e4962a915739 at start. Recent Actions: 42485092438 success source 2ba593a; 42485049794 success and 42485049910 failure on 95e555a; latter failed at 'Audit actual Material Shader references and dummy marker controls', a graphics-team scope, not evidence of mouse regression. 42472339258 success on e1e7ac93 confirms epoch classifier source tests only. No new physical mouse Android log proven. No Actions cancelled or rerun.

## Decision and next discriminating experiment

INPUT-005 remains OPEN. Do not claim runtime mouse fix from source-only green CI. For next signed APK whose source contains epoch events, record manifest APK/OBB hashes and exact source SHA before associating CL logs. On phone capture the sequence: gameplay authored_lock -> capture_requested(epoch=N) -> relative(epoch=N) during uninterrupted movement across screen edges; Escape/menu -> release -> custom Raft cursor (not black Android system pointer); return -> new request/retry epoch and relative; focus loss and mouse disconnect -> release; keyboard controls unaffected. Run scripts/t4_classify_mouse_capture_log.py on the *new* device log; check its false-positive boundaries against timestamps and physical mouse actions. If no request, trace Unity lock intent to Android View; if request without relative, trace pointer capture callbacks and MotionEvent relative axes; if relative arrives but camera stationary, trace Input System consumption. Keep original .rgd save/load regression in same candidate.

No source runtime change, no build or phone execution this cycle; no evidence supports a safe causal patch without new input. Preserve .meta, GUID, keyboard, .rgd, audio, Settings and T5 right-side buttons/Resolution scope. Next T4 chat/scheduled session should consume this gate rather than rerun classifier CI.
