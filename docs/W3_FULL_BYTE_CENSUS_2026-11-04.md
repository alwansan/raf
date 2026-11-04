# W3 — full byte census: all 82 owners byte-identical across the identity triangle — 4 November 2026

Twelfth W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T204500Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-full-byte-census.md); it upgrades step 11's honest label — "byte-identity honored for the two pinned owners only, the other 80 size-equal only" — to **full byte identity for all 82 owners**, closing the identity triangle with the strongest evidence available. Read-only at every phase; no branch edits, no LFS smudge, no Unity/build. New script `scripts/probe_w3_full_byte_census.py` (two phases, both fail-closed, resumable by whole owner) + 2/2 model tests (all prior suites remain green). Artifact: [W3_FULL_BYTE_CENSUS_2026-11-04.json](../docs/W3_FULL_BYTE_CENSUS_2026-11-04.json) SHA-256 `4fbd9ab159722a16db25d1c86ef06e5652951e76de9391b3c4bce3cb7378c1fb` (public repo file paths only; no shader/asset names, no decompiled content).

## Phase A — feature ⇄ local (metadata-only, fast, exhibit for free)

For each of the 82 owners: LFS-backed owners' committed pointer `oid sha256:` + `size` **must equal** the local file's SHA-256 + size; direct-blob owners' committed blob SHA-1 **must equal** `git hash-object` of the local file. Result: **0 mismatches / 82** (fail-closed). This was already implicitly relied on by every prior W3 probe; it is now an explicit exhibit.

## Phase B — zip2 ⇄ local (streaming census)

Streamed the zip2 hosted copy for **all 82 owners** (77 direct blobs + 5 split-part trees; parts concatenated in order) and compared per-owner SHA-256 and size against the local originals:

| aspect | value |
|---|---:|
| owners verified | **82 / 82 byte-identical** |
| total streamed bytes | 819,595,355 B (**the 82 owners total ~820MB**; the 7.3GB `Raft_Data` also carries `.resS`/Streaming material outside this owner set — corrected from an interim ~7.3GB read in the scope note) |
| zip2 storage kinds | 77 direct blob / 5 split tree |
| restart policy | fresh full-owner hasher on any transport abort; resume by whole owner only, never partial-byte merge |

Combined with CI run 41828539269 (local ⇄ repo-LFS) and step 11 (pins ⇄ zip2 slots), the identity triangle is now **byte-closed for every one of the 82 owners across all three hosted sources**. Any client can pick any of the three environments and treat the serialized set as a single, proven byte seed.

## Limits

Read-only provenance: no unpacking/rendering claims of any kind; eligibility was limited to the 82 serialized owners (`.assets` + bare `levelN`) — outside materials like `.resS` and StreamingAssets were neither claimed nor required. Peer lanes untouched. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; 0/3 reviews.**
