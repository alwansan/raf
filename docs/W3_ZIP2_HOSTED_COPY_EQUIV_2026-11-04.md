# W3 — zip2 hosted-copy equivalence: 82/82 owner-size identity + byte-identity of the two pinned owners — 4 November 2026

Eleventh W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T164000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-zip2-equivalence.md) under the owner's explicit authorization to use the `zip2` branch game files (`Raft/`). Read-only; methodology is metadata-first over the public repo tree plus a streaming download of only the two byte-pinned owners. No full checkout, no LFS smudge of the 7.3GB set, no edits to either branch. Two probes + 2/2 model tests (all prior suites remain green); both runs exit 0 fail-closed. Artifacts: [W3_ZIP2_HOSTED_COPY_EQUIV_2026-11-04.json](../docs/W3_ZIP2_HOSTED_COPY_EQUIV_2026-11-04.json) SHA-256 `7ba7d51a02cddc9ce90c6fa935069a2f5f0d05da59a05df23fd4601b239bfdbe` and [W3_ZIP2_PIN_BYTES_2026-11-04.json](../docs/W3_ZIP2_PIN_BYTES_2026-11-04.json) SHA-256 `46e281cc123c87b05cdb44e7efc95567dccc22743326e6f2aac024dd129da176` (public repo file paths only; no shader/asset names).

## Structural discovery (documented before verification)

`Raft/Raft_Data@zip2` hosts the same 82-owner game-data set as the feature branch/local originals, with **two storage-convention differences that carry no size delta**:

| storage kind | owners | notes |
|---|---|---|
| split into ≤45MB part trees (with README) on zip2 | **5** | `resources.assets`, `sharedassets0.assets`, `sharedassets36.assets` (.assets family) **and** `level30`, `level34` (bare-name levels) |
| direct blob on both branches | 77 | levels keep their bare names on *both* sides (`level0`, not `level0.assets`) — the naming convention is identical across local originals / feature branch / zip2 |

An interim claim in this session's scratch analysis that zip2 shared a "bare level-name difference from the feature branch" was wrong and was corrected pre-publication: the feature branch itself already stores levels bare, so no rename mapping exists at all — the owner sets are name-identical.

## Results

**Metadata equivalence (82 owners, no bulk download):** feature-branch content sizes (from committed LFS pointer texts / direct blob sizes via local `git`) vs zip2 sizes (blob size, or sum of split-part sizes) → **82/82 size-equal**, fail-closed abort on any mismatch; split-owner set exactly the five listed above with part sums matching the pinned sizes exactly (`resources.assets` 111,533,516; `sharedassets0.assets` 115,978,112).

**Byte identity (the two pinned owners only):** a streaming concatenation of the zip2 part blobs re-derives exactly the committed pins — `sha_match: true` for both — completing a triangle of evidence:

- **local originals ⇄ repo LFS stream:** covered by CI run 41828539269 (step 10).
- **repo LFS stream pins ⇄ zip2 hosted copies:** this step (metadata for all 82 owners; bytes for the two pinned ones — streamed, not fetched through git).

Both artifacts carry all negative controls true (`fail_closed_on_any_mismatch`, `no_bulk_download_performed`, `streamed_no_full_checkout`, `aggregate_only_publication`).

## Limits

Read-only equivalence: provenance/metadata and two pinned byte-identities only. Not claimed: per-byte identity for the other 80 owners (sizes only, honest label), any unpacking/rezipping, and no rendering claims of any kind. Peer lanes untouched. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; 0/3 reviews.** Flaky-link handling recorded honestly: the byte probe's first execution aborted mid-stream on a host connection error; a re-download with a per-owner clean-restart policy (fresh hasher, no partial-byte reuse) completed exit 0 — only the successful, self-contained run is committed as durable.
