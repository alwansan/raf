# T1 isolated session — raw C# string lexical evidence guard

session_id: 20261105T050710Z-T1-raw-string-lexical-guard
resumed_from_session: 20261105T041234Z-T1-indirect-dispatch-regression
identity: T1
identity_conflict: possible parallel T1; shared state/MEMORY deliberately untouched
baseline_sha: d3539213fc1fbcbf0ecc5c25d59d675cd1f7c527
issue: WATER-001 OPEN; NOT_READY 0/3

## Baseline and hypothesis
Read current T-team operating guidance, T1 state and memory, original derived FFT report, existing caller audit and tests. GitHub branch API HEAD d3539213; recent T1 Unity 2021 real Editor job 41959712898 failed at source-free licensing gate before original owner acquisition; original bank0 41939314440 successful CPU Vulkan six cases; bank1 negatives retained. No original private data used. Raw C# 11 triple-quoted and interpolated raw strings can contain `shader.FindKernel(...)` text; original masker does not recognize them and can emit false evidence.

## Actual change and verification
Plan created at commit 3cccc987. Script fix commit 3f1b88f: mask C# raw string tokens before regular comment/string lexical mask. Test commit 5218edb adds raw and interpolated raw false-call regression plus actual Dispatch outside literal. Locally ran a standalone Python reproduction of exact regex and call-count assertions: PASS (FindKernel=0, Dispatch=1, SetTexture=0). Full repository unittest, original caller dataflow, CI and Unity were NOT run in this session; do not count isolated synthetic reproduction as source/device proof. Caveat: regex masking is conservative, not a complete C# parser; interpolated expressions may be masked, failing closed.

## Next
Do not repeat 20/20 private source translation or CPU Vulkan success. Fix source-free Unity activation on authorized runner with T5; then run authenticated FFT candidate import and capture actual HasKernel/FindKernel results. Alternatively independently recover original caller dataflow with verified private source. No Actions cancelled, no other branches touched, no audio/Settings/touch edits.
