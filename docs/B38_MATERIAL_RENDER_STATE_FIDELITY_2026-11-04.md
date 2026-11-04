# B38 — original Material render-state parity lane (4 November 2026)

RENDER-002 remains OPEN. Other independent guards already cover shader/keyword state (B43), Material float/int SavedProperties (B22), Material colors (B44), textures/UV (B05), Renderer pointers (B03). This guard handles **top-level Material draw/lighting flags** omitted from those prior checks: m_CustomRenderQueue, m_LightmapFlags, m_EnableInstancingVariants and m_DoubleSidedGI.

## Source and trust boundary
- Original source: only providers size/SHA-pinned by SHADER_OWNERS, staged from ZIP2 pin15964ea8f246b6e076ce26b60931ee2e1a9a2385.
- Only exact same-export trace maps original (owner,pathID) to actual exported (GUID,fileID). No name-derived GUID or different-run guesses.
- Original Boolean and exported integer0/1 flags normalized semantically; render queue/lightmap values compared exactly. Missing fields and duplicate YAML mappings are rejected. SafeLoader never executes constructors.
- Output: aggregate mismatch counts only; no serialized material/source names or bytes. Read-only checker; no .meta, scenes, render queues, graphics assets or Unity candidate changed.
- Private authenticated source-to-export run NOT performed in this synthetic experiment. Green tests cannot establish actual Raft Material parity, shader pixels or Adreno, and do not fix white textures automatically.
- Owner-confirmed audio and Settings preserved, touch/layout deferred; RENDER-002 OPEN, NOT_READY0/3.
