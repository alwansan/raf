# T5 scheduled — 2026-11-11T19:46Z

- session_id: 20261111T1946Z-T5-scheduled-q7m2
- origin: scheduled
- scope: read-only verification of existing Resolution delegate topology CI; no Unity, mouse, T4 or game source changes
- baseline: [owner device report](../../../../docs/DEVICE_FEEDBACK_42058825739_AR.md); world/save/re-entry on artifact 42058825739 is owner-confirmed, not CI-confirmed
- workflow: https://github.com/alwansan/raf/actions/runs/43081428467 ; job 130734868129 completed **success** on 2026-11-11 18:50 UTC
- immutable original ZIP2 source: 15964ea8f246b6e076ce26b60931ee2e1a9a2385; Assembly-CSharp.dll 3,211,776 bytes, original assembly SHA verified by oracle
- actual bounded graph: 42 compiled methods; 2 delegate instruction sites, both resolved; 1 unique target; 1 option-population call site; 0 option methods with delegate sites; 0 option methods reaching apply or Screen.SetResolution; 0 delegate targets reaching apply, Screen.SetResolution or PlayerPrefs write; 22 internal direct call edges, 0 unresolved internal call sites.
- **Conclusion:** tests and original IL topology gate passed; no evidence that the option population path binds a runtime dropdown callback, persists a user-selected resolution or controls Android render scale. Do not infer a proven absence of callbacks via other indirection or prefab UnityEvent wiring from this bounded graph.
- Remaining: inspect original prefab/scene serialized events and source Android Settings bridge, then design native render-scale option behind evidence. APK/OBB SHA/versionCode and LogRaft same-build performance remain unverified. Do not change T4 mouse code. No new CI launched.
- status: SOURCE_EVIDENCE_ONLY / NOT_READY 0/3.
