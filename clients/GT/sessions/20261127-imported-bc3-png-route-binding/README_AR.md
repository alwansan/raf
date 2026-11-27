# GT V10 — corrected exporter replay witness prepared / PENDING

Historical 5x7 pair unchanged, pin both exact old source top hashes and compare with original independent oracle. New extended 5x7 pair adds equal RGB565 endpoints with all selectors and visible alpha-zero RGB on both textures. Transparent RGB control targets actual transparent texture in old pair, no false rejection from NPOT crop. 10 counterfactuals per fixture. Patch is scratch public-tool only, not installed in production. Dedicated public-only CI: pinned patch, 5 new patch tests (256 blocks), historical 242 regressions, exact old fixture replay, extended equal-endpoint fixture. Require strict RGBA match and 10 negative controls each. Historical transparent RGB control selects texture that actually has alpha-zero pixels; extended requires both. No production install yet.

---

# GT V10 — exact decoder root cause; repair source prepared | 27 نوفمبر 2026

[45962397906](https://github.com/alwansan/raf/actions/runs/45962397906) strict FAIL, 242 source regressions and public build successful, 53/70 exact RGBA, all 70 alpha exact. Downloaded ZIP 15181805246: 11690 bytes SHA256 5f790d361a1bddfa0ff523942a76f8b646e8d26488c32b161720aa0cdcbec65c, Git blob da4b8d8b6686be9f4f8097b141f20b90561181fd, CRC and 19 member hashes verified; retained exact synthetic source top hex, actual PNG base64, expected/actual RGBA, hashes, mismatch indices in diagnostic-45962397906.json. Every one of the 17 mismatches has RGB565 c0<c1 and selector 2/3: erroneous BC1 3-color palette in DXT5 dependency, not a tolerance/flip issue. Source patch on exact public TextureConverter blob f8cec77003d86fa3d6ad1a04002927733a1986a6: ordinary DXT5 only, private temporary top-mip copy, swap endpoints and xor selectors 0x55, equal endpoints select 0; no source byte mutation, DXT1/DXT3/Crunch unchanged. Independent Pillow mathematical control. **Not executed yet**. Next: Compile pinned exporter with scratch-only DXT5 normalization; rerun exact previous authored bytes and independent extended equal-endpoint/alpha-visible fixture; require strict V10 parity and negative controls. No production integration until actual proof. A3 blocked, all G0–G6 open; original assets not read, no XAPK.

---

# GT V10 — focused diagnostic activated | 27 نوفمبر 2026

[b734df6](https://github.com/alwansan/raf/commit/b734df6fde87bad3e478697367a8e7f5b12342d6) preserves the real RGB mismatch, adds bounded authored forensic output before unchanged strict gate. [01ccb8f](https://github.com/alwansan/raf/commit/01ccb8f171511e6069a335b4ed969fd070699d23) activates diagnostic [45962397906](https://github.com/alwansan/raf/actions/runs/45962397906), job 140383056608 in_progress, guard 45962397871. No V10 pass. Next: Read exact run 45962397906; download/verify artifact and inspect per-channel histograms, stored block indices and actual PNG pixels. Derive a justified correction only from evidence; strict V10 remains false. Separately fix authored fixture alpha-zero visibility. A3 remains blocked. No original assets, Unity, Android or XAPK. G0–G6 remain open; no force push or non-target branch writes.

---

# GT V10 — actual BC3 RGB mismatch, diagnostic prepared | 27 نوفمبر 2026

[45962079936](https://github.com/alwansan/raf/actions/runs/45962079936) 242 source regressions and pinned public .NET build passed; actual two authored PNG collections exported, strict route proof FAILED for both renderers with same_route_png_RGB_DRIFT:2. No tolerance or normalization accepted; no V10 pass. Verified artifact 15181053655, 8745 bytes SHA256 42206ac56d230c8a673a40aaa13b151c545144c761086ad75976692af2bfaf10, CRC 16 members. Added bounded per-pixel diagnostic to retain exact authored PNGs, source 64-byte top mip hex, expected/actual RGBA, block and selector, channel deltas, orientation and channel-swap diagnostics before unchanged strict gate abort. Exact same fixture bytes retained for reproduction. Independent local Pillow check also identified fixture 0 missing visible alpha-zero pixels due NPOT crop; later adjust selector separately, not to hide RGB mismatch. A3 blocked, G0–G6 open; no original assets or XAPK.

---

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

