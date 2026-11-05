# T4 → T5 | authentic SaveAndLoad world-RGD factory return-site evidence

Session 20261105T1713Z-T4-chat-original-rgd-return-sites-j7q4, origin chat, issue LOCAL-005.

[CI42072718216](https://github.com/alwansan/raf/actions/runs/42072718216) SUCCESS 50/50, with .NET8 Mono.Cecil original read-only IL input (owner ZIP2 commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385; 3,211,776 bytes; SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e). Wrong source byte rejected.

The exact original ZERO-argument SaveAndLoad instance method feeding SaveWorld's derived-RGD local has ONE lexical return immediately preceded by a derived-RGD local load. Original method contains 2 derived-RGD local slots, 1 direct derived-RGD constructor site, 1 call returning derived RGD, 34 conditional branches, 10 null literal loads, and 0 explicit throw/rethrow sites. The method's return is not immediately preceded by a null literal or constructor/call. None of this is path-sensitive, proves that a particular constructor or call initialized the returned local, proves the actual return value non-null, or executes original Save. No Android game device test.

Next T4 narrow trace: the returned local's compiled write sites under branch ambiguity, not inventing a game world or substituting shipped StreamingAssets/Data.rgd. If signed T5 native [run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) completes, assess real delivered APK/OBB/XAPK and have owner test offline playable world, real nonzero .rgd save, full process exit, same-world playable reopen. Run remains in_progress in Unity Editor at latest read, not a device pass. No Unity build duplicates/cancellations, no audio/Settings/touch changes.

[Detailed report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T4_ORIGINAL_RGD_RETURN_SITES_2026-11-05.md). T4 scheduled JSONL overflow work separate and not touched. LOCAL-005 OPEN, NOT_READY 0/3.