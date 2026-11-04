# B04 — session 20261104T2102Z-B04-7c20

Scope: independent RENDER-002 original project Linear color-space parity before Unity import. B44 addresses material values, B46 exported textures, B01/B45/B47/B48/B49 water/FFT/pass guards, B50 local StoreStats/Cheat. No overlap or claimed device resolution.

Initial HEAD 09480c40be3ccf65c0a8661142c6d5f78e519b39. Original source zip2 commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385. Original globalgamemanagers: 1914356 bytes SHA256 6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5; W2 verified PlayerSettings.m_ActiveColorSpace=1 (Linear), color gamuts [0]. Source: docs/W2_COLOR_SPACE_SETTINGS_2026-11-03.md.

Read B_TEAM PROMPT_AR, README, OPERATING_MODEL, SOURCES_AND_ACTIONS, TEMPLATES, SUMMARY, REVIEW, RESTORE, AGENTS, owner requirements, prompt/README, CONTINUE, STATUS current sections, ZIP2_SOURCE_PROVIDER, W2 reports. Latest actual Android release run 41812889049, APK versionCode86, source d181ee715...; no newer device proof. CL segment3 StoreStats issue reviewed from B_TEAM REVIEW. Live Action 41911830635 in progress (LOCAL-005), do not cancel or duplicate. LogRaft release is separate.

Hypothesis: project Gamma vs original Linear is a possible pale-color cause; not proven. Plan: SHA-pin original settings, guarded ProjectSettings YAML patch with idempotence and fail-closed behavior, isolated test/CI, then integrate to native workflow if appropriate, no new heavy build. Never modify original data, GUID, sound, Settings UI, deferred touch or other agents' files. Last step: register, then implement and test.
