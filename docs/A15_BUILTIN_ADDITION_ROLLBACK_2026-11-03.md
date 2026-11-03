# A15 built-in shader addition rollback — 3 November 2026

## Reproduced production defect
In `scripts/restore_builtin_shaders.restore_project`, strict matching and dependency validation could succeed before writing include/license additions. A truncated or interrupted write then left a newly created partial addition behind because exception handling restored only exported shader bytes. A retry could fail with a conflicting file. Existing byte-identical files were needlessly rewritten, while ordinary truncating writes risked overwriting a destination created after preflight.

The historical native preview [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) failed *earlier*, before Unity, with no matching exported built-in shader identities. This separate hard blocker remains open; A15's fix does not solve it.

## Fail-first and exact-source green tests
- **Red:** [test source ff6dda2b](https://github.com/alwansan/raf/commit/ff6dda2b2e45c27fc629906e1f2a84a415ba4256), [run41643857822](https://github.com/alwansan/raf/actions/runs/41643857822), intentional **4/4 FAIL** with actionable traces for stranded partial include, stranded additions after failed shader write, rewritten identical notice, and concurrent new target safety.
- **Fix:** [source b7188de1](https://github.com/alwansan/raf/commit/b7188de1daffb34eaba11efcf24d4295f912453a). Existing identical include/license destinations are skipped; newly absent additions use exclusive `open('xb')`; only destinations successfully opened by this restore are registered for cleanup; on exception attempted shader replacements and newly created (even partially written) additions roll back. Exact authentication/identity, missing metadata, comment and symlink guards, and zero-match failure remain.
- **Green:** [A15 CI41644109948](https://github.com/alwansan/raf/actions/runs/41644109948) **SUCCESS, 22/22 synthetic/source tests** (4 new, 10 restorer, 4 A9 identity, 4 A3 symlink). Separate [A3 41644110046](https://github.com/alwansan/raf/actions/runs/41644110046), [A9 41644110350](https://github.com/alwansan/raf/actions/runs/41644110350), and [authenticated Unity 2021.3.45f2 vendor CI41644109994](https://github.com/alwansan/raf/actions/runs/41644109994) all SUCCESS on the same fix SHA.
- A15's isolated CPU-only `.github/workflows/raft-a15-builtin-restore-rollback.yml` uses Ubuntu 24.04, no LFS, six-minute timeout, unique A15+commit concurrency, `cancel-in-progress:false`; no original content artifacts.

## Evidence limits
These are deterministic synthetic filesystem exceptions, **not** Unity/Android GPU, power-loss atomicity, adversarial concurrent replacement after open, or a complete original AssetRipper shader export. Existing external backup and empty directories can remain after failure; a second I/O failure during rollback is not guaranteed recoverable. No original sources, shaders, `.meta`/GUIDs, `.rgd`, game data, protected branches, native requests, LFS, CL, scheduled tasks or releases were modified.

**A15 scoped transaction repair COMPLETE; overall RENDER-002/WATER-001/FFT-FORMAT-009 OPEN, game NOT_READY, no candidate, 0/3 full immutable readiness reviews.** The next authenticity gate is in-run complete export provenance before any claim of matched original built-ins.
