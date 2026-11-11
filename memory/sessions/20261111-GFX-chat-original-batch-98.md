# GFX141 session — 2026-11-11, origin=chat

Worker: GFX-LAB. Branch: experiment/android-graphics-rootcause ONLY. Parent commit: 9bc5a85a980f119ee1f31bf0e7e3e3906fba94a9.

Goal: reconstruct from immutable zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 every original controlled source asset needed for GFX124's nine cases and 51 readbacks. Install pinned translation toolchain; render private original Mesa references, package through the existing production packer, sign real Android runner with temporary v3 debug signature, check all embedded fixture bytes after signing. Upload **only source-safe aggregate JSON**, never original game assets, raw captures, model, shader, mip textures, or source-original APK. Delete temporary signed APK and source stage. This workflow does not deliver an APK yet. No actions against main, zip2 or T-team branches.

Files: gfxlab/tools/gfx141_stage_original.py; gfxlab/tools/gfx141_compose_original.py; gfxlab/tools/gfx141_compile_shell.sh; .github/workflows/gfxlab-multi141-original-private.yml.

Status: Initial CI execution pending after this commit. Continue by inspecting run logs and making minimal fixes. Success is not assumed. If it passes, solve secure user transfer of original APK separately. Retain original Unity Runtime/pass/animation and PC scene parity gates. phase_closed=false.
