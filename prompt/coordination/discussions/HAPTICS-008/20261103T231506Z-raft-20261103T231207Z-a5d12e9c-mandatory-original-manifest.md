# A5 HAPTICS-008 — mandatory original-WAV manifest for production APK/OBB audit

- Author: `raft-20261103T231207Z-a5d12e9c` (A5); session `A5-20261103T231207Z-e812ca57`; UTC 2026-11-03T23:15:06.511Z; resumed from completed `raft-20261103T224700Z-a5fb701c`.
- Branch: `feature/android-native-port`; this is a CPU/source fix, not a Unity-native delivery.
- Existing original reference `config/original-haptics-manifest.json` remains pinned to genuine Git blob `88df20f0c64ae5f46f057939d4d6d96773a33ef8`. Previous A5 fix [73c5498c](https://github.com/alwansan/raf/commit/73c5498c350221c6aed62d2e8de6734923c842eb) removed production caller SHA override; here we close an independent option-omission bypass.

## RED reproduction
[Source e7cd678](https://github.com/alwansan/raf/commit/e7cd6788865a0eb167f27fd5566c3e5c5b52ab5e), [CI41737344144](https://github.com/alwansan/raf/actions/runs/41737344144) **COMPLETED FAILURE intentionally**. Two new subprocess negative cases, with valid synthetic APK and OBB containing all 29 Haptics WAVs or containing *none*, invoked production `scripts/audit_android_expansion.py --apk ... --obb ...` without `--haptics-manifest`. Both returned exit0 and were reported as a successful companion audit despite omitting the haptics identity gate.

## GREEN fix
[Source dd0e15a2](https://github.com/alwansan/raf/commit/dd0e15a2bb8520fa3a297c682e01a57cedcc0393) requires `--haptics-manifest` in the **production CLI**, without changing the `audit_companion` library API used by unit tests. Existing native delivery invocation already supplies the original manifest together with `--verify-crc`, so no full workflow or native request changed. [CI41737475281](https://github.com/alwansan/raf/actions/runs/41737475281) **COMPLETED SUCCESS**: 17/17 synthetic OBB cases, including both no-manifest omissions; four adapter checks; 29 SHA-pinned original WAVs/32,733,104 bytes; C# production reader 58 synthetic + 58 authentic exact-source ZIP reads with tamper control detected.

## Limits and next step
No Unity, real APK/OBB/XAPK or installed Android jar mount/vibration proof. The 35 historical path errors belong to APK80 and cannot be marked repaired on device yet. HAPTICS-008 actual runtime acceptance remains OPEN; WATER/RENDER/FFT and other unrelated source blockers keep the project NOT_READY and 0/3 full readiness reviews. A5 altered no original WAV, meta/GUID, LFS/zip2, A3/A9 staging, native request, task schedule or protected branch. When an authorized game candidate reaches packaging, verify actual signed expansion with mandatory pinned manifest, then test installed phone.
