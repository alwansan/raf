# T4 isolated LOCAL-005 — parser escape audit

session_id: 20261105T0744Z-T4-parser-escape-audit
status: paused_identity_conflict
resumed_from_session: 20261105T0635Z-T4-filemanager-signature-classification
baseline_sha: 7142c6bd0e4a7659eb97da3521aedff5fbb188d8
taken_over_from: T4 20261105T0635Z isolated parser work; original T4 20261104T2357Z active; B07/B14/B19/B24/B37/B50 credited only.

Plan before edits: inspect actual regex escapes in isolated T4 classifier and eight synthetic tests, repair incorrect double-escaped Python raw regex and test newline fixtures if confirmed; run tests or record exact inability; no production/game/Unity changes. Preserve active T4 state/MEMORY. Latest GitHub branch head and Actions reviewed, no in_progress jobs at check; APK86 remains last demonstrated phone candidate. LOCAL-005 OPEN, NOT_READY 0/3.

## Implemented and evidence

Confirmed double escaping in the isolated diagnostic: Python raw regex patterns used literal `\\b`, `\\s`, `\\w` and newline fixture strings used literal `\\n`, so intended word boundaries/newlines were not represented. Corrected the classifier in commit `21b6a089a01b6c1bc670a69411d28b31b236161e` and the eight synthetic fixtures in `eeea61c2db4fa25cca6b3cac8c374edf15f9b850`. Exact source/test paths only; no production instrumentation changed. These commits correct a source-level defect, but tests are **not run**: local runtime has no network access to clone dependencies and no CI dispatch was initiated. Avoid claiming 8/8 pass. An independent test run must check declaration-vs-call false positives, especially access-modifier lookbehind and method tail classification. Current active original T4 state/MEMORY left untouched due identity conflict. No native build, phone or `.rgd` acceptance. Next step: execute `python -m unittest tests.test_t4_filemanager_declaration_shapes` in repo checkout, fix failures, then SHA-pin original private FileManager read-only classification; LOCAL-005 OPEN / NOT_READY 0/3.
