# B21 — transient class1 trace test assertions not updated (closed)

- Agent: B21, session: `20261104T2257Z-B21-8e72`
- Issue: `RENDER-002`; discovered: 2026-11-04T23:10Z
- Failed [41931596587](https://github.com/alwansan/raf/actions/runs/41931596587): source `8b927602514771661ad486a88b8225334a8eb7f4`, failed at synthetic stage, BEFORE original ZIP2 acquisition/export or .NET compiler.
- Root cause: B21 extended optional class108 tracer to also capture native GameObject class1; two tests still asserted exact *old* C# diagnostic strings (`if (asset.ClassID != 108)` and `Ambiguous Light source identity`) rather than the revised source contract. The *code transformation* was not rejected by compiler, but the stale expected test tokens failed, which is correct fail-closed behavior.
- Resolution: [B21 test correction 847a7b7](https://github.com/alwansan/raf/commit/847a7b78056084ab0190c4d711ded5a60f692ff4) updated only targeted test expectations to `classID1 or 108`, the exact new diagnostic and additional GameObject skip counter; negative tests preserved. No original assets, shared W1/B02 code or pins modified.
- Confirmed [41931620538](https://github.com/alwansan/raf/actions/runs/41931620538) SUCCESS staging checks and pinned public tool compiler; [41931942755](https://github.com/alwansan/raf/actions/runs/41931942755) SUCCESS actual original 9-source Raft export and 2/2 exact Light→GameObject owner parity.
- Rejected hypothesis: this was not evidence that source class1 capture was incompatible with AssetRipper; only stale string-based assertions failed before compilation.
- Closed reason: tests and actual bounded same-instance export validated after revised test expectations. Neither CI success is GPU/device pixel proof.
