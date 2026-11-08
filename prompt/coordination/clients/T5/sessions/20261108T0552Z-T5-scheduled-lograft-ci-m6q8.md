# T5 scheduled — LogRaft provenance CI execution

- session_id: 20261108T0552Z-T5-scheduled-lograft-ci-m6q8
- origin: scheduled
- base HEAD: 648358631cf2287a8c464841d0d28ae7097048ab
- scope: prompt/coordination/work/INTEGRATION-001/20261108T0552Z-T5-scheduled-lograft-ci-m6q8.json
- scope commit: 382306f4172602e803c84b9ffc341afa661d083b
- production/CI commit: aa2d6c3c84418847e93e970d68299a66490e39e7
- workflow: .github/workflows/raft-t5-unity-interval-regression.yml
- CI: https://github.com/alwansan/raf/actions/runs/42452502335 (queued at first verification; **waiting_ci**, not PASS)
- Change: run published LogRaft Python unit tests and py_compile in the existing T5 source-only workflow, with an independent synthetic CLI test proving valid native Raft estimate accepted, wrong package rejected, unverified telemetry rejected, legacy flat projection retained. Workflow paths include the new parser and test files, without changing Unity or shared resources.
- Prior published fixes: 068e535115d9c161e36233942f661f0de375bda4 (quality), d58d981bf0dd7af46bdf419b6e55cdf7d3da9512 (package), original owner CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- Limits: synthetic source-only regression; no direct phone FPS, scene attribution, installed APK/OBB cryptographic identity, right-button/Resolution or Unity test. SurfaceFlinger estimate is not Unity FPS.
- Owner artifact 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 proves world/save/reopen on that phone trial only.
- Concurrent HEAD checked after workflow commit: aa2d6c3c84418847e93e970d68299a66490e39e7; no overlapping file writes observed. T4 owns physical mouse files. Trial vote 5/5 not achieved; no native build dispatched.
- Next: inspect CI42452502335; if failing fix exact regression; if passing analyze pinned CL original rows and APK/OBB attestation, then return to right buttons and Resolution after checking current scopes.
- Full game readiness: NOT_READY 0/3.
