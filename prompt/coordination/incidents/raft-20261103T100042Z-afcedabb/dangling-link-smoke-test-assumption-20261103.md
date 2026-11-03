# A6 — dangling-link Smoke assertion incident (resolved)

Owner: raft-20261103T100042Z-afcedabb; 2026-11-03; LOCAL-005.
- Original run https://github.com/alwansan/raf/actions/runs/41623327576 FAILED: 14/15 Smoke, only new dangling-link test failed because it assumed File.Exists(symlink) must be false when the destination is missing.
- Correction: use File.GetAttributes(leaf) & FileAttributes.ReparsePoint, and independently verify target is absent. Test-only change https://github.com/alwansan/raf/commit/d01f4c4bfab342dc2eba35c569151cac9b292973.
- Same-source rerun https://github.com/alwansan/raf/actions/runs/41623564391 SUCCESS with 15/15 Smoke and netstandard2.1 build 0 errors.
- Resolved scope: false test assumption, not actual Unity/phone world save. No native build/release/cancellation.
