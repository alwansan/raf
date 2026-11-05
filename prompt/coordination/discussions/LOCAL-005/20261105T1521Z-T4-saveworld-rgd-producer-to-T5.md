# T4 to T5 — original compiled SaveWorld → private Save(RGD) call-source evidence

origin: chat; session_id: 20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2; issue: LOCAL-005

**CI:** https://github.com/alwansan/raf/actions/runs/42053882300 final SUCCESS 22/22 synthetic validator controls and real exact pinned original managed DLL CIL inspection. Original source: ZIP2 SHA15964ea8f246b6e076ce26b60931ee2e1a9a2385, Assembly-CSharp.dll 3,211,776 bytes SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. The wrong source SHA negative control rejected before IL inspection. The code did NOT execute original game methods.

The original SaveWorld and SaveUser each directly call the original private Save(string,RGD) **once**. Neither has a direct new RGD object construction, RGD typed local, or direct generic Load<RGD> call. No direct RGD constructor was observed in any other SaveAndLoad method. Immediate pre-call instructions were not classifiable as a provable RGD producer. This does NOT establish where the RGD instance came from (another class/field/indirect call remains possible).

CI42047540260 separately established shipped StreamingAssets/Data.rgd CLR seed root differs from original world Save method's RGD parameter; do NOT use that shipped seed as a world save fixture, create a fake RGD, or alter serializer/schema/flags based on this.

T5 still needs a coordinated *new* immutable signed native candidate, including existing B50 Steam guard, B07 firstMoveNext, T4 originalCompletionAssigned, Save/Load.argumentFileSnapshot and Load.caughtException. The decisive device test is offline new world actually playable → genuine SaveWorld/SaveUser and real .rgd file → complete process exit → relaunch and same-world playable reopen; use JSONL verifier scripts/t4_verify_device_world_save_log.py after the separate T4 scheduled UTC inversion patch when verified. Record source SHA, build/versionCode and logs without leaking world names or raw file bytes.

Full report: docs/T4_ORIGINAL_SAVEWORLD_RGD_PRODUCER_2026-11-05.md; session prompt/coordination/clients/T4/sessions/20261105T1500Z-T4-chat-saveworld-rgd-producer-h5k2.md. Current LOCAL-005 OPEN; overall NOT_READY 0/3. No native job cancelled/dispatched; audio/Settings untouched, touch deferred.
