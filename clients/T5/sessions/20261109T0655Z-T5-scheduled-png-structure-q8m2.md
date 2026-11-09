# T5 session 20261109T0655Z-T5-scheduled-png-structure-q8m2
origin=scheduled
baseline_sha=7bcc268625def40e3d40c877f344e3066c5f2b8c
scope_commit=90c738ba66c44a06abc7c49979a6533779680aa6
implementation_commit=fd8a1b8a31de9a2360630c1bd7936d4a8d5a7008
test_commit=4ba03baf83c91bdf6dde1569f51e44264d6cdd81

## Evidence and result
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: world/save/re-entry success is limited to artifact 42058825739, source e9c358e; release packaging failed. Device LogRaft 220911-559 reported 23,884 water-pass errors and 3,850 FFT errors; presented FPS samples are not GPU timings. CL images and APK/OBB physical pairing remain unverified this run.

Read AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, STATUS, T_TEAM protocol/operating instructions, and current T5 PNG validator. New source correction: enforce IHDR color/depth combinations and standard encoding, exact unfiltered scanline payload byte count, and valid filter bytes for noninterlaced PNG. Preserve Adam7 support without claiming per-pass scanline validation. Added six synthetic regression cases. No game assets, T4 mouse, T1/T2 water or T3 shader changes.

## Validation limits
GitHub commits confirmed. Python regression cases NOT EXECUTED (no network-accessible source checkout in local container); CI/device/visual validation pending. The new gate is file-integrity evidence, not GPU pixel parity. No Unity/APK builds triggered or canceled.

## Next
Run `python -m unittest discover -s scripts -p 'test_t5_png_scanlines.py'` against repository checkout; audit six actual CL PNG files and hashes if available. Then prioritize owner-requested right-side buttons/Resolution and signed APK/OBB pairing, coordinating overlap with T4. Read latest HEAD and running Actions before further changes.
status=SOURCE_FIXED_UNVERIFIED
