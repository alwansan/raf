# Raft Android — standalone APK delivery candidate, 2026-11-02
Only writable branch: feature/android-native-port. Unity2021.3.45f2, ubuntu-24.04, ARM64 IL2CPP.

## Entry evidence
HEAD8d66889b5e7b9ad0c545d4cff7ab4d1dafce578b. User explicitly requests a new APK for phone testing and continued research/development.
Last real native41371789680/sourceff8e9034/job125043642226 SUCCESS: APK654246062bytes plus mandatory OBB2287764013bytes; neither retained. It is not a downloadable standalone APK. Earlier standalone failed because a generated Unity asset was2750639264bytes, above Java signed-array capacity, not a CSharp compile regression. See complete prior evidence in WORK_SESSION_HANDOFF_2026-11-01_LOGRAFT_GPU_OOM.md.
Current source has opt-in original-gamepad touch controls, safe-area layout editor and allowlisted mapping persistence. Latest original Android source integration41398404703/platform41398404710 SUCCESS, but these newer features have not passed a full Unity/device interaction test.
CL raft-log directory and LF index still refer to historical 2026-11-01 evidence. No new phone acceptance assumed. Water FFT/custom shaders, FMOD audible sound, original .rgd roundtrip, complete touch action ownership and GPU OOM remain open.

## Primary-source research and delivery decision
Unity2021.3 documentation explains Android GPU formats, uncompressed RGB(A) storage and ASTC block sizes:
https://docs.unity3d.com/cn/2021.3/Manual/class-TextureImporterOverride.html
Unity2021.3 GetAutomaticFormat reports the platform-selected importer format:
https://docs.unity3d.com/jp/2021.3/ScriptReference/TextureImporter.GetAutomaticFormat.html
Android Gradle source uses BytesSource for assets even when noCompress selects NO_COMPRESSION:
https://android.googlesource.com/platform/tools/base/+/studio-master-dev/build-system/gradle-core/src/main/java/com/android/build/gradle/internal/tasks/CompressAssetsTask.kt
Thus merely adding noCompress is not established as a safe fix for the observed Java array failure. Do not bypass the actual size gate or split Unity binary members blindly.

Existing bounded import profile changed only six >2048 textures in the last measured native. That profile does not address uncompressed eligible colour images already capped to2048. We have NOT measured how many such images exist yet; new aggregate per-Android-format inventory and changed counts will establish this in Unity.

## Implemented candidate
- Preserve previous bounded2048 profile and its explicit override protection.
- Add a separate conservative colour-compression pass. Only Default Texture2D colour/sRGB importers, PNG/JPG/JPEG/TGA/BMP sources, no explicit Android override, no TMP font dependency, and Android-resolved RGB24/RGBA32/ARGB32 formats qualify.
- Use Android-only ASTC4x4 at unchanged importer maximum dimensions; preserve source images, GUIDs, mip/filter/alpha/readability settings. Linear/data maps, HDR, sprites/normal maps, special shapes, fonts, unknown or already-compressed formats and explicit Android overrides remain untouched.
- ASTC4x4 is LOSSY8bpp GPU compression, not lossless restoration. No claim of image parity, device memory reduction, package-size success or actual converted count before real Unity evidence. Selected texture counts and anonymous format histogram are logged.
- Real selection logic extracted to AndroidColourTexturePolicy and linked directly into a .NET8 executable fixture.37 cases cover accepted formats/extensions and special/data/font/override/HDR/compressed/unknown exclusions. No Unity/GPU is executed by that fixture.
- Standalone is the default package layout; explicit -raftPackageLayout split remains available for private diagnostics. Unknown layouts fail. Split still requires nonempty OBB; standalone refuses unexpected OBB. All40scene, SDK, histogram, original banks and signatures remain mandatory.
- Workflow verifies exact original StreamingAssets SHA256/size/uniqueness against APK alone or the actual pair, not an assumed OBB. Tests execute the REAL embedded workflow gate against synthetic standalone/split archives, rejecting missing, altered and duplicated data. Mock ELF metadata only; not actual ELF/phone proof.
- Public delivery still requires BOTH explicit native/device markers, successful reconstruction and signature/data gates, no OBB dependency, and APK<2GiB. Releases publishes only direct APK. No loose resources or OBB publication.

## Validation and next step
Local8scene/texture-policy+6distribution-policy+3actual embedded data-gate tests pass; YAML and embedded Python parse; git diff check passes. No dotnet runtime in this scratch environment, so executable37case selection fixture must pass GitHub Actions before native opt-in.
First commit requests cheap platform CI only. After it passes, submit ONE native+device-test request. Inspect RAFT_ANDROID_COLOUR_COMPRESSION counts/histogram, actual Gradle largest member, full APK/SDK/FMОD/signature gates and release job. If still oversized, preserve strict gate and classify actual sizes; do not publish incomplete APK or claim gameplay restored.
Continue independent source/water/input/save work as supported; if only multi-hour build remains, give run/status and stop waiting per owner direction. Subsequent scheduled cycle inspects actual result without duplicate native dispatch.


## Verified cheap gates and native delivery opt-in
Sourcefce6ec4d7ea00b5d87d8d715aff709c17c234f95: platform41400736657/job125131794073 COMPLETED SUCCESS. Real linked selection code ran37cases, actual embedded original-data gate passed standalone/split positive and altered/missing/duplicate negative fixtures, existing7APK/OBB+5payload audits+8scene contracts passed, offline library build and10identity/session smoke passed. Runner41400736664 SUCCESS; gated Unity41400736654 was preflight/skip, NOT full Unity validation.
Explicitly request ONE native+device-test run with -raftPackageLayout standalone. If it succeeds and all delivery gates pass, publish directAPK automatically under existing prerelease policy; no OBB or rawsource/asset publication. Release notes tell owner Test report→Enable touch gamepad→Edit touch layout and warn of water/render/save/audio uncertainty and lossyASTC. No claim of APK until real outcome.
