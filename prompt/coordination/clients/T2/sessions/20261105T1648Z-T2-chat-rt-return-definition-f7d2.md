# T2 chat — Foam RenderTexture-returning element call target

- session_id: `20261105T1648Z-T2-chat-rt-return-definition-f7d2`, origin: `chat`, owner: `T2`, issue: `WATER-001`, status: active.
- base_sha: `f191f352f251bdcea3460f3f142bb5f5aa07764c`.
- work recorded BEFORE code: `prompt/coordination/work/WATER-001/T2-20261105T1648Z-T2-chat-rt-return-definition-f7d2-return-method.json` at `5cf98dbd71fcb45bbfa92debbf5d87e9ddc87336`.
- resumed_from_sessions: `20261105T1611Z-T2-chat-foam-length-source-9ab4` and `20261105T1623Z-T2-scheduled-caller-origin-6f2d`.
- authenticated original source baseline: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original 3,211,776-byte managed `Assembly-CSharp.dll` SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- [CI42065864809](https://github.com/alwansan/raf/actions/runs/42065864809) SUCCESS: actual original source-verifiable `stelem.ref` value is a direct `call` whose declared return is `UnityEngine.RenderTexture`. Earlier [CI42064653958](https://github.com/alwansan/raf/actions/runs/42064653958) SUCCESS: four original private `Texture(int)` indices structurally in bounds for positive literal actual allocation length; no runtime/drawn pixel proof.
- new hypothesis / experiment_key: `T2|ZIP2-15964ea8|managed-DLL-0a6f0527|exact-Foam-stelem-rendertexture-callee-return-body-v1`. Capture precise original same-block call MethodReference feeding verified element store, identify exact internal original method declaration or external UnityEngine call. If internal, inspect body return predecessor conservatively; no original methods/names/source IL or private numeric constants/digests output.
- intended files: own `FoamByrefElementValueOrigin.cs`, new `FoamRenderTextureReturnBody.cs`, own `Program.cs`, own managed-literals workflow, work/experiments/session/evidence. No gameplay assets, .meta/GUID, ShaderLab, FMOD/Settings or deferred touch.
- coordination: [T1 FFT run42066983894](https://github.com/alwansan/raf/actions/runs/42066983894) and [T5 native run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) separately active; no T2 managed CI queued at reservation. Don't cancel or duplicate.
- next: implement source-free signed/typed internal and external decoy controls, run SHA-genuine original Cecil CI. Work remains active; overarching WATER-001 OPEN, Raft NOT_READY0/3.
