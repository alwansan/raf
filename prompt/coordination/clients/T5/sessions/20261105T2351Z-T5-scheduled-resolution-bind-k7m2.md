# T5 scheduled — Resolution owner binding audit

- session_id: 20261105T2351Z-T5-scheduled-resolution-bind-k7m2
- origin: scheduled
- base_sha: 188839a8bbf35cb96e71971935284206666ae06d
- plan_commit: e403464dc3b8d21bc730f24495c658a2618318a3
- resumed_from_sessions: T5 scheduled 2026-11-05 Resolution policy review; T5 chat signed APK/OBB and OBB GUID investigations (see prompt/STATUS.md)
- scope: INTEGRATION-001, read-only cross-check of original Settings ownership and existing probes; no shared Unity resource, no T4 mouse files.

## Evidence and discriminating result

Owner phone feedback docs/DEVICE_FEEDBACK_42058825739_AR.md establishes successful world/save/exit/reopen on source e9c358eda01785b65e4eb14f18723da426635628; FPS samples are sparse and not GPU timings. Three right-side buttons are already source-integrated; no duplication. Original APK/OBB signed pair and optional patch GUID warning attribution have already been verified in CI42117471172 and CI42119428667; no 6GB repeat.

Read the current original-source display audit and scripts/probe_settings_dynamic_reachability.py, probe_a2_settings_owner_links.py, probe_a2_settings_metadata_contract.py. **New integration distinction:** A2 probes target the *Settings.cs* MonoScript (pinned SHA904c52b337fe951f711e2efc15bfafc4fc77f2a8d2cc9c5bee2f7d14075103ad) and scene serialized pointer/FieldDef candidates, whereas the actual desktop resolution mutation is in *GraphicsSettingsBox.cs* (pinned SHAe1854d74adbbe0565b586ec749f7de2cc73e3f97f59c388934a3faa0defc9300). Thus A2 field/scene matches **cannot establish** GraphicsSettingsBox dropdown callback or persistence without an explicit typed owner link. The existing dynamic-reachability script masks literals and scans qualified references only; it expressly cannot establish indirect callbacks or reflection. Treating either as a persisted resolution selector would be an unjustified inference.

The original DynamicResolution.cs pinned SHA69f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc calls ResizeBuffers, but its two factors are not shown numerically asymmetric. Do not force scale or modify working Settings until the original GraphicsSettingsBox dropdown option construction, event subscription, preference save/load and Android early return are mapped in a private source/IL inspection. Output method/token relationships only, not proprietary source.

## Execution and limits

- Source/API-only read and independent analysis; no new original DLL decompilation or actual device/LogRaft capture in this run. No runtime patch, no Unity, no Actions dispatch, no cancellation, no raw assets or secrets.
- Latest observed branch HEAD 188839a8bbf35cb96e71971935284206666ae06d (T3). Latest sampled T3 CI42130529677 completed SUCCESS, but not a Resolution test. Do not claim readiness; NOT_READY 0/3.
- Next: private original IL method-call edge probe scoped to GraphicsSettingsBox option creation/selection/persistence with SHA pin and negative fixtures for labels vs actual callbacks. Then patch existing Android Settings adapter only if a real persisted scale control can be bound safely, with equal-axis aspect and no physical mode switch. Independently profile p50/p95 and memory/I/O from matched phone sessions after confirming binary identity.
