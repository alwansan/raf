# T2 scheduled session 20261111T0724Z-T2-scheduled-parent-symlink-q8r3
origin=scheduled
baseline_sha=44a33169533c936c1adf355b72f0c6b9461dc9c4
scope_commit=6faf9ef155c277c643342744c32763d7927633ae
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; owner confirms local world/save/reopen from artifact 42058825739; water pass/FFT errors remain.
result=Reject symlinked destination parent before temporary-file creation. Add isolated regression checking no file appears outside intended parent. This is a static symlink guard, NOT a complete TOCTOU solution against concurrently replaced directories.
verification=CI pending; no Unity/device run; no shader integration claimed.
next=Run Python unittest, inspect CI, then establish Foam RenderTexture and CB0 lineage and original ShaderLab binding. Preserve T3 fire/candle/smoke and T4/T5 mouse/resolution ownership.
