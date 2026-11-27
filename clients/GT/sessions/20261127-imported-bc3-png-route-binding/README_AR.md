# GT V10 — initial actual fixture overflow; corrected, retry pending

[45961831652](https://github.com/alwansan/raf/actions/runs/45961831652) 242/242 source regressions (234 historical +8 V10), public exporter build SUCCESS; actual fixture stopped before export in authored byte generator, System.OverflowException at AuthoredBC3. Mask low 8 bits of packed selectors and RGB565 before checked byte conversions, no oracle or proof condition changed. Archive 15181236191 verified 8390 bytes SHA256 90352767518827fa94bd933c16ab8c4e2c1566b9b71c29c0c8ccd9b1a605f343, CRC and 15 members. No V10 actual pass; retry only dedicated public workflow. A3 blocked; no Unity/Android/XAPK.

---

# GT V10 — actual public exporter CI / PENDING | 27 نوفمبر 2026

V9 scoped PASS retained in 7f80870e611c616ab7d3cf75a6bd4457e3ddad18 (234 tests, 69 controls; four Swizzle unknown). [21514d0](https://github.com/alwansan/raf/commit/21514d088819182daf02ccd8890bf6deafa3936e) V10 source gate; [d6f63f0](https://github.com/alwansan/raf/commit/d6f63f0451940caf53fb1fa04a0349feacf3d037) typed actual authored BC3 fixture and controls; [ec6f6a8](https://github.com/alwansan/raf/commit/ec6f6a8dc080d24d21c6680cc9ea8388ab92b8e7) dedicated public-only workflow. [45961831652](https://github.com/alwansan/raf/actions/runs/45961831652) job 140381208160 in_progress; source regression step success, guard [45961831613](https://github.com/alwansan/raf/actions/runs/45961831613) success. No actual V10 pass yet. Separate BC3 ordinary texture format 12, 5x7 partial block, both alpha endpoint modes; source top-mip bytes from pinned provider, independent Pillow DDS decode and verified converter FlipY. V8/V9/native/full mip/Unity/Android proof not promoted. No original assets, LFS, Unity or XAPK. A3 blocked, G0–G6 open, white/fire unresolved. Next: Inspect exact actual public exporter result from run 45961831652. Verify independent BC3 top-mip same-route pixels, controls, archive, and no scope promotion; if fail, retain and diagnose actual NPOT/decoder behavior. No repeated historical actual V7–V9 runs.

---

# GT V10 — actual authored BC3 witness prepared / PENDING

Two authored 5x7 NPOT DXT5 textures, four top-mip blocks and one lower block each, distinct selectors and both alpha endpoint modes, independently captured typed source and exact same-route public PNG/meta. Ten proposed negative controls and explicit lower-mip/V8 exclusion. Not yet built or executed. Activate a dedicated source-only/public-exporter CI for V10. Verify 5x7 partial-block DXT5, actual PNG/meta, 10 negative controls, both alpha modes, no V8/V9/native promotion. Diagnose any decoder rounding/edge difference rather than adjusting the oracle to force parity.

---

# GT V10 — BC3 source gate implementation / PENDING | 27 نوفمبر 2026

Separate --imported-bc3-png-top-mip and typed BC3 receipt, ordinary format 12, complete block-rounded mip extent, pinned inline/direct-stream top decode using existing independent Pillow DDS oracle and pinned public converter FlipY. V8/V9 scopes remain separate; native and lower-mip/GPU/import claims false. New source controls, **not yet executed**. V10 source gate implemented (unexecuted); extend actual authored public DXT5 PNG export fixture with two distinct same-size NPOT multiblock textures, both alpha selector modes, test independent decode plus same-route counterfactuals. Run dedicated authored-only public tool CI; preserve historical 234 tests and 69 controls; no need to rerun actual V7–V9 without new purpose. A3 blocked; no original assets or XAPK.

---

