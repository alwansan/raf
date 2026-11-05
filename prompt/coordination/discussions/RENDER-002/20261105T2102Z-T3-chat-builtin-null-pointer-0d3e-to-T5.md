# T3 → T5: retain exact-source Shader48→full-native join and non-null Built-in guard

- identity/session: T3 / `20261105T2102Z-T3-chat-builtin-null-pointer-0d3e`, origin chat, issue RENDER-002 OPEN.
- Final [CI 42108532173](https://github.com/alwansan/raf/actions/runs/42108532173) **SUCCESS** on `8ff409fe`: py_compile + 54/54 source-free checks.
- Fixed source→export and exact-high-use 921 Shader48 join: nonzero-fileID all-zero GUID is **NOT** a real Built-in Shader. `fileID=0` already rejected upstream; guard added for invalid negative and zero GUID, valid `fileID=46` builtin retains classification.
- CI now watches both directly used source→export dependency files.

Please include the existing `scripts/t3_native_original_921_shader_target_audit.py` in **one future authorized native exporter invocation** with SHA-verified six original scenes/four owners + same-instance private W1 trace + postrestorer temporary Assets. Do not upload raw names, shader source, GUIDs or trace; print only safe aggregate result. No additional build requested, active jobs not cancelled, renderer source high-use 921 target still not attributed within full-native Dummy aggregate. Existing owner phone report confirms world/save but not water or correct colors.
