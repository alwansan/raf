# B14 WATER-001 — fail-closed shader/compute path provenance (2026-11-04)

## Why this matters

The currently used `scripts/verify_water_render_contract.py` previously accepted an `Assets` symlink through `is_dir()` and accepted a `*.shader.meta` symlink through `is_file()`. On normal POSIX filesystems both predicates follow symbolic links. This creates a source-integrity blind spot: an external metadata file can be counted as the existing shader's metadata during an otherwise structural water pass check. The older `*.compute.meta` check already rejected direct symlinks but not the project root redirect. This is **not** evidence that APK86's invalid water passes originate from a symlink.

## Integrated source change

- [Production scanner cfb97bf](https://github.com/alwansan/raf/commit/cfb97bf58e6c2736268df5aa8ecc9e54f3789ef6): verify the nonredirected project and Assets roots and every scanned shader/compute file and sidecar component without resolving away a symlink. Missing ordinary metadata still leaves `original_meta_present=false`, rather than forging an original GUID or throwing for an absent file.
- [Regressions 4e0ce04](https://github.com/alwansan/raf/commit/4e0ce04441e64e95439f8023cead5b2a9da025b3): five new fixture cases check external Assets redirects, linked Unity project root, external shader and compute sidecars, and missing regular sidecars. Existing pass counts and unauthenticated kernel fail-closed behavior remain tested.
- [Preflight 41917493634](https://github.com/alwansan/raf/actions/runs/41917493634), source `4e0ce04441e64e95439f8023cead5b2a9da025b3`: **SUCCESS**. Job `126880924437` executed the existing `test_verify_water_render_contract.py` suite: **10 tests passed** (previous five plus five new); the larger preflight job also succeeded. [Earlier source-only preflight 41917434811](https://github.com/alwansan/raf/actions/runs/41917434811) SUCCESS before the new tests, not a replacement for them.
- Standalone baseline reproduction on Linux: `Path('fake.meta').is_file() == True` for a symlink to a regular external file; `Path('Assets').is_dir() == True` for a symlink to a real external directory. The new scanner rejects both instead of accepting them.

## Evidence boundary and negative hypotheses

These tests exercise source-free synthetic files and the actual production Python validator; they verify path policy, not original Raft file byte integrity, shader programs, compute kernel ordering, Unity compilation, Vulkan execution or phone colors. They **reject** the assumption that `.is_file()` and `.is_dir()` imply nonredirected input. They do **not** validate the hypothesis that linked files explain water failures on the owner's phone; no such link was observed in the APK/source.

The [APK86 device log summary](https://github.com/alwansan/CL/blob/5394407b5cd0a0ca1848ff0902f8d2133bf6ea29/raft%20log/lf/LogRaft-20261104-225757-156/session-summary.json) still documents **40,327 invalid Ultimate Water passes and 5,555 invalid compute-kernel messages** in the final counters, including kernel index 6. Audio and Settings are working per owner; touch/layout is deferred. No native build/request/release, .meta, GUID, LFS, private source, CL, audio or touch modification was made.

## Handoff

Scoped path provenance defect **SOURCE_FIXED** only; **WATER-001 remains OPEN**, as do RENDER-002/LOCAL-005. **NOT_READY (0/3 independent full reviews)**. The useful next blocker is to establish actual original Unity-export shader/compute metadata/Kernel index identity and authenticated Source→Export binding (B47/B48/W1), then a coordinated Unity + device render test. No need to rerun this now-passing synthetic path experiment without a newly observed regression.
