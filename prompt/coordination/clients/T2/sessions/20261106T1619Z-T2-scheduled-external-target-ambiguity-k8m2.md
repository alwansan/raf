# T2 — source-only external Shader PPtr ambiguity guard
session_id: 20261106T1619Z-T2-scheduled-external-target-ambiguity-k8m2
origin: scheduled
base_sha: 195a2f0f85448ed39bbc6d792c942b8728e8e085
resumed_from_sessions: 20261106T1544Z-T2-chat-four-original-owners-pptr-6a71; 20261106T1518Z-T2-scheduled-original-foam-identity-reconcile-p7k4
work: prompt/coordination/work/WATER-001/T2-20261106T1619Z-T2-scheduled-external-target-ambiguity-k8m2.json
owner phone evidence: https://github.com/alwansan/raf/actions/runs/42058825739 — world enter/save/reopen works on artifact; water errors remain.
original baseline: https://github.com/alwansan/raf/actions/runs/42247200163 — four original SHA-pinned owners, two unresolved external Shader PPtrs.
result: added scripts/t2_external_pptr_manifest_resolver.py at b2c64ae7ccf4e0bf802bc55b44b8e8eeb2dcc63b and tests/test_t2_external_pptr_manifest_resolver.py at 4a5b87ac06686bc12a73c29c9864349d2bb34dc0. Local source-free Python unittest: 7/7 PASS, testing unique candidate, absent, ambiguous, unpinned, traversal, invalid reference and malformed unrelated manifest entry. Filename+SHA is only a candidate; Unity external GUID and typed Shader PathID still require private verification.
limits: no original 366-owner manifest run, no Unity/Adreno/device test, no private game data output, no game ShaderLab/audio/Settings/touch/input/scene/.meta edits, no CI duplicate. WATER-001 OPEN.
next: private ZIP2-pinned two-reference lookup across immutable 366-owner manifest, reject collisions, stage verified candidate bytes and check original FileIdentifier GUID and Shader PathID before claiming Foam binding. Coordinate T1/T3.
