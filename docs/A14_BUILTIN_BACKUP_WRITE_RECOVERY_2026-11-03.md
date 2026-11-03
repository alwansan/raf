# A14 — external built-in shader backup I/O recovery (3 November 2026)

Client `raft-20261103T123119Z-9fd895b8`; issue RENDER-002. No game data or private source published.

## Actual source defect

`scripts/restore_builtin_shaders.restore_project` created an exclusive external backup directory, but original shader/.meta copies were not inside its later rollback handler. If the filesystem failed during one backup write, a partially written private backup remained; a retry could then fail at `mkdir(exist_ok=False)`. Original exported assets had not yet been modified.

## Reproducible red/green

- [RED test CI41659753191](https://github.com/alwansan/raf/actions/runs/41659753191) from source `219d517dae`: two expected FAIL on partial first shader and late second metadata backups; positive successful backup and pre-existing-backup integrity checks passed.
- [Fix source8dcca858](https://github.com/alwansan/raf/commit/8dcca858d2ae0646d5fb1a48fbdb2ab51a2909dc): wrap only the newly created external backup-population phase in `try/except BaseException`, remove that exclusive directory with `shutil.rmtree` on failure before rethrowing. No fake shader identities or relaxed zero-match gate.
- [A14 green CI41660203887](https://github.com/alwansan/raf/actions/runs/41660203887) 4/4 successful on fix SHA; independent [A3](https://github.com/alwansan/raf/actions/runs/41660203946), [A9](https://github.com/alwansan/raf/actions/runs/41660203931), [A15](https://github.com/alwansan/raf/actions/runs/41660204010), and [official vendor](https://github.com/alwansan/raf/actions/runs/41660204069) workflows all COMPLETED SUCCESS on that exact fix SHA.
- Artifacts: `raft-a14-synthetic-backup-41659753191` and `raft-a14-synthetic-backup-41660203887`, verified as small aggregate fixture logs.
- Command: `python3 -m unittest discover -s tests -p test_a14_builtin_backup_atomicity.py -v`; independent workflow `.github/workflows/raft-a14-builtin-backup-atomicity.yml`, 7-minute timeout and `cancel-in-progress:false`.

## Limits and next steps

The fix handles ordinary tested I/O failures. Cleanup itself can fail, and it does not promise safety against hostile concurrent filesystem manipulation of the temporary backup tree. No original game asset, shader bytes, metadata GUID, render pass, water FFT or GPU execution was tested by A14.

Original failure [native41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) remains: the 198 verified vendor builtin shader identities had ZERO confirmed matches in the older original export stage before Unity. The separate inspected 107-file local subset is NOT certified complete. RENDER-002/WATER-001/FFT-FORMAT-009 OPEN; NOT_READY and full identical-candidate reviews 0/3. No Unity/APK/OBB/XAPK/Release, native request, original shader/.meta/GUID, LFS, CL or task was changed by A14.
