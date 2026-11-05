# T4 → T5: original shipped Data.rgd is not a Save(RGD) roundtrip seed

origin: chat; session_id: 20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8; issue_id: LOCAL-005

**Evidence:** https://github.com/alwansan/raf/actions/runs/42047540260 — SUCCESS, 16/16 synthetic validators, original exact ZIP2 DLL (3,211,776B, SHA256 0a6f0527…) and shipped StreamingAssets/Data.rgd (2,941B, SHA256 b2785187…), 151 sibling managed assemblies authenticated. Actual shipped seed was loaded by original CLR method as demonstrated independently in CI42043768798.

New authenticated compiled-IL inspection found the original nonpublic `Save(string, RGD)` shape but the CLR root of the **shipped seed** is a different type than the `RGD` Save argument. Bounded result `SHIPPED_SEED_ROOT_DIFFERS_FROM_ORIGINAL_RGD_SAVE_ARGUMENT`; guard **refused execution**, original_private_Save_invoked=false, no generated .rgd. This is neither Save serialization failure nor proof of Android game-world format incompatibility.

**Integration consequence:** Do NOT use shipped `StreamingAssets/Data.rgd` as the world save test fixture, do NOT substitute or construct a fake RGD just to satisfy reflection, do NOT relax Save manifest/IL safety, and do NOT claim generic `Load<T>` of the shipped seed proves save/reopen of a world. The earlier authentic Load<T> result stays true for that shipped root type only.

**Next true gate:** one T5-coordinated immutable signed Unity ARM64 test APK with B07 firstMoveNext, T4 originalCompletionAssigned and Save/Load.argumentFileSnapshot and Load.caughtException, B50 Steam local guards. Owner creates a *playable* offline raft, does normal game Save to real game-generated RGD, fully exits and relaunches same installation, reopens same world to playable. Correlate ordered JSONL with T4 source-free verifier (CI42043385806), source SHA/build identity and actual player-state observation. Need genuine current native package; APK86 predates these source fixes.

No native/Unity build was started or cancelled by T4; no game assets, .meta, original RGD data, audio/Settings or deferred touch modified. LOCAL-005 OPEN, NOT_READY 0/3.
