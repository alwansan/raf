# T3 — SHA-authentic bounded Material ShaderLab vendor-restorer delta (2026-11-05)

**Owner:** T3. **Issue:** RENDER-002 OPEN. **Status:** original-source-scoped diagnostic, **not** an Android game/device fix.

## Tested boundary and provenance

[GitHub Actions run 42033940194](https://github.com/alwansan/raf/actions/runs/42033940194) completed **SUCCESS** on commit `dcb81c72b91817872cacc0fd664d937ea2f9ddef`, with job `bounded-original-export-postvendor` green. Original ZIP2 provider ref `15964ea8f246b6e076ce26b60931ee2e1a9a2385` and per-file size/SHA pins were checked for **12 original serialized providers**. The same public AssetRipperCLI source `036098ab525a3f9f693dc101edeb21faad4d32d8` and the original B21/W1/B02 same-instance export/traces were used for both before/after observations.

The experiment audited the **actual Unity YAML Material → .shader.meta GUID → .shader program content** from one disposable, authentic, bounded AssetRipper export. It then ran three production vendor Shader restoration tools in the same temporary export, with their own source checks and protected backups:

1. TMP 3.0.6, SHA256-pinned package `1ce172027b906a30be33cefe7b2ee46e1c8d35f729359b8b9785fc120d57b637`.
2. Unity Post Processing v1 upstream commit `933df236f509ed64ae5763ed57af33f2342cd1c2`.
3. Volumetric Lights upstream commit `d20b6f9a47ae857e1d313b147db2df3ef44b9196`.

**All three restorers succeeded** in this bounded export. This is *not* the full production native restorer set: it excludes the full-file-count original import, engine builtin restoration, W1 Depth Copy, B45 Blur, water/FFT integration, ILSpy game overlay, Unity 2021 Android compile, GPU output and phone test.

## Genuine same-instance results

| Authenticated 12-owner bounded export | Before vendor restoration | After three vendors |
| --- | ---: | ---: |
| Material YAML documents | 731 | 731 |
| Materials referencing Unity built-in shaders | 220 | 220 |
| Materials referencing local custom Shader GUIDs | 511 | 511 |
| Custom Material links to Shader files with `//DummyShaderTextExporter` | **511** | **495** |
| Custom Material links to non-Dummy Shader files | 0 | **16** |
| Distinct linked custom Shader targets | 54 | 54 |
| Distinct linked Shader targets retaining Dummy marker | **54** | **50** |
| Exported `.shader` files carrying Dummy marker | **126** | **98** |
| Total exported `.shader` files (vendor additions allowed) | 126 | 128 |
| Material links unresolved or zero | 0 | 0 |

**Observed effect:** vendor restoration removed the Dummy marker from Shader files referenced by **16 of the original 511 custom Material documents**, leaving **495 Dummy-linked documents across 50 distinct referenced targets**. This is an actual safe aggregate of original derived export files, **not** a claimed count of white objects on a phone. A non-Dummy vendor source is not proof of the original Shader48 compiled pass/variant semantics, Android import or pixels. The structural program counter can still count a Dummy template's complete-looking Pass; do not treat it as authentic executable shader recovery.

A private hash snapshot compared **every pre-existing `.mat` and `.shader.meta` file** before/after vendor replacement and asserted exact byte identity. The scoped Material YAML reference category counts also remained unchanged. Original source, project assets and associated `.meta` GUIDs were not patched in the repository.

## Outcome, reproducibility and CI caveat

- New isolated workflow: [`raft-t3-bounded-postrestorer-shader.yml`](../.github/workflows/raft-t3-bounded-postrestorer-shader.yml). The successful run used its initial push-trigger revision; after the run, commit [`2fa28c99`](https://github.com/alwansan/raf/commit/2fa28c993be93c59c1d15c4586ec62292cccbd88) changed the expensive experiment to **manual-only** and corrected a literal-escaped final newline in the *safe delta JSON writer*. No duplicate full export was run. On the completed original run, the safe **console JSON line is valid evidence**; the `t3-bounded-delta-safe.json` artifact member may have an invalid literal trailing `\\n` and should **not** be fed to strict JSON tooling without checking. The independent pre/post audit JSON files and console line were created successfully.
- CI artifact: `t3-bounded-postvendor-Material-Shader-42033940194`, artifact ID `13418610210` (seven-day retention at run creation). Only aggregates were uploaded, no raw Raft data, vendor source, GUID or private export trace.
- The stage asserts that pre-existing standalone Material/`ShaderImporter` metadata bytes are untouched and that counts of built-in, custom, null and unknown Material references remain unchanged. It also rejects a negative Dummy-link reduction.
- `RENDER-002` stays **OPEN**. This does not authenticate 50 remaining original shaders for Android or imply the 16 restored vendor shader programs reproduce the PC source. No APK, OBB, XAPK, native import or Adreno screenshot was created in this experiment.

## Next engineering step

Determine which **high-use remaining Dummy-linked custom Shader48 targets** matter most to actual scene Renderer→Material links, without exposing original GUIDs in a public report. Reuse B03 authenticated six-scene `Renderer→Material` graph and original Shader48 identity matching; stage real program reconstruction only against authenticated compiled source and preserve each program's original Passes/subshader variants, code, metadata and dependencies. When the existing main native importer is *separately authorized and coordinated*, inspect its full **post-restorer** `t3-native-material-shader-quality.json`, then require Unity 2021 and Android visual/device confirmation. Keep working audio/Settings unchanged and touch/layout deferred.
