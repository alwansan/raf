# T4 LOCAL-005 — original shipped Data.rgd true SaveAndLoad.Save → Load<T> experiment

## Question

T4 previously proved that the **compiled original** `SaveAndLoad.Load<T>` can read the immutable shipped `Data.rgd` in .NET 8, but did not test original serialization. This experiment tries the original **instance** `Save(string, RGD)` with the genuinely decoded original root object, with a compiled-IL allowlist and a fresh private throwaway filename, then original `Load<T>` from that new file. The goal is to learn whether the original compiled serializer can execute outside Unity; it is not a user-created world save.

## Strict inputs and isolation

- Source ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; DLL 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`; Data.rgd 2,941 bytes SHA256 `b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba`, plus 151 existing pinned original managed sibling assemblies.
- New .NET8 experimental project under `android-port/Experiments/T4/OriginalRgdSaveRoundtrip/`. Preflight Mono.Cecil 0.11.5 checks exact nonpublic instance `Save(string, original RGD root type)` and its IL; refuses unexpected field reads/writes, external calls, Unity/non-FileManager game reachability or missing `FileManager.CreateFile` + `BinaryFormatter.Serialize` reachability before invocation.
- Output is process-owned temporary directory only; private generated RGD bytes, original save fields and player data never enter git, CI artifact, stdout or report. The created file is deleted after testing even on failure. The original shipped Data.rgd is read-only and never passed to Save as a target.
- No game project source, .meta GUID, Unity assets, Android app or actual user save is modified. Even success cannot close LOCAL-005 or establish offline playable world, same-world relaunch, or Android IL2CPP compatibility.

## Verified result

Pending isolated workflow; record CI ID, method guard classification and runtime outcome. Do not misreport a safety guard refusal as original game serialization failure.
