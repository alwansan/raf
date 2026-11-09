undefined
## GFX-MULTI-003 third failure and source-original model reselection (20261110-GFX-chat-multi-source-geometry-02)
[42718266273](https://github.com/alwansan/raf/actions/runs/42718266273) completed FAILURE; actual Unity Editor imported M00 and M01, then original M02 fallback 1598 vertices/2095 triangles failed **GFX_MULTI_DEGENERATE_SOURCE_VERTEX_BOUNDS_M02**. This proves Renderer.bounds was not the only issue; extracted original M02's vertices have an unusable spatial range. No APK, signing, Android pixels, or M05 proof.

A source-only fixed-SHA experiment now rejects geometry whose real exported OBJ positions collapse in Unity float32 (or produce impossible viewer transforms). It chooses another original typed Renderer→Mesh→Material→Shader48→Texture chain, maintaining 1material/3 images or 2materials/6 images; no fabricated asset or alternate arbitrary source. New source-selection run must pass before another Unity build.
