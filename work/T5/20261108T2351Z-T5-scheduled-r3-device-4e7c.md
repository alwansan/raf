# T5 R3 device evidence scope
session_id: 20261108T2351Z-T5-scheduled-r3-device-4e7c
origin: scheduled
base_sha: 5e3e3b8d294f29658d71d8bd4d4745625f2e5d91
issue_id: SHARED-MINI-R3-SURFACE-CAPTURE
status: completed
intended_files: work/T5/20261108T2351Z-T5-scheduled-r3-device-4e7c.md; clients/T5/sessions/20261108T2351Z-T5-scheduled-r3-device-4e7c.md
experiment_key: shared-mini-r3-pixelcopy-e7a6248-20261108-232759
resource_key: none
hypothesis: newer device evidence distinguishes fixed GLSurfaceView capture from old black PNG.
evidence: https://github.com/alwansan/CL/blob/main/test/shared-20261108-232759-468049775/summary-20261108-232759-468049775.json
result: T3-01 through T3-06 all EVIDENCE_READY, capture=verified-GLSurfaceView-overlay-on-window, verified_surface_pixels=true, GL error 0x0. Six PNGs have sizes 119360,210904,162232,149557,154489,158584 bytes. T3-01 expected red left and blue right, viewport 1060x1768. app_source=e7a6248b0d0c14b9772bd52f3bbdc5cf22fa9b9a, pack_sha256=6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f. Machine-verified synthetic GLES screenshot capture, NOT human visual acceptance or Raft graphics pass.
next: visually inspect PNG, check exact Mini provenance, do not rebuild unchanged Mini; game APK/OBB, Resolution and 3 right buttons still open.
