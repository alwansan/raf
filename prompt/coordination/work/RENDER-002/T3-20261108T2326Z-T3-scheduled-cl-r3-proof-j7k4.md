# T3 RENDER-002 — R3 device capture evidence

session_id: 20261108T2326Z-T3-scheduled-cl-r3-proof-j7k4
origin: scheduled
baseline_sha: 8535bac2cc9843a6881355f434493ceff4d9de05
scope: read-only CL unified mini-lab 0.2.13 T3-01..06 evidence classification; no changes to T5 capture implementation or game materials.
hypothesis: R3 SurfaceView capture resolves prior false-black Window PNG, without proving original Raft shaders.
experiment_key: T3-CL-R3-20261108-232759-468049775
shared_resource: none; CL read only; no CI requested.

## Evidence
- Device events: https://github.com/alwansan/CL/blob/main/test/shared-20261108-232759-468049775/events-20261108-232759-468049775.jsonl
- Six PNGs in https://github.com/alwansan/CL/tree/main/test/shared-20261108-232759-468049775
- APK 0.2.13-shared code 13, reported source e7a6248b0d0c14b9772bd52f3bbdc5cf22fa9b9a, pack SHA256 6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f; Android 35 POCO 23013PC75G.
- T3-01..06 each EVIDENCE_READY, gl_error=0x0, contract=true, capture=verified-GLSurfaceView-overlay-on-window, verified_surface_pixels=true, and PNG sizes 119360,210904,162232,149557,154489,158584 bytes.
- T3-01 left red [255,0,0,255] and right blue [0,0,255,255]; T3-05 sRGB-like difference [128,128,128] vs [55,55,55]. These are synthetic GPU test frames, not game rendering.
- Earlier T3 state reported six false-black Window screenshots on 0.2.10; new R3 reports verified_surface_pixels=true. Visual human review still required, and actual PNG pixel analysis not performed in this cycle.

## Result and limits
SOURCE/DEVICE CAPTURE EVIDENCE IMPROVED: six device tests returned colored GLES readback contracts and nonempty captured PNGs, with SurfaceView capture verification reported by test harness. No original game materials, textures, shader keywords, alpha blend or lighting tested; no claim RENDER-002 closed. Do not conflate mini-lab device GPU proof with Raft world visual parity.

next_step: inspect actual six PNG pixels against expected colors; correlate original game's square smoke/white raft/hand screenshots with prefab→material→shader→texture using pinned ZIP2 export, without duplicating T1/T2 water work. Preserve NOT_READY 0/3.
