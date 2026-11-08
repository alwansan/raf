# T5 scheduled session
session_id: 20261108T1954Z-T5-scheduled-r2-provenance-7c29
origin: scheduled
base_sha: 91861e53beea14468479b160c1045d5afbe35680
scope_commit: f3684eafd742540170fcd5738f2a531ccd2e0152
work: work/T5/20261108T1954Z-T5-scheduled-r2-provenance-7c29.md
prior_checkpoint: clients/T5/sessions/20261108T1746Z-T5-scheduled-c91d.md

## Verified new evidence
The unified Mini r2 build [42517104924](https://github.com/alwansan/raf/actions/runs/42517104924) succeeded at immutable source c5100411c50ec3b663fa9262eb68c49c95180f3e; artifact 13631588625, ZIP digest sha256:f7f3bf586ebcfc61c55495ba037d5cdaead377a917441b84306977c2c75de0dc, expires 2026-11-22T19:52:14Z. This is not a direct APK or on-device result. The branch had moved to 91861e53 at read; comparison c5100411..91861e53 has 15 commits. The later T3 direct-launch buttons in bef7f88 were not compiled into that artifact. Source-only T5 SAF gate [42517141318](https://github.com/alwansan/raf/actions/runs/42517141318) FAILED at 'Assert shared Android host calls proven SAF stream'; separate Arabic portrait gate [42517141319](https://github.com/alwansan/raf/actions/runs/42517141319) SUCCESS. No redundant Mini build, Unity run, or T4 file edits.

## Boundaries / next
Read actual failing guard and Java source before deciding if failure is stale assertion or broken SAF call. Coordinate one next Mini build only if new compiled delta and gates warrant it; T3 direct-launch UI is a concrete unbuilt delta. Reconcile source HEAD and readiness votes before dispatch. Installed APK/OBB hashes, Resolution acceptance, three right controls and in-game p50/p95 remain DEVICE_PENDING. Original world save/reload result belongs solely to artifact 42058825739. NOT_READY.
