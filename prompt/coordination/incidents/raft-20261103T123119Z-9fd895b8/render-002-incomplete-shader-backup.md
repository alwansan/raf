# RENDER-002 — partial private backup retained on synthetic I/O exception

- Client A14 `raft-20261103T123119Z-9fd895b8`; time 2026-11-03T15:09:26.953Z; status: **fixed within CPU-only source scope**.
- Reproduced: [RED41659753191](https://github.com/alwansan/raf/actions/runs/41659753191) two of four tests intentionally failed due to left-behind partial external backup tree.
- Fixed: [source8dcca858](https://github.com/alwansan/raf/commit/8dcca858d2ae0646d5fb1a48fbdb2ab51a2909dc) exclusively created external backup directory removed on write failure, before any export mutation; existing user backup is untouched.
- Verified: [GREEN41660203887](https://github.com/alwansan/raf/actions/runs/41660203887) 4/4 pass, plus A3/A9/A15/vendor same-source CI success.
- Scope: synthetic fixture, not proof of real failed native export leak. This does not restore original GPU programs or establish device behavior.

Original failure [native41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) remains: the 198 verified vendor builtin shader identities had ZERO confirmed matches in the older original export stage before Unity. The separate inspected 107-file local subset is NOT certified complete. RENDER-002/WATER-001/FFT-FORMAT-009 OPEN; NOT_READY and full identical-candidate reviews 0/3. No Unity/APK/OBB/XAPK/Release, native request, original shader/.meta/GUID, LFS, CL or task was changed by A14.
