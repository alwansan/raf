# LogRaft public test signing — automatic and permanent

This is an **open-source, experimental logger**. Its owner explicitly chose a **public APK signing key** to eliminate Termux, GitHub Secrets and manual setup.

## Identity
- Keystore: `signing/lograf-public-test.p12` (PKCS#12)
- Integrity: `signing/lograf-public-test.sha256`
- Alias: `lograf-public`
- Store/key password: `LogRaftOpenSource2026` (public test password, not a secret)
- APK signing certificate SHA-256: `bdb27cfad1fd9a6ac14bd47317206ce4df462040f45ddb1fdbb66a0974043149`
- Key created once in workflow run #30 on 2026-11-01, then committed back to branch `lograf`.

## Automatic workflow
`.github/workflows/lograf-apk.yml` checks out the `lograf` branch. On its first run, if no key exists, it generates one and **commits it before building**; otherwise it reuses that exact file. Its checksum is checked before signing. The release APK is verified against the corresponding key certificate before upload, and published directly in GitHub Releases as `LogRaft-signed.apk`.

The Android package name remains `com.alwansan.lograf`. APK `versionCode` increases automatically with `GITHUB_RUN_NUMBER`, so future APKs can be installed over an older release signed by this same public key.

**The private key is published.** Anybody who clones the project can sign a spoofed APK with this identity. Users should only install releases they trust; this key must not be used for banking, credentials, commercial production, or other security-sensitive apps.

## Migration from older APKs
Builds through `lograf-21` were Android debug signed with a *different* certificate. Switching from those old APKs to the new public-test-signed version may require uninstalling **once**. Back up the existing selected-folder log recordings before removing the app. Once a stable-key APK is installed, subsequent signed releases use the same certificate and upgrade without uninstalling.

Do not replace, regenerate or rotate `lograf-public-test.p12`; doing so would break update continuity.
