# T3 RENDER-002 — duplicate Material shader field fail-closed

- session_id: 20261108T0630Z-T3-scheduled-parser-boundary-f4c9
- origin: scheduled
- resumed_from_sessions: 20261108T0526Z-T3-scheduled-symlink-boundary-n6r2; 20261108T0427Z-T3-scheduled-duplicate-shader-guid-q8m4
- base_sha: 9c11fdf4349373573eff3cd925dc3db00e0524c6
- issue: RENDER-002 OPEN / NOT_READY
- owner phone baseline: run 42058825739, original run SHA e9c358eda01785b65e4eb14f18723da426635628; world entry/save/re-entry succeeded only, graphics not confirmed.

## New bounded finding and patch

Source review identified a fail-open case in `scripts/t3_material_shader_link_audit.py`: a Unity text .mat containing one well-formed `m_Shader` pointer and a second malformed `m_Shader` field was previously counted as resolved, because the code only counted *parseable* matches. This is ambiguous source and must not count as recovered linkage. Added an independent anchored shader-field count guard; now only exactly one field and one parseable pointer is accepted. Added a synthetic regression fixture for the duplicate-field case. Changes: source commit 8aba711d5b6708175fdca13b4c3f999ddf559bb3; test f2272d801f5f2a7f81160df00c82c145e671b219; newline fixture correction 4d3e1f323d9bb6ded3f07b0280707cdb96ced7f2.

## Evidence and limitations

Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, current owner requirements, STATUS, T_TEAM chat/schedule, operating model, prompt, trial votes, T3 historical state/memory and source/tests. Latest branch HEAD at last code read 4d3e1f323d9bb6ded3f07b0280707cdb96ced7f2. Reviewed recent Actions; did not dispatch/cancel native or CI. Local git DNS resolution to github.com failed, so the published Python unit suite was not executed; only source-level regression logic reviewed. No actual original ZIP2/CL image pixel inspection, shader recovery, Unity Editor, device run or game asset edits. The known 41 selected original Materials had authentic 227 texture slots/150 color values matched in previous CI; this does not establish Android pixels or other Materials.

## Next

Run `python3 -m unittest tests.test_t3_material_shader_link_audit` against checked-out HEAD in a runner; apply audit to full authenticated export and classify missing shader source vs true shader/material/particle alpha failure. Coordinate with T1/T2 shader and T4/T5 input/display. No new APK request; vote remains no-needs for T3 until substantive integrated graphics repair. Preserve .meta/GUID, .rgd, Settings and sound.
