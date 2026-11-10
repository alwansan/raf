# T4 scheduled session 20261110T2336Z-T4-scheduled-ci-result-m8q2

# T4 INPUT-005 — CI evidence / 20261110T2336Z-T4-scheduled-ci-result-m8q2
origin=scheduled
base_head=21d668e76e1d9605fc5dcf3b6e0ca77b18711be8
scope=CI outcome verification only; no Android/Unity source modification
files=prompt/coordination/clients/T4/work/INPUT-005/20261110T2336Z-T4-scheduled-ci-result-m8q2.md; prompt/coordination/clients/T4/sessions/20261110T2336Z-T4-scheduled-ci-result-m8q2.md
hypothesis=latest T4 boundary parser regression is still awaiting validation
finding=run 42916987581 completed success for head 712500d40ca0950ac6079e14ef05710d0673611c at 2026-11-10T22:42:18Z. This supersedes previous waiting_ci; does not prove Android mouse button behavior.
shared_resource=none; no duplicate CI run.
owner_device=artifact 42058825739 world create/save/reload confirmed on phone; preserve .rgd, keyboard, audio, Settings. Mouse camera moves but clicks/wheel not confirmed.
next=instrument native Android MotionEvent buttons/axes and Unity Mouse0/1/2 + scroll with same session ID, route to Raft; coordinate T5 mini-lab; keep INPUT-005 open.

Evidence: https://github.com/alwansan/raf/actions/runs/42916987581
Prior session: 20261110T2242Z-T4-scheduled-b4k9.md
Result: source-only tests PASS; no signed device proof; no new CI launched.
