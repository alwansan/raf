# T2 — Foam source/report alias isolation (chat)

- session_id: `20261109T1854Z-T2-chat-foam-report-alias-b8e7`
- origin: `chat`
- started_utc: `2026-11-09T18:54Z`
- base_sha: `965afcc1710e62ffa90d159c0516efc72e4214a7`
- resumed_from_sessions: `20261109T1616Z-T2-scheduled-stage-key-guard-v7q2`, `20261109T1528Z-T2-scheduled-resource-report-guard-k8m2`, `20261109T1517Z-T2-scheduled-foam-provenance-p6k4`.
- scope_record: `prompt/coordination/work/WATER-001/20261109T1854Z-T2-chat-foam-report-alias-b8e7.json` (registered before edits, commit `fcb145400f5bf5a6d71b3e33e28f810188ab8331`).
- issue: `WATER-001`; experiment_key: `T2_WATER001_foam_resource_report_copy_isolation_py312_test_42664209077`.

## Live evidence and non-overlap

On initial inspection feature/android-native-port HEAD was `965afcc`. Latest T2 scheduled stage-key guard had only source-level claims. Initial Actions list showed T2 authenticated Foam `42664209077` failure (22 tests, 4 errors); earlier `42664186862` had succeeded and `42673027759` failure had no jobs returned by connector. T1/T3/T4/T5 work was kept untouched; no game/Unity/mini-app CI dispatched manually. Latest OWNER requirements preserve Android15 shared Arabic portrait lab, use CL/test for phone evidence and keep full XAPK 5/5 gate. No current owner phone-water acceptance exists; earlier game world entry/save/reentry is separate evidence.

## Reproduced mechanism and engineering change

[CI42664209077](https://github.com/alwansan/raf/actions/runs/42664209077) failed four subtests in `test_tampered_source_table_types_and_extra_fields_fail_closed`: after mutating `original_numeric_table_rows`, subsequent `combine(profile, resources)` raised `ValueError("Unsupported source descriptor table rows")` *before* reaching the intended report validator. `combine()` set `original_numeric_table_rows = original["table_rows"]`, so the report shared the original mutable dictionary. The existing test previously created its own temporary copy to hide this alias.

- Commit `7b4874874691b8c07ac2841f56623367ba0e4fa5`: `scripts/t2_foam_resource_abi.py` now copies the validated primitive count dictionary with `dict(original["table_rows"])` when assembling a report.
- Commit `63efef7bf925f1222783163fce32aef56695ff94`: `tests/test_t2_foam_resource_abi.py` removes the workaround copy so the existing malformed-report subtests directly exercise production isolation. New `test_report_isolation_from_original_source_profiles` checks an invalid mutated report is rejected, its original authenticated source profile is unchanged, and a fresh report from the same profile can pass again.
- No original game asset, private shader, package, .meta/GUID, audio, Settings, mouse, unified APK/pack, full-game request, or another worker's source modified.

## CI and bounded outcome

The workflow's existing path-filter auto-triggered two commits; no additional manual dispatch or cancellation:
- [CI42678552250](https://github.com/alwansan/raf/actions/runs/42678552250) — intermediate source-only fix, in_progress when checked.
- [CI42678582388](https://github.com/alwansan/raf/actions/runs/42678582388) — regression test at `63efef7b`, in_progress when checked. **This is the authoritative test of the combined patch**, not the prior run.

Source change and regression published via optimistic blob SHA. **Do not claim PASS before CI completion**. The workflow also uses SHA-pinned private authenticated Foam source and safe aggregate artifacts, so review failures and avoid private logs. This fixes report reproducibility, **not** Foam texture→sampler identity, CB0 upload, original ShaderLab render parity, Unity import, phone water/FFT/color pixels, or final game readiness. WATER-001 remains OPEN / full game NOT_READY 0/3.

## Next handoff for scheduled T2

1. Check final run `42678582388` and its source-free adversarial step, then authenticated private source steps and artifact cleanup, recording exact conclusion and failure location. If failure, fetch the failing job log; do not rerun blindly.
2. If green, keep the report isolation as a verified guard. Continue original Foam cross-pass instance binding and CB0/ShaderLab evidence independently of T1 FFT/T3 material work; no new full Unity or Mini build without respective gates.
3. Update this session's own file, or append a separate new session from the scheduler; do not overwrite other sessions. Honor CL/test phone evidence and device acceptance limits.

## Verified final CI result — 2026-11-09T18:58Z

- CI `42678552250`: **completed/success**, all member ABI, resource ABI, authentic source verification, texture identity and cleanup steps successful.
- CI `42678582388`: **completed/success**, source commit `63efef7bf925f1222783163fce32aef56695ff94`, job `129366587680`.
- Final logs show **20 member + 23 resource + 20 texture** source-free Python tests, all OK, **0 fail/error**. Original source SHA pin stage reported **115,978,112 bytes, LFS false**. Original resource safe status `original_foam_resource_interface_observed` / four stages / six original descriptor rows / 12 translated non-CB descriptor rows. Texture literal identity audit had `literal_name_matches=0` (do not infer identity equivalence). Private cleanup and safe artifact publishing steps passed.
- The observed alias regression is repaired and CI-verified. WATER-001 remains open for real ShaderLab, source texture/sampler binding, CB0, Unity and Android water pixels. No device PASS or full XAPK build is implied.
- The work record for this isolated task may be marked completed; the broader WATER-001 issue remains OPEN.
