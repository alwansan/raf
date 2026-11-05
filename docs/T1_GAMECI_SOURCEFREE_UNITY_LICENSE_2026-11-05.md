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
