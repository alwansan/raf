# T2 — Authentic Foam Blit per-pass roles (source-only)

Date: 2026-11-07 UTC. Source: [GitHub Actions 42308583977](https://github.com/alwansan/raf/actions/runs/42308583977), source commit `4e5f4d24e0049518928b0fe47db8adfa3b853db7`, safe artifact ID `13547696649`, ZIP SHA256 `e4a31957a9637656dba391582f21a9513d1fc03786723694793731d23233c22f` (matches GitHub artifact digest). Original ZIP2 shader name and managed assembly SHA authenticated by report flags. No proprietary source copied.

Downloaded the **actual safe artifact** (not merely the workflow success flag) and inspected `t2-foam-resultflow-safe.json`. It records 19,118 original compiled method bodies, 491,490 IL instructions, one exact original Foam `Shader.Find` call and one original Foam Shader field -> Material constructor site. The tracked original Material field has 13 read instructions in four reader methods. Two original Graphics.Blit material sites use explicit pass indices; exactly one is pass 0 and one pass 1.

| Explicit pass | Source type from typed IL | Destination type from typed IL |
| --- | --- | --- |
| 0 | RenderTexture (1/1) | RenderTexture (1/1) |
| 1 | UNKNOWN (1/1) | UNKNOWN (1/1) |

Aggregate counters reconcile: source Texture=0, RenderTexture=1, unknown=1; destination RenderTexture=1, null=0, unknown=1. No other pass literal or unknown pass index was observed. **This supersedes the earlier four-permutation concern about aggregated counters**: the original safe report already contains *per-pass* counters, so pass 0 roles are assigned. Pass 1 still has unresolved provenance; UNKNOWN means the bounded static IL analyzer did not resolve it, **not** that Unity lacks the resources. Typed role evidence does not establish actual RenderTexture instance identity, dimensions, CB0 upload, material GUID binding, shader compilation, runtime water, or device pixels.

Source-free schema fixture for `scripts/t2_foam_pass_role_matrix.py`:

```json
{"schema_version":1,"passes":[{"pass":0,"source":"RenderTexture","destination":"RenderTexture"},{"pass":1,"source":"UNKNOWN","destination":"UNKNOWN"}],"aggregates":{"source":{"Texture":0,"RenderTexture":1,"UNKNOWN":1},"destination":{"RenderTexture":1,"NULL":0,"UNKNOWN":1}}}
```

Next: trace the two UNKNOWN pass-1 argument producers in the authenticated managed IL using a bounded intra-method stack/dataflow analysis, preserving control-flow uncertainty. Verify the resulting typed per-pass report against the strict schema, then investigate CB0 and Unity ShaderLab integration. Do not build Android or claim a water fix from this source-only finding. WATER-001 remains OPEN.
