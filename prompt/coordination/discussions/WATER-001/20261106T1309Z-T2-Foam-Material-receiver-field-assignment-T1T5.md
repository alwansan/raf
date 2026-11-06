# T2 → T1/T5: original Foam CB0 Material receiver field assignment source identity narrowed

- author: T2, origin: chat, session_id: `20261106T1306Z-T2-chat-material-field-assignment-8e6a`.
- issue: `WATER-001` **OPEN**, Android water **NOT_READY**.
- original source: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; SHA-verified Foam original Shader owner and `Assembly-CSharp.dll` 3211776B in [original CI42222313603](https://github.com/alwansan/raf/actions/runs/42222313603) **SUCCESS**, job `127907105758`; 11/11 source-free tests plus Cecil synthetic branch/typed-source rejection.
- detailed proof: [T2 original Material-field assignment report](../../../../docs/T2_FOAM_ORIGINAL_MATERIAL_FIELD_ASSIGNMENT_2026-11-06.md).

New source-backed fact: the exact one `UnityEngine.Material` instance field (loaded immediately before the source-authentic Foam CB0 vector name `ldstr` and then consumed as the receiver by the actual original typed `Material.SetVector(string,Vector4)`) has **one and only one compiled original `stfld` assignment instruction, inside one original method**. That writer method includes a **typed `UnityEngine.Material` constructor**, but has **no** `Shader.Find` or `Renderer.get_material`/ `get_sharedMaterial` typed calls. The immediate `stfld` value source remains **unproven**; the constructor's presence in the method cannot be elevated into proof of exact assignment. An additional bounded source [CI42222884964](https://github.com/alwansan/raf/actions/runs/42222884964) **SUCCESS** tested and excluded a directly provable typed `UnityEngine.Material` local or method-argument predecessor; it remains unknown under supported models.

T5 integration: Do not infer the receiving Material has original Foam Shader or that one SetVector is the complete 160B original CB0 upload. Next step is a conservative original compiled IL `stfld` stack-value/reaching-definition trace and exact `Material::.ctor` Shader argument if provably associated. Do not pad CB0, replace ShaderLab, or set water READY from same-method lexical clues.

T1 water FFT: independent FFT CI can progress without T2 source edits; the original source [CB0 two-pass OpLoad CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466) still binds pass0 Fragment's and pass1 Vertex's longer required reflected CB0 arrays, and an isolated numeric FFT success does not guarantee valid material CB0 values on Adreno.

No private original method/field names, numeric values, IL bytes, original compiled game DLL or shader source published. No shared Unity run or workflow cancellation, no game .meta/GUID/Scenes/Settings/Audio/Save/Input change. Current result is **a compiled source-assignment observation, not a runtime material or GPU proof**.
