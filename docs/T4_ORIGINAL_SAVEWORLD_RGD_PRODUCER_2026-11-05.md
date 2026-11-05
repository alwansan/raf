# T4 LOCAL-005 — authentic compiled SaveWorld RGD argument producer (2026-11-05)

## Hypothesis and contrast with previous original seed test

The authenticated original ZIP2 StreamingAssets/Data.rgd 2,941B is decodable with its own root CLR type, but T4 CI42047540260 proved that root is **not** the RGD argument accepted by the private original `Save(string,RGD)` method. This experiment does **not** serialize a fake RGD. It inspects the actual original `SaveWorld()` CIL to identify its direct edge to the authentic private Save method, and whether the original method contains direct RGD constructor calls/typed locals/field stores. Counts are insufficient to prove that a specific constructed instance traverses that call; no claim of dynamic argument-identity, game save or runtime playability is allowed.

Read-only source: original ZIP2 `alwansan/raf@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, exactly 3,211,776-byte `Assembly-CSharp.dll`, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`. Mono.Cecil v0.11.5 metadata only, .NET8 Ubuntu24.04, no original Unity game source decompiled/published, no original DLL/artifact uploaded, no RGD file read, no game Save called.

New files `android-port/Experiments/T4/OriginalRgdProducerIl/`, `scripts/t4_validate_original_rgd_producer.py`, 16 source-free adversarial controls and isolated workflow `.github/workflows/raft-t4-original-rgd-producer-il.yml`. Zero touch to prior T4 scheduled JSONL UTC task, B14 Save order, original game metadata/source, .meta, Settings/audio or native build pipeline.

## Results

Await actual private GitHub Actions source attestation, bounded original IL counts and synthetic-test conclusion. Never infer SaveWorld runtime execution, Android playability, durable user-generated RGD or world reload from a compiled callsite.
