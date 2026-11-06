# T4 scheduled — owner-direct Unity failure provenance and mouse fix handoff

- session_id: `20261106T2035Z-T4-scheduled-native-failure-h7q2`
- origin: scheduled
- issue_id: INPUT-005 / LOCAL-005
- status: completed (read-only evidence verification)
- base_sha: `ca21657f1d36cb4b3e07b394f56acd4d2c38200f`
- work reservation commit: `e927858c56e53c50413b2ae323497a69edc1640e`
- resumed_from: `20261106T1943Z-T4-scheduled-r6k2`, `20261106T2014Z-T4-chat-editor-mouse-symbol-k3m9`.
- scope: no shared runtime code or Unity build. Compare owner-direct run and T4 independently validated Editor symbol fix.
- **Verified current result:** [owner-direct run 42281310905](https://github.com/alwansan/raf/actions/runs/42281310905) completed **failure** at immutable `d692400115c36c4839fa4f4954e5f6ed1c60d413`; native-request gate and license passed, `reconstruct` failed during Unity Editor 2021.3.45f2 Android import and compile. Delivery-result failed as a consequence, publish skipped. No new signed APK/OBB/XAPK from this run.
- **Resolved source blocker, not native validation:** T4 chat traced ten CS0234 errors to `AndroidPhysicalMouseCapture` being hidden from UNITY_EDITOR while original mouse-axis callsites were unconditional. [Fix f554e8b6](https://github.com/alwansan/raf/commit/f554e8b6757e46aa037603ed592a04acc2bf7a61) provides editor-only API-compatible fallback, preserves Android JNI capture; [CI42287041110](https://github.com/alwansan/raf/actions/runs/42287041110) passed actual Unity2021 managed ABI checks and 48 mouse controls. Owner-direct run predates fix; cannot retroactively claim success.
- **Fresh Actions snapshot:** HEAD `ca21657f1d36cb4b3e07b394f56acd4d2c38200f` before work reservation. Run `42289238865` in_progress at snapshot on `177a57342dc6197e2f5dceee940c9bb0bec34c6f`; several more recent source checks failed, including `42289624213`. Do not attribute them to Unity build without job review. No duplicate CI or native dispatch.
- **Owner phone evidence retained:** [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) on older `e9c358eda01785b65e4eb14f18723da426635628` is owner-confirmed world entry/save/exit/reopen. [Feedback](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md) CL sessions and screenshots support that bounded report, not new mouse or OBB acceptance. Original .rgd compatibility and keyboard/audio/Settings untouched.
- **Trial:** `trial-20261106-r1` remains T4 `يحتاج` and other four `لا يحتاج`; owner-direct request is a separate exception, not 5/5. Full readiness NOT_READY 0/3.
- **Files changed this cycle:** independent work JSON and this session only. No original source, GUID, game files, assets, CL or shared vote modified.
- **Next:** T5 independently decides whether and when a single later Unity build is authorized. On any new build inspect first actual error and artifact provenance; if signed candidate emerges, phone-test relative physical mouse camera rotation, Raft cursor, three mouse buttons, keyboard, focus release, Resolution, and original same-world .rgd save/exit/reopen. Keep INPUT-005/LOCAL-005 open. Do not repeat 42287041110.
