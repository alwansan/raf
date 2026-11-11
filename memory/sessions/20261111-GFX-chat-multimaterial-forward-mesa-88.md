## 11 Nov 2026 — GFX123 M00 and both original M03 Forward slots rendered on Mesa

Session `20261111-GFX-chat-multimaterial-forward-mesa-88`, origin=chat. Write only `experiment/android-graphics-rootcause`. Pinned ZIP2 source `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

Extended the GFX119 witness using the exact renderer material pointers and per-material original Forward variant. Authenticated source DXT1/DXT5 mip spans and decoded each mip independently, including mixed 1024 and 2048 sizes. Preserved original index ranges, texture identity, original material bytes and sampler mapping. All three new programs passed offline GLSL linking and Mesa linked and drew them. Each slot responded to light, flat-normal and nonmetal controls. M00/0 drew 420 triangles with 703 covered pixels. M03/0 and M03/1 drew 456 and 2,872 triangles with 4,456 and 3,301 covered pixels separately. Their shared-depth composite matched the union at 7,022 pixels with 735 overlap. Both slots retained their exclusive colors and each composite pixel matched a source slot. GFX119 M02 lit output repeated byte-for-byte. Safe evidence `gfxlab/evidence/20261111_gfx123_multimaterial_forward_mesa_safe.json`.

Private portable packs have shader, indexed mesh, buffers, mip layout and readbacks for the three slots, plus a composite reference. The GFX120 Android shell still expects the prior one-slot and 1024-size fixture, so the new packs need the multi-slot Android runner. Remaining Windows reference for these models, original pass states and animation are open. No new APK sent to the owner. `phase_closed=false`.

