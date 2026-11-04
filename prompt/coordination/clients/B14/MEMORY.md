# B14 engineering memory

Session: `20261104T2131Z-B14-a71c`; enrolled 2026-11-04 21:31 UTC, no earlier B14 state found. Writing only `feature/android-native-port`.

Read live owner directions and B-team PROMPT_AR, README, OPERATING_MODEL, SOURCES_AND_ACTIONS, REVIEW, TEMPLATES, AGENTS, ZIP2 provider, current requirements, and current status; inspected the current WATER-001, RENDER-002, LOCAL-005 issues and active client scopes. Initial HEAD `f8028d15b2401d1fd8c73b2316e5bf76fef88eae`. Latest observed game release: Raft APK86 from run 41812889049, source d181ee7152580f49ee0b41dfd05fa2bfdacfafe5; not the later source-only fixes. CL snapshot `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29` contains documented failed Steam stats SaveGame and water pass/kernel errors.

Scope: WATER-001, independent source-integrity repair. `scripts/verify_water_render_contract.py` uses `.is_dir()` for Assets and `.is_file()` for shader sidecar .meta, accepting symlink targets; compute checks sidecar links but no ancestor guard. Hypothesis: linked path can be wrongly counted as an original-source candidate; reject redirects without rewriting assets, shader programs, originals, .meta GUID or production readiness flags.

Adjacent work: B49 per-pass program structure; B47 entrypoints; B48 numeric kernel identity; B06 capability/dispatch; B07/B24/B50 world path; B02/B05/B11 render color. Do not duplicate. Sound/Settings owner-confirmed, touch deferred. ZIP2 original source provider pinned `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; no asset acquisition required.

Planned test: fixture using actual structural gate plus symlinked Assets, shader .meta and ancestor directories; reject redirected inputs; ensure valid regular fixture still works. Structural source check ONLY, not original shader identities, Unity/Adreno or device validation. WATER/RENDER/LOCAL open, NOT_READY 0/3.

## Checkpoint 2026-11-04T21:39:01.943Z
Water provenance scope integrated at cfb97bf; new tests 4e0ce04. Actual preflight 41917493634 SUCCESS, job 126880924437: 10/10 tests including all five new path controls. Source-only validator; not authentic water/FFT pixel proof. WATER-001 OPEN, NOT_READY 0/3. Next independent scope considered: check project/backup redirect protection in SaveAndLoad stage, not duplicate B50's SteamStats repair.
