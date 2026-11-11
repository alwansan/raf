# T5 scheduled — APK/OBB offline manifest audit

- session_id: 20261111T2246Z-T5-scheduled-apkobb-audit-k7m2
- origin: scheduled
- base_sha: abda13b6939215c591558dd86e3e8317314f81e8
- resumed_from_sessions: prior T5 scheduled Resolution delegate topology session 2026-11-11, T5 state.json chat 20261108T2010Z; report docs/DEVICE_FEEDBACK_42058825739_AR.md
- work: prompt/coordination/work/INTEGRATION-001/20261111T2246Z-T5-scheduled-apkobb-audit-k7m2.json
- source commit: dd5cf3dabfcaf7f8cb4cbb802361aba032f220d7
- source: scripts/t5_apk_obb_manifest_audit.py
- result: Implemented a read-only offline APK/OBB audit that uses Android build-tools aapt dump badging for package and versionCode, checks main.<versionCode>.<package>.obb, emits byte counts and streaming SHA256 for both files, optionally compares OBB SHA against an independently trusted value, and optionally tests ZIP CRC. It does not extract proprietary assets. It explicitly reports APK signer verification and actual OBB resource loading as false/not proven.
- local controls: Python py_compile PASS; synthetic positive APK manifest/aapt + matching OBB exit 0 PASS; synthetic mismatched OBB name exit 1 PASS. This is synthetic tool validation, NOT verification of owner Artifact 42058825739.
- use: python3 scripts/t5_apk_obb_manifest_audit.py --apk /path/to/signed.apk --obb /path/to/main.N.package.obb --aapt /path/to/aapt --expected-obb-sha256 64_HEX
- limits: Signed APK/OBB delivery IDs 13441227298 and 13441766832 were not accessible in earlier sessions. No matching binary inputs here; therefore package version, actual OBB digest, signer certificate, device installation, resource loads and performance remain unverified. No Unity build or CI dispatch. T4 owns mouse; this script does not modify Settings, three buttons or touch.
- next: obtain actual signed APK/OBB bytes from verified delivery, run audit, separately use apksigner verify --print-certs and compare signing certificate, inspect installed versionCode, then compare LogRaft FPS p50/p95 by identical scene/settings. Continue three-button safe-area and existing Resolution integration in separate coordinated scope.
- readiness: NOT_READY; no phone PASS claimed by this session.
