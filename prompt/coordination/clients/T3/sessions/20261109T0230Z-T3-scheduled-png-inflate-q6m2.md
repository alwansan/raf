# T3 scheduled — PNG inflate bound
session_id: 20261109T0230Z-T3-scheduled-png-inflate-q6m2
origin: scheduled
base_sha: 05d3e1d61d6b4aa82ba473002465179890ccd5b6
scope: RENDER-002, isolated diagnostic only

Read owner device feedback 42058825739 and T_TEAM instructions, T3 state/MEMORY and prior PNG audit. Phone world save/reopen is owner-confirmed for that artifact; white materials and square smoke remain unresolved. CL shared 20261108-232759 contains six T3 PNGs, but no pixel-level verification from this cycle.

Problem: PNG auditor allocated the entire untrusted zlib stream with zlib.decompress before checking IHDR-implied output length. A crafted screenshot can expand far beyond declared dimensions, risking worker memory. Also appended compressed trailing data was not rejected.

Scope registered before source edits: prompt/coordination/work/RENDER-002/T3-20261109T0230Z-scheduled-png-inflate-guard-q6m2.json, commit 1455db787f8a30dfd80dc8d5cd1d3abc5a028921.

Change: bound decompression with decompressobj(max_length=expected+1), require exact expected output and eof, reject unconsumed_tail and unused_data. Commit bfcb61b92ead7fe9ec1190bf12569679a8bffd19.
Tests: oversized valid-CRC PNG and valid scanlines with trailing compressed bytes. Commit badc18ecc527e33464c6fa141c7c9d6ec240fbe9.

Validation status: code reviewed; no Python execution or GitHub Actions test result confirmed yet. No CI dispatched. No raw game assets, Unity resources, .meta, GUID, .rgd, Android APK, mouse, or Settings modified.

Next: run python -m unittest tests/test_t3_cl_png_pixel_audit.py (or unittest discover), verify source-only CI, then analyze actual CL PNG pixels; this test does not establish any Raft visual repair. RENDER-002 OPEN / NOT_READY.
