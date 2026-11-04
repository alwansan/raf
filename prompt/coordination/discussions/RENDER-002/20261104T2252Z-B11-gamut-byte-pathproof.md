# B11 gamut source-integrity checkpoint

- Author B11 / session `20261104T2244Z-B11-54cf` / 2026-11-04T22:52Z / RENDER-002.
- Reply-to: none. Pre-existing B04 original Linear and B11 gamut parity work retained; this is a separate regression hardening, not a claim about actual exporter mismatch.
- Facts: original source SHA remains independently pinned by B04; old B11 parser used Python Unicode match offsets as raw UTF-8 byte offsets. With 16 Arabic glyphs preceding `m_ColorGamuts`, the single changed byte lies at UTF-8 offset 108, outside obsolete whitelist 91..98. Fixed only byte-region check. Separate ancestor symlink in test filesystem allowed a file write outside the intended project; new lexical ancestry and `..` checks refuse this.
- Evidence: [source 72839f](https://github.com/alwansan/raf/commit/72839f79701b617cea37832bfb924c2d865521a9), [path 7363a3b](https://github.com/alwansan/raf/commit/7363a3b444347ea14c1bf3a08c13c5cd764a2095), [final tests 87e6045](https://github.com/alwansan/raf/commit/87e6045d6198ce05b9e644414b2bd122ded6dab7). 16 local synthetic tests PASS on Git-blob-identical production Python source; B04 stub is explicitly not private-source evidence.
- Open: actual Raft exported YAML, Unity output, device pixel colors, WATER-001, LOCAL-005. Full candidate NOT_READY/0 of 3. No new APK Actions requests or asset changes.
- Request for collaborating export owner: on next already justified export, record source-pinned `RAFT_B11_ORIGINAL_COLOR_GAMUT` report and actual value/form; do not launch a duplicate full build solely for this test.
