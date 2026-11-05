# T1 — alternative supported Unity 2021 activation check (GameCI, no Raft assets)

Date: 5 November 2026. Owner: T1, WATER-001 OPEN, NOT_READY 0/3.
Session: `20261105T102000Z-T1-gameci-sourcefree`.
This is **environment diagnosis only**, not original game/shader restoration or device verification.

## Previous proven boundary

An authentic SHA-pinned original FFT source-to-private compute staging run [CI41957549770](https://github.com/alwansan/raf/actions/runs/41957549770) converted 20 original DXBC compiled candidate programs to 20 private `.compute` import candidates (7 adversarial controls, workgroup shape and SPIR-V roundtrip checks). Original author source, Unity original kernel names and device GPU pixels remain unknown.

Three separate custom Docker Unity Editor 2021 attempts produced no valid shader import report. The most decisive fail-closed environment control is [CI41959712898](https://github.com/alwansan/raf/actions/runs/41959712898): **a source-free empty project failed before any ZIP2 asset acquisition**, Editor exit nonzero and a sanitized Unity licensing-failure message category. That control cannot establish *why* the custom `-manualLicenseFile` process failed; it excludes translated FFT code as the cause of *that* early failure.

## Distinct new engineering hypothesis

GameCI's [documented activation methods](https://game.ci/docs/github/activation/) and [unity-test-runner@v4](https://game.ci/docs/github/test-runner/) provide their own license activation and test pipeline. They are already in the same GameCI family used by Raft's separate full native Unity delivery pipeline. Test whether that **supported action** can activate the exact Unity 2021.3.45f2 environment and run one EditMode test. This is *not* a retry of the proprietary FFT conversion.

- New isolated `.github/workflows/raft-t1-gameci-unity-activation.yml`: only `scripts` and `tests` sparse checkout, reused existing `UNITY_LICENSE` environment, no new secrets, shared native Editor mutex `raft-native-engine-${{ github.ref }}`, no job cancellation and 35min budget.
- New `scripts/t1_sourcefree_unity_fixture.py`: generates a temporary, bounded Unity2021.3.45f2 project using a single entirely synthetic C#/NUnit test and Unity Test Framework package. No Raft code, source, shaders, DXBC, ZIP2, LFS, APK or proprietary pixels.
- New `tests/test_t1_sourcefree_unity_fixture.py`: four source-free controls for exact version/test manifest, forbidden preexisting overwrite, symlinks and invalid parent. The job runs these *before* GameCI activation. No original `.compute` is copied.
- Action `game-ci/unity-test-runner@v4`, `testMode=editmode`, expected output is ordinary passing tiny fixture only. The third-party action handles its own activation; the job never prints secret values or uploads private shader artifacts. Test runner output itself contains only synthetic fixture data.

## Experiment and interpretation

[CI42010878771](https://github.com/alwansan/raf/actions/runs/42010878771) was **in progress at initial report** after the source-free fixture stage succeeded. **Do not assume its eventual conclusion**.

If GameCI succeeds, this establishes *source-free supported activation and synthetic Unity C# EditMode execution* in that runner; it does **not** establish that the old manual Docker activation is fixed, that private FFT-derived code imports, that `FindKernel` maps the original game, or that Adreno water renders.

If GameCI fails, classify whether the fault occurred during activation, test package resolution or synthetic test discovery before blaming license validity or game shaders. A failed action alone cannot prove which secret/entitlement is invalid. Preserve bounded logs, no secret disclosure. Do not rerun heavy original 116MB SHA-pinned FFT acquisition until a license-validated Unity import pipeline exists.

Next: send the confirmed outcome to T5 via Git-backed coordination, then adapt the **separate private** authentic-FFT import test to whichever safe Editor activation is proved (if any), preserving original author/runtime and device evidence boundaries. WATER-001 OPEN and current Raft APK86 unchanged.


## Verified original-free Unity2021 license and ComputeShader import — actual results

The first [CI42010878771](https://github.com/alwansan/raf/actions/runs/42010878771) **COMPLETED SUCCESS** on public synthetic-only code. The GameCI action successfully loaded Unity 2021.3.45f2, resolved license entitlement, compiled a Unity Test Framework EditMode assembly and ran **1 passed / 0 failed** test. It used pinned observed CLI version `game-ci/cli v0.1.72` and `unityci/editor:ubuntu-2021.3.45f2-linux-il2cpp-3`, unlike the earlier custom `base-3` Docker invocation. No Raft files were acquired.

One code/test intermediate [CI42011666916](https://github.com/alwansan/raf/actions/runs/42011666916) **FAILED** before meaningful Unity execution because the generator added a second test before its Python regression expectation was updated. This is not shader or license failure. Reconciled at [source/test commit8f74158](https://github.com/alwansan/raf/commit/8f74158e8e285d26c779a695459d14641ce8f3f2).

The follow-up [CI42011720822](https://github.com/alwansan/raf/actions/runs/42011720822) **COMPLETED SUCCESS**: four source-free Python fixture controls, **2 passed / 0 failed Unity EditMode tests** on real Editor 2021.3.45f2. The second test imported a public, authored **synthetic** `Assets/T1Synthetic/FFTCanary.compute`, checked `AssetDatabase.LoadAssetAtPath<ComputeShader>`, and—because `SystemInfo.supportsComputeShaders=true` on this runner—actually executed `HasKernel("T1Canary")`, `FindKernel` and `GetKernelThreadGroupSizes` with asserted **(64,1,1)**. The bounded log `RAFT_T1_SOURCEFREE_COMPUTE_IMPORT asset_loaded=true gpu_compute_supported=true original_fft=false original_runtime_mapping=false android_device=false` matches the passing NUnit test. This is a **real, positive Unity2021 Editor/ComputeShader API smoke gate**, not only Python structural staging.

**Conclusion:** the Unity 2021 Editor *can* activate and import a ComputeShader with this current GitHub Actions license environment under the supported GameCI runner. Previous custom Docker activation failure does **not** prove the license secret is invalid; its process/image path was distinct. This directly removes the broad claim "no licensed Editor execution is possible" as a remaining environmental blocker. The new remaining target is an **actual private original-DXBC-derived shader import using the proven GameCI activation route with strictly private/redacted shader compiler logs**, followed by independent original runtime program/variant index-to-kernel mapping, resource/format fidelity and Adreno execution. Do **not** upload original DXBC/HLSL/shader source or feed it to GameCI's unfiltered public test-console logging.

WATER-001 remains OPEN and NOT_READY 0/3, most recent actual phone game remains APK86. No original authored Unity water source or graphics/device pixels restored in these tests.
