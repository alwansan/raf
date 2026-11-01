# Device log analysis — 2026-11-01

Aggregate only from the three owner-uploaded LogRaft 0.1.0 device log segments (session 20261101-163325-870). No raw logs or private identifiers committed.

92,415,739 bytes; 972,220 lines; approximately 16:33:30.650 to 16:35:06.258 local time.

Unity tag: 948,852 lines. Invalid Graphics.Blit pass 2/3 for PostFX - Bloom: 6,819 occurrences each.

UltimateWater/Foam/Global pass 1: 5,460. Invalid Dx11FFT compute kernelIndex 6 where available kernel count is zero: 1,365.

UltimateWater/Spectrum/Water Spectrum passes 3/5: 1,365 each. More invalid BilateralBlur, unknown-material and volumetric light passes.

FMOD Android Java bootstrap logged javaInitialized=true nativeVersion=00020215, which does not prove full audio correctness.

IL2CPP repeatedly reports System.IO.DirectoryNotFoundException on an APK jar:file: URI under assets/Haptics/SharkBiteRaftHaptics.wav. This requires Android asset-path inspection in the game project.

No FATAL EXCEPTION, Fatal signal, SIGSEGV or ANR matched these supplied segments, but absence cannot rule out failures outside capture.

No sampled CPU, GPU, memory or FPS counters in the old LogRaft logs. This motivated the new metrics stream.

Development of game-side shader/kernel and Haptics fixes remains separate on feature/android-native-port. This logging branch does not modify the game.

Unity's internal AndroidTestDiagnostics.cs already has its own FPS/frame percentile/Unity allocation diagnostics stored under the game's raft-logs folder.

Metrics rules: process CPU core-equivalent differs from device CPU load; KGSL GPU usage is device-wide; SurfaceFlinger FPS is presented-frame estimate. Null means unavailable, not zero.
