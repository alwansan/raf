# A10 — ZIP2 authentic original RGD metadata compatibility checkpoint (4 November 2026)

## Goal and original inputs

CPU-only, safe metadata inspection of the authentic game seed `Raft/Raft_Data/StreamingAssets/Data.rgd` and original managed `Raft/Raft_Data/Managed/Assembly-CSharp.dll`, both acquired **read-only** from `zip2` pinned at `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. This is an original-data investigation in LOCAL-005, not an Android runtime change.

- RGD bytes **2,941**, original SHA-256 `b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba`.
- Original managed assembly bytes **3,211,776**, original SHA-256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- Isolated workflow: [raft-a10-zip2-original-rgd-nrbf.yml](../.github/workflows/raft-a10-zip2-original-rgd-nrbf.yml). Pinned source sparse checkouts, `lfs: false`; no original binary committed to feature branch, no original source or field/value contents logged.
- Safe project: [OriginalRgdProbe.csproj](../tests/a10-original-rgd-nrbf/OriginalRgdProbe.csproj), [Program.cs](../tests/a10-original-rgd-nrbf/Program.cs), `System.Formats.Nrbf 10.0.14` for record-only decoding and .NET `PEReader` for metadata-only assembly inspection. The tool never executes `BinaryFormatter.Deserialize`, loads game types or executes a Windows/Unity binary.

## Evidence

- [Baseline CI41734043230](https://github.com/alwansan/raf/actions/runs/41734043230), exact workflow source `098695be3b7db49d1d08e275b70539e041b42be5`: **SUCCESS**. Original RGD source hash matched; valid NRBF `ClassWithMembersAndTypes` root, all original 2,941 bytes consumed, root type fingerprint `28cc5a313f1677b14325312e7a409329e6678e7f81c5838f8f4922e72b0a9307`, bad SHA/header/truncation rejected 3/3. No executable deserialization.
- [Assembly metadata CI41734409921](https://github.com/alwansan/raf/actions/runs/41734409921), source `66af65b82a57f21292dfa2629c3b7832e78eeaa6`: **SUCCESS**. Both source SHA checks matched; root type identified among 3,033 original `Assembly-CSharp` metadata type definitions. Root has one serialized member; corresponding original type declares one field; direct names intersect 0. Four negative controls rejected, including wrong original assembly hash.
- [Extended type classification CI41734609973](https://github.com/alwansan/raf/actions/runs/41734609973), source [951e25e](https://github.com/alwansan/raf/commit/951e25e213160c442bd10a47631242d6fffcdf5d): **SUCCESS**. Original payload is decodable to the same root type and consumes all bytes, 4/4 negative controls rejected. Matching original managed type: **one declared field, one serialized root member, zero exact field-name matches, zero properties, zero exact property-name matches, and no direct `ISerializable` interface** (in the verified metadata reader).
- Intermediate [CI41734377772](https://github.com/alwansan/raf/actions/runs/41734377772) failed on the transient revision in which code required new assembly args but the workflow still supplied prior two args. Both files were then updated and CI41734409921/41734609973 passed. This was a test wiring mismatch, not authentic data decoding failure.

## Interpretation and honest limits

This authentic source test establishes that the original RGD file can be decoded as NRBF data **without constructing game objects** and its root type exists in the exact original game DLL. The one-member name mismatch is a concrete potential versioning/custom-serialization/field-identity question for follow-up; it **does not prove** default BinaryFormatter can or cannot instantiate the object, that the object is a live saved world, or that Unity's original `SaveAndLoad` path can load/save/resume it. Original input might use an intermediary container or compatibility rules not visible in simple field-name comparison. Do not rewrite serialized members or change the file schema based on this finding.

Future relevant source work: compare the original save and load call sites, class serialization attributes/possible surrogates and canonical RGD producer/consumer, then test a genuinely generated phone world once authorized candidate builds exist. Keep save bytes, GUIDs, metadata, original data and LEFT Mouse0 behavior unchanged. This session did **not** run Unity, generate APK/OBB/XAPK/Release, change scheduled tasks, edit protected branches or transfer any LFS data.

Overall **LOCAL-005 remains OPEN**, WATER-001/RENDER-002/FFT-FORMAT-009 and other prebuild blockers remain open, **NOT_READY, 0/3** complete independent readiness reviews and no immutable build candidate is validated by this work.
