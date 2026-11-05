# T1 — independent original FFT bank1 sampled-descriptor permutation failures

- Identity/session: T1 / 20261104T235355Z-T1-9fca; source final green narrowed SHA `ec6618e14ef6a26ba0d0dc925f3b17056d03721a`.
- Impact: A CPU Mesa Vulkan two-pass probe cannot treat bank1 swapped input descriptors as a safe numeric oracle. **Not** evidence of Unity/Adreno bug; original shader/phone water remain unknown.
- Original input: SHA-checked ZIP2 `sharedassets0.assets` 115978112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; ComputeShader original pathID2456 SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`.
- CI `41938536760`: pair18/19 at original second-pass swap crashed `-11/SIGSEGV`, after original size/SHA and synthetic tests passed.
- CI `41939082498`: pair10/11 second-pass swap returned finite, written original output but *same-source comparator tolerance=false*, so numeric oracle fails closed.
- Recovery: retain failures and avoid re-running identical dangerous bank1 profile without new driver/descriptor analysis. Narrow source-authentic probe to bank0 pairs0/1 and8/9, CI `41939314440` 6/6 original two-pass runs green with both first/second swaps altering outputs. No original game or harness A1 modified.
- Close reason (scoped incident): negative evidence preserved, bank1 deliberately left INCONCLUSIVE; no hidden error and no widened result claim. WATER-001 remains OPEN.
- Next: independent bank1 descriptor/SSA numeric path or actual Unity imported authenticated .compute, then Adreno.
