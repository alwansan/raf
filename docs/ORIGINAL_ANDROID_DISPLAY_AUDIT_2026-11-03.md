# Original Android display mutation audit — 2026-11-03

**Scope:** read-only structural investigation of the owner's Settings-only aspect/resolution regression. No Unity Editor, native game build, APK/OBB/XAPK, release, device test, original asset change, or scheduled automation modification. Only `feature/android-native-port` is writable.

## Verified implementation and CI

- Source/test/workflow commit: [315639e7cfac17685bd961038cd81d1f177bbef4](https://github.com/alwansan/raf/commit/315639e7cfac17685bd961038cd81d1f177bbef4).
- [Original-source offline integration 41536225034](https://github.com/alwansan/raf/actions/runs/41536225034) **COMPLETED SUCCESS** on the exact commit: synthetic lexer/readonly tests, private ILSpy CSharp9 decompilation, original adapter/harness checks, and managed C# compile passed.
- New `scripts/probe_original_android_display_paths.py` scans decompiled C# privately, masking comments/literals; reports only source basenames, hashes, line numbers, and direct display-mutation categories. It neither publishes original code nor changes the game. Four synthetic tests passed locally and in CI.

## Authentic source evidence

The probe inspected **2,394** original C# files. It found **three** direct display mutation sites in its *bounded categories*:

- `GraphicsSettingsBox.cs` SHA256 `e1854d74adbbe0565b586ec749f7de2cc73e3f97f59c388934a3faa0defc9300`: one `Screen.SetResolution` call at original source line 565. The existing Android-specific adapter inserts an early return in `ApplyCurrentResolutionAndFullscreenMode`; this is source-level protection only.
- `DynamicResolution.cs` SHA256 `69f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc`: two `ScalableBufferManager.ResizeBuffers` calls at original source lines 37 and 55. Their runtime invocation conditions and horizontal/vertical scale arguments are **not yet established**.
- The scan found no direct `Screen.orientation` or `Screen.fullScreenMode` assignments in the decompiled C# within its explicit patterns. It does **not** cover native/Unity engine internals, indirect calls, CanvasScaler/RectTransform changes, preprocessor reachability or third-party code outside this assembly.

## Interpretation and next discriminating test

**Confirmed:** there is a second original display mutation owner beyond `GraphicsSettingsBox`, so treating the Settings guard as an exhaustive resolution fix would be incorrect. **Not confirmed:** whether `DynamicResolution` changes aspect ratio, is invoked by Settings, or causes the owner's observed regression.

Next inspect the original `DynamicResolution` call arguments, lifecycle and references from the Settings path in private source-only CI, preserving source SHA and only structural output. Determine whether width/height scale factors differ or another UI layout path is responsible. Only then implement a narrow Android guard if the evidence warrants it. The owner's existing phone logs are from APK80 and cannot validate source-only changes. Full Unity/APK build remains explicitly on hold.

## Follow-up source-only argument comparison — 2026-11-03

- Follow-up code commit [f833082c6636b702ba45a8da4b72f70febdfb0f6](https://github.com/alwansan/raf/commit/f833082c6636b702ba45a8da4b72f70febdfb0f6) adds a bounded lexical parser comparing the two `ScalableBufferManager.ResizeBuffers` arguments without disclosing them. Five synthetic tests passed locally.
- [Original-source CI 41536643823](https://github.com/alwansan/raf/actions/runs/41536643823) **COMPLETED SUCCESS**, including original private CSharp9 recovery and managed compatibility compilation. Same authenticated `DynamicResolution.cs` SHA256 `69f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc`.
- The call at original line **37** has **syntactically identical** horizontal/vertical scale arguments. The call at original line **55** has **different source expressions** for horizontal/vertical arguments. This is a genuine second potentially asymmetric render-buffer path, **not proof** of differing numeric values, reachability from Settings, actual aspect change, or device validation.
- Next inspect privately the call-site method and argument expression semantics, including whether the line-55 values can differ and whether Settings invokes that path. Preserve the original behavior until a cause is demonstrated; do not blindly clamp both factors, disable dynamic resolution or alter Android graphics quality. The existing Android Settings guard only protects the one pinned `GraphicsSettingsBox` method. Full Unity/APK hold remains active.


## Original dynamic-resolution timing validation — 3 November 2026

- Private inspection [41552723321](https://github.com/alwansan/raf/actions/runs/41552723321) succeeded on28ee9fd0. Its encrypted packet was decrypted only in the working session and all128 file hashes and source commit were verified. DynamicResolution source matches the earlier audited SHA25669f9ab873de44b167deb3d6d00182fd59b0147b27d8365fff64b2849069cedbc. No plaintext source, original binary or key was published. The inspection workflow now preserves concurrent work instead of cancelling an earlier run.
- Full original-source review shows: OnDestroy resets both buffer factors to1; Update sends the two static factors; initial factors and min/max bounds match; internal increase/decrease methods apply the same operations to both. Different argument expressions at line55 therefore do NOT establish unequal numeric scaling or the cause of the owner's Settings regression. External writers/reachability still require investigation. Do not force uniform scaling or disable dynamic resolution on this evidence.
- A distinct source-proven defect: DetermineResolution ignored the return count from GetLatestTimings and checked the allocated array length instead. A retained old sample, missing timing support, zero/negative/nonfinite GPU timing could reach scale decisions without a valid measurement.
- Repair [fb0cdc20eef70a75c8d0bd1a5ed455137cbf7078](https://github.com/alwansan/raf/commit/fb0cdc20eef70a75c8d0bd1a5ed455137cbf7078) adds a SHA-pinned Android-only guard for zero returned samples and nonpositive/NaN/infinite GPU times before the original algorithm. Valid positive samples retain the original scale/quality decisions and existing frame-completion check. No scale clamping change, source asset alteration, resolution disable or new GPU percentage claim. Desktop source is byte-for-byte preserved after preprocessing, checked on the authenticated file.
- Local28 relevant Python tests passed. The private C# harness executes the actual adapted original class against timing doubles: absent return count with stale array, five invalid numeric values, valid slow/fast timing, first-frame wait and incomplete frame. It tests invalid samples cannot change factors or the raise counter while valid samples retain behavior. Original-source CI [41552985664](https://github.com/alwansan/raf/actions/runs/41552985664): **SUCCESS**, job125644914824:23 executable checks across10 cases, and original adapted gameplay managed compilation exit0/errorCodes={}. No Unity or actual GPU execution.
- Official Unity2021.3 references: [GetLatestTimings](https://docs.unity3d.com/2021.3/Documentation/ScriptReference/FrameTimingManager.GetLatestTimings.html), [ResizeBuffers](https://docs.unity3d.com/2021.3/Documentation/ScriptReference/ScalableBufferManager.ResizeBuffers.html), [Dynamic resolution](https://docs.unity3d.com/2021.3/Documentation/Manual/DynamicResolution.html). Buffer scaling and a desktop Screen.SetResolution call are distinct mechanisms. Remaining Settings/UI/device acceptance is open; only APK80 has the owner's existing logs. No Unity/APK build or automation change.


## Settings / dynamic-resolution source-reference experiment — 3 November 2026

A new bounded, private CSharp9 lexical inventory `scripts/probe_settings_dynamic_reachability.py` determines which source files contain explicit DynamicResolution class references, qualified writes to its horizontal/vertical scale fields, ScalableBufferManager.ResizeBuffers calls, and occurrences of ApplyCurrentResolutionAndFullscreenMode. Only basenames, normalized source SHA256, line numbers and category counts are output; the original two source fingerprints are pinned and unique, and unsafe/symlink inputs fail closed. This checks possible external writers and direct Settings references without changing a single game statement. It does NOT assert a complete call graph, Settings-to-dynamic invocation, concrete aspect regression or device result.

Three synthetic fixtures passed locally (plus py_compile) using the byte-identical original scanner masking helper; the same tests and original private ILSpy source scan are wired into the existing inexpensive offline integration CI. Source results must be read from the resulting run; until then the actual external-write and Settings-reference counts are UNKNOWN. The owner has not authorized a Unity/native game build from this research task. Primary engine documentation: https://docs.unity.cn/2021.3/Documentation/ScriptReference/Screen.SetResolution.html .
