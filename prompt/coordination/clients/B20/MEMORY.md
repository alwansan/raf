# B20 — working memory

- Identity: B20, session 20261104T2230Z-B20-6c9a; owner-authorized branch `feature/android-native-port` only.
- Startup HEAD: `5fc5c4838247c33669bba8b67e988893f22cd28e` (2026-11-04T22:20Z). Latest actual game release `android-early-test-41812889049-1` / APK versionCode86; no newer phone evidence verified. CL review 2026-11-04 has original water pass/FFT failures and SaveGame→Steam StoreStats exception; source logs and images cited in B_TEAM/REVIEW_2026-11-04.md. Audio and Settings owner-confirmed; touch deferred.
- Read: B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, SUMMARY.md, REVIEW_2026-11-04.md, TEMPLATES.md, issues/WATER-001.json, AGENTS.md, owner requirements, prompt README/continue/status and ZIP2 provider. No original shader bytes copied, no private asset published.
- Live Actions review: latest visible branch runs 41923703800 and 41923703812 SUCCESS, no running job in first 25 latest; original B18 FFT SPIR-V validation is source/translation evidence only.
- Assigned gap WATER-001: strengthen `scripts/b49_shaderlab_pass_contract.py` water **source-only** Pass scope verification, preventing fake authored Pass tokens in non-SubShader scopes or ShaderLab malformed braces from satisfying the prebuild diagnostic. B49 prior source guard supports syntax but not GPU or originality. Check upstream test contracts before changing. Distinct from B18 bindings, B24 Foam, B30 FFT selector, B45 original Blur.
- Hypothesis: global regex `Pass\s*{` can count token outside a `SubShader`; a staged fake candidate could fool structural counts despite being invalid ShaderLab. Reject synthetically and add CI before claiming SOURCE_FIXED.
- Active work record: `prompt/coordination/work/WATER-001/B20-20261104T2230Z-B20-6c9a-shaderlab-scope.json`.
- Do not change original assets/.meta/GUID, audio, Settings, touch, Unity request or any other agent's workflow.
- Next: add strict scope controls, run tests, commit and record result; WATER-001 stays OPEN, READY 0/3.
