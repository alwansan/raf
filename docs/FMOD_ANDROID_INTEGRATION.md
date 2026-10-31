# FMOD Android integration: verified acquisition and validation

Current source wrapper version: **2.02.15**, constant `131605` / `0x00020215`.
FMOD versions use BCD; interpreting the patch byte as decimal incorrectly gives21.
The original FMOD managed providers are present, but the proven Android APKs lack
the native Android FMOD library. A successful IL2CPP build does not prove audio.

## Package received (2026-11-01)

The owner supplied fmodstudio20215.unitypackage; exact version/ARM64 ELF/export/Java
checks passed. Package SHA256: b157d6e298bed0eb54b9c07246cb4de51ce9de10f850d7dc0c494ccaee664c48.
No further download is currently needed. Historical acquisition instructions:

### Original acquisition

Download **FMOD for Unity2.02.15** from https://www.fmod.com/download after signing
in/registering there, then attach the original `.unitypackage` to the Work chat.
No PC, fork, extraction or public SDK upload is required. If this exact version
is unavailable, report that rather than substituting a different version blindly.

The official source repository explicitly excludes native binaries:
https://github.com/fmod/fmod-for-unity . Forking it cannot supply Android libraries.
The live FMOD download page requires sign-in. Do not share account passwords or
Unity license secrets. Do not publish the full downloaded SDK/installer in this
public project. Official CI/download discussion:
https://qa.fmod.com/t/how-can-i-download-the-fmod-engine-api-from-a-terminal-or-script/21466

## Read-only preflight

Run `python3 -m scripts.audit_fmod_unity_package /private/input.unitypackage`.
This standard-library-only validator checks:

- Exact original BCD header version, refusing mixed or incorrect versions.
- Release Android ARM64 ELF64 shared libraries, bounded section tables, defined
  dynamic FMOD API exports and missing packaged FMOD/native dependencies.
- Android `fmod.jar` and actual `org/fmod/FMOD.class` Java class signature.
- Archive links/traversal/duplicate records, compressed/expanded size bounds,
  package/library fingerprints. No extracted file writes or native execution.

These are metadata/identity checks, not a vendor-signature assertion or a native
runtime `getVersion` test. The actual supplied package passed these metadata checks on 2026-11-01.
Synthetic fixtures remain separate from actual runtime/device evidence.

## Integration after the real package passes

Stage only the required native runtime/Java bridge and any actually required DSP
plugins using correct Android ARM64 import settings. Preserve original managed
DLLs and gameplay/script GUIDs; do not import a second competing FMOD CSharp SDK.
Verify native dependency closure and actual FMOD runtime version on Android.
Original Raft bank selection, sizes/hashes, Android loading paths, DSP availability
and audible/device tests remain separate gates. The owner need not resend the
already supplied original game archive or bank data merely to acquire FMOD.

Work only on `feature/android-native-port`; no branch merge or release is implied.


## Original StreamingAssets inventory (metadata only)

Five original banks total **123817498 bytes**. MasterBank.bank is the only LFS
bank: **101600960 bytes**, SHA256
`10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339`.
The regular Git banks are MasterBank.strings.bank (29530), VO_logs_english.bank
(11455008), VO_npc_english.bank (8180896), VO_olof_english.bank (2551104 bytes).
Original StreamingAssets/Data.rgd and haptic WAVs also exist. This inventory did
not fetch LFS bank bytes. The current export ignores StreamingAssets; a future
explicit staging/loading audit is required. Do not claim native-library presence
alone restores audio, or ask the owner to resend the original game archive.


## Private Actions transfer

Only a sealed 10-file runtime subset is in the public branch:
`android-port/Dependencies/fmod-2.02.15-android-arm64.aesgcm`, with exact file
provenance in `config/fmod-android-runtime.json`. The 32-byte hex decryption key
belongs ONLY in the existing UNITY_LICENSE environment secret named
`FMOD_ANDROID_RUNTIME_KEY`. It is not an FMOD-account credential or Unity license.
Never commit the key, a plaintext SDK or a hash-derived substitute key.

The isolated `raft-fmod-runtime-preflight.yml` checks file safety and actual
ARM64 payload only after the secret exists. Missing key explicitly blocks the
real stage. Main Unity integration, original managed Android bootstrap, Java
initialization, banks, DSPs, attribution and device audio remain unverified.
Vendor native metas/Java meta/license meta are preserved exactly; no competing
FMOD CSharp files or debug libraries are imported.


Actual Actions preflight41251245329 retry/job124687318069 passed:10 exact files,
ARM64 ELF identity,0 competing CSharp sources,0 overwritten original metas.
FMOD_ANDROID_RUNTIME_KEY is now configured in UNITY_LICENSE; no further owner
setup/download is required. This is not Unity import or audible-device proof.
