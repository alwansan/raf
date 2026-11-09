# T2 scoped work — 20261109T1517Z-T2-scheduled-foam-provenance-p6k4
origin: scheduled
base_head: 8c54ce1645da1af3fc31f3fc8e2b4eac3f6b0b90
track: WATER-001
experiment_key: T2-FOAM-CFG-RECEIVER-IDENTITY-20261109
files: isolated work and session markdown only; no game assets, no shared workflow, no T3 files.
hypothesis: Mono.Cecil --selftest passing does not establish same runtime Texture identity between Foam passes. Original pass0 typed_field and pass1 typed_call_result require receiver and return CFG provenance; a branch join must yield unknown unless all incoming aliases agree.
shared_resources: none
source_evidence: owner docs/DEVICE_FEEDBACK_42058825739_AR.md, original T2 state and 20261109T1216Z session, CI42607763178 success on 3d5afd95.
scope_check: T1 FFT; T3 fire/candles/smoke/colors; T4 physical mouse; T5 resolution/packaging. No overlap.
acceptance: synthetic Cecil fixtures for (a) same field distinct receivers (b) same receiver differing field (c) call-result with branch join (d) DUP unknown; source-pinned scan with safe aggregate only. Do not mark same Texture or integrate ShaderLab without original proof.
next: inspect original-safe CI report and implement receiver-aware bounded CFG tracing in isolated analyzer with actual tests. No new CI while equivalent active.
