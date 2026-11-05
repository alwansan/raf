# T5 — Offline completed APK and OBB pairing validator (2026-11-05)

## Why this is needed

Owner reports actual world entry, save, exit and reopening on the APK/OBB obtained from native GitHub Actions 42058825739, immutable source e9c358eda01785b65e4eb14f18723da426635628. The CL device session summaries report one OBB GUID warning in 220911-559 and two in 230108-327. The observed warnings alone cannot establish corrupt OBB bytes, a mismatch between APK and OBB, or missing Unity assets. Native reconstruct/sign/package succeeded; public GitHub Release creation failed HTTP 403. Retained full delivery artifact 13441227298 expires 2026-11-06T18:19:05Z, and signed checkpoint 13441766832 expires 2026-11-07T18:18:17Z. These artifact ZIP SHA256 declarations are **not** the hashes of the two individually packaged game files.

## Concrete new integrity boundary

New script: scripts/t5_verify_apk_obb_pair.py.

It accepts the *reassembled, complete* Raft-Android-Test.apk and matching main.VERSION.com.alwansan.raft.androidtest.obb plus delivery.json. It invokes aapt dump badging on the provided actual APK (without invoking a shell or trusting a separately supplied badging text), and validates the package and versionCode against the delivery manifest and the OBB filename. It streams both actual files through SHA256 and checks sizes against the two corresponding logical file records. The tool also checks all three APK/OBB/XAPK declared logical records and their transport part-size sums, validates ZIP central directory safety/uniqueness and expected Unity asset presence, and checks basic APK manifest/DEX/ARM64 IL2CPP header structure. No raw game bytes are extracted, uploaded or emitted.

Example, with native Android SDK build-tools aapt installed, and **after** assembling the parts through the project's reassemble.py:

    python3 scripts/t5_verify_apk_obb_pair.py \
      --delivery /private/raft/delivery.json \
      --apk /private/raft/Raft-Android-Test.apk \
      --obb /private/raft/main.86.com.alwansan.raft.androidtest.obb

For a different versionCode, use the exact OBB name declared in its own delivery.json. A pass means both files match **that local manifest**. The manifest should independently be authenticated to the immutable source/release; if both manifest and bytes are maliciously replaced together, this tool alone cannot detect that.

## Reproducible verification

Source-free tests: tests/test_t5_verify_apk_obb_pair.py (17 cases), narrow .github/workflows/raft-t5-apk-obb-pair.yml, no Unity, no game archive download. Tests construct synthetic valid ZIPs, modify full-file bytes, change aapt identity, substitute OBB version, tamper the manifest/part sums, strip APK core, corrupt ZIP format, add traversal/duplicate archive entries or use symlinks.

The workflow validates the code/negative controls, **not** the real signed delivery. This distinction is essential.

## Explicit limitations and next step

This tool does NOT verify cryptographic APK v2/v3 signature, trusted source of delivery.json, XAPK actual file bytes, OBB installation path/Android 15 mount, OBB's internal Unity GUID, ZIP local payload CRC for all members, original shader/FFT authenticity, rendering, performance or gameplay. Actual owner phone testing of the 42058825739 artifact is a separate positive observation. An OBB GUID warning may persist even after pair hashes pass, in which case investigate the exact Unity log line and expected GUID using actual signed package and same-scene logs. Preserve the 6GB delivery artifact before its expiry if authorized; do not rerun full Unity or claim release publication from synthetic tests.

T5 scheduled right-side diagnostic UI (AndroidTouchUiPanel.cs) is untouched. T1/T2 water, T3 graphics and T4 mouse/world areas are untouched. Game remains NOT_READY 0/3; no fake flags, no unverified asset/GUID edits.
