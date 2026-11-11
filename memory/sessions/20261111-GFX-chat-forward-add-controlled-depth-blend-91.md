## 11 Nov 2026 — GFX127 original M02 ForwardAdd composed on Mesa

Session `20261111-GFX-chat-forward-add-controlled-depth-blend-91`, origin=chat. Write only `experiment/android-graphics-rootcause`.

Selected the original M02 first-subshader ForwardAdd directional pair using the exact full material keywords. DXBC-to-SPIR-V validation, GLES offline link and Mesa draw passed. Used the same indexed geometry as GFX119, authenticated material CB bytes and source texture mappings. A controlled LEQUAL, depth-write-off and ONE/ONE RGB blend with alpha preserved changed 1,979 of 2,008 covered pixels; output RGB matched the saturating sum exactly. Zero light and GL_NEVER controls both preserved the original Forward image byte-for-byte. The controlled state is explicit; actual Unity pass-state resolution is still open. Evidence `gfxlab/evidence/20261111_gfx127_forward_add_safe.json`.

Added three captures to the one-APK Android runner for lit additional pass, zero light and depth rejection. Reused M02 texture assets. The private assembly validator checked 136 fixture entries with the old source-free shell as a ZIP test harness. The log auditor replayed 6 cases/20 captures and a partially failing 5 cases/18 captures. [Android shell build 43055403000](https://github.com/alwansan/raf/actions/runs/43055403000) succeeded, artifact 13870888047. No new signed or device-run APK. Windows ForwardAdd, actual Unity states, shadow/Deferred cases, animation, and matched original PC gameplay remain open. `phase_closed=false`.

