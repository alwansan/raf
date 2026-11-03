# A6 — authenticated Unity built-in shader include-comment regression

Date: 2026-11-03. Issue: RENDER-002. Branch: `feature/android-native-port`. Coordination owner: `raft-20261103T121333Z-a6c7f4e2`.

## Reproduction

The original `scripts.restore_builtin_shaders.rewrite(path, files)` scanned every `#include "name"` substring using `INCLUDE.sub`, including those inside ShaderLab line comments and C-style block comments. A synthetically commented `#include "missing.cginc"` was therefore incorrectly interpreted as a mandatory original shader dependency and threw `ValueError('Unresolved built-in shader include')`. The prior A6 local red suite recorded two failing negative cases before the patch; this was not a game/device observation.

## Bounded source repair

[Commit fa4647359f07b0734e6013dade930b9b010bc1f6](https://github.com/alwansan/raf/commit/fa4647359f07b0734e6013dade930b9b010bc1f6) changed **only** `scripts/restore_builtin_shaders.py` and `tests/test_restore_builtin_shaders.py` (+40/-3 lines total). The new `rewrite` masks comments to same-length whitespace, preserving line breaks, locates real include directives in that masked copy, and copies untouched source segments directly from the original text. An include path whose *quoted filename contains* `//` remains active and resolves normally. Genuine unresolved active includes still fail closed. Existing A9 `exported_shader_identity` lexer, original shipped shaders and all original game source/GUID/meta files were untouched. The zero-matched-exported-built-in identity gate remains strict.

The three additional C#-independent Python regression cases cover (a) commented fake include with genuine include on a different line, (b) closed/unterminated block comments, (c) quoted path containing literal double slash, plus all seven prior tests for source restoration/metadata and missing true include.

## Verified same-source evidence

- [Exact-source CPU Unity built-in shader restoration CI 41633638783](https://github.com/alwansan/raf/actions/runs/41633638783): **COMPLETED SUCCESS**, 10/10 tests, SHA256-authenticated Unity 2021.3.45f2 archive providing 198 runtime shader identities, five fixture shader restores and 29 include dependencies, all original fixture metas unchanged.
- [Same-source independent A9 lexical compatibility CI 41633638754](https://github.com/alwansan/raf/actions/runs/41633638754): **COMPLETED SUCCESS**, four A9 lexer tests and the same 10 shader-restorer regressions, including commenting tests.
- Verified source commit has exactly two changed files; no native request, full Unity or APK initiated by A6.

## Limitations

This is a genuine parser correctness fix, **not** recovery of Raft's missing original water/FFT programs. The older independent [native run 41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) failed pre-Unity at no matching exported built-in shader identities; this correction does not assert that blocker is closed. No original .meta/GUIDs, game assets, LFS, APK/OBB/XAPK, Release, scheduled tasks or `alwansan/CL` changed. Neither unit tests nor official shader archive fixture restores establish Unity Editor, Vulkan/Adreno or phone behavior. RENDER-002 and WATER-001/FFT-FORMAT-009 remain OPEN; game readiness remains NOT_READY (0/3 full reviews).
