# T4 isolated LOCAL-005 recovery — compiled IL supersedes declaration triage

- session_id: 20261105T1043Z-T4-il-metadata-handoff
- status: paused_identity_conflict
- resumed_from_session: 20261105T0935Z-T4-declaration-ci-confirmed
- baseline_sha: 80b4724e1f745e4a9b44f33b2663c7e6701463e6
- taken_over_from: T4 original 20261104T2357Z-T4-lw01 and isolated 20261105T0935Z; B07/B14/B19/B24/B37/B50 historical evidence (attributed, not reactivated); T5 compiled IL oracle CI42012597665 (credited to T5).
- branch: feature/android-native-port only
- track: LOCAL-005

## Live evidence and hypothesis update
Read T_TEAM PROMPT_AR/README/RESTORE, OPERATING_MODEL, LEGACY_HANDOFF, SOURCES_AND_ACTIONS, TEMPLATES, migration, owner requirements, status, T4 state/MEMORY, T4 FileManager contract/classifier and tests, T5 compiled IL verifier/report. T4 original state remains active (20261104T2357Z-T4-lw01); do not overwrite state.json or MEMORY.md. Original ZIP2 DLL SHA 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e; source provider 15964ea8f246b6e076ce26b60931ee2e1a9a2385. CL main 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29. Last phone game APK86, no fresh device evidence.

At observation, branch HEAD 80b4724e1f745e4a9b44f33b2663c7e6701463e6. Actions queried: 0 queued and 0 in_progress. T5 original compiled IL metadata oracle CI42012597665 SUCCESS at 7159dba5, 11/11 controls, authenticated 3211776-byte original DLL. Crucially, unlike T4's lexical classifier, it **resolves both real original FileManager targets**: read=2 parameters/14 IL instructions/1 direct System.IO call/1 exception handler; write=1 parameter/13 IL instructions/1 direct System.IO call/1 exception handler; separate metadata tokens. Thus the earlier unresolved C# declaration parser is **not a blocker to method existence or call-edge identity**. Do not repeat the parser/ILSpy export solely to prove those methods exist. This does not establish file path semantics, durability, or phone behavior. T4 reference-context CI42012049920 succeeded; prior failed attempts remain negative evidence.

## Engineering decision
The next test must ask a *different* question: compare the original read method's two-argument call site and original write method's one-argument call site to the actual adapted FileManager implementation and platform-specific path/root/catch semantics, without publishing original source. Then request a single SHA-pinned integrated Android candidate from T5 if ready; capture original world completion marker, Load<T> catch marker, SaveGame invocation and durable .rgd create/close/relaunch/readback. A direct System.IO call in IL does not prove file path correctness or save durability. No production source, sound, Settings, touch, GUIDs, workflows, or original game assets changed. No Actions cancelled. LOCAL-005 OPEN, NOT_READY 0/3.

## Checkpoint
Read-only integration boundary identified; no new game patch justified from metadata counts alone. Next step: inspect adapted FileManager signatures/path handling and produce targeted contract comparison; fix only a demonstrated mismatch. No native APK/Unity/phone evidence.
