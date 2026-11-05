# T4 — independent LOCAL-005 platform regression triage

session_id: 20261105T1142Z-T4-automation-platform-regression-triage
status: paused_identity_conflict
resumed_from_session: 20261105T1121Z-T4-managed-stream
baseline_sha: 3476c75ee4cd8274b9ccada391c673c8d11d95db (branch HEAD at initial read; concurrent T3/T2/T4 commits advanced branch during this inspection)
taken_over_from: T4 original managed stream CI42020039305; T4 original compiled FileManager IO CI42019696138; B07/B14/B19/B24/B37/B50 historical contributions (no restart)
plan: T4-LOCAL-005-platform-regression-readonly-gate — inspect live Actions before any native build or production edit, separate source regression from Android world/device evidence.

## Fresh independent evidence
- At initial GitHub Actions query, run 42020924863 at SHA 92b3e28e989708b1779a6996866dc50cb455550e completed FAILURE in 'Raft Android offline platform adapter - build and test'. Job 127223188005 passed netstandard2.1 original offline Android compatibility compilation and numerous source checks, but **'Run storage, identity and offline-session smoke tests' failed**; later symlink guard and summary skipped. The workflow job-step metadata does not expose the failure assertion or stderr, so do not attribute it to FileManager, Steam or world completion without logs.
- Same workflow at previous SHA 479935efc870598ec6c36139738615b1cc178934 run 42020751210 SUCCESS. Therefore the current failure is a new platform smoke regression or transient test/environment issue, not proof of Android world failure. Investigate failing step logs and diff between those exact SHAs before patching.
- Independent original T4 real managed stream test 42020039305 SUCCESS at SHA f94a1d27210b9aa3736d113bc104d43168e51004; original disposable .rgd-suffixed stream bytes roundtripped with File.Create/File.Open, but not BinaryFormatter/Unity/IL2CPP or persistent device .rgd. No need to repeat without a new hypothesis.
- Latest queried Actions first 12 runs had no queued/in_progress; query is a snapshot, not guarantee against concurrent jobs. Latest queried releases were LogRaft, not a new Raft Android APK.

## Boundaries and next action
No source modifications, no native build, no Actions canceled, no source pins/GUID/.rgd/audio/Settings/touch edits. Parent T4 state and MEMORY left untouched because separate T4 sessions may still be active. Need full failing platform smoke test log (run42020924863, job127223188005) and exact commit diff; coordinate with T5 who owns integration before remediation. Then single coordinated current native candidate and actual offline create/play/save/quit/relaunch/load acceptance on device; LOCAL-005 OPEN NOT_READY 0/3. This file records evidence, not a successful fix or device proof.
