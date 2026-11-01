# LogRaft — stable test APK signing (one-time)
This repository deliberately contains **no private signing material**. A public signing key would let anyone publish a malicious APK signed as LogRaft. We use two GitHub Actions Secrets to keep signatures stable across runs.

Identity created for LogRaft on 2026-11-01:
- keystore type PKCS12, alias `lograf-update`, validity to 2054-03-19
- SHA256 keystore file = `de90c4500d3bbb1336b54891952f90500dfed6efdce4e68388280eb1a2e462a3`
- signing certificate SHA256 = `B2:6A:8C:17:02:90:E4:DC:F3:3C:8E:B0:57:D8:71:23:95:83:39:D5:2D:4A:59:EC:8E:1A:72:94:B5:14:27:B8`.
- Back up the P12 securely. Losing it means a new signing identity and app uninstall.

## Activate on GitHub from Android Termux (one-time)
1. Save the owner-provided `LogRaft-Update-Signing-Key.p12` securely on your phone.
2. In Termux, if needed: `pkg install gh coreutils`, `gh auth login`.
3. Replace the file path below with the **actual downloaded file location**.
```sh
gh secret set LOGRAF_SIGNING_KEYSTORE_B64 --repo alwansan/raf --body "$(base64 -w 0 /storage/emulated/0/Download/LogRaft-Update-Signing-Key.p12)"
gh secret set LOGRAF_SIGNING_PASSWORD --repo alwansan/raf --body 'LogRaftPublicTest2026'
gh workflow run lograf-apk.yml --repo alwansan/raf --ref lograf
```
(If `base64 -w 0` is not supported on your device, use `base64 < file | tr -d '\\n'` instead.)
4. Wait for the Actions run, then download **LogRaft-signed.apk** from a `lograf-*` prerelease.
5. The former ad hoc debug signed APK uses a DIFFERENT certificate. Android might require uninstalling that **once** when moving to this test identity. All future signed releases keep the same key and higher `versionCode`; use update/replace without data removal thereafter. **Do not uninstall until the signed release is verified**.

The CI verifies the exact keystore SHA-256 before signing and verifies APK signature/certificate before publishing. When secrets are absent, CI checks compilation and intentionally **does not publish another incompatible-key APK**.
