# ZIP2 original game source — owner direction 2026-11-04

Preferred original input: https://github.com/alwansan/raf/tree/zip2/Raft
Reviewed immutable source commit: 15964ea8f246b6e076ce26b60931ee2e1a9a2385.
Read zip2 only; write source/code/docs only on feature/android-native-port. Protected main/zip/Unity-Editor unchanged.

## Verified inventory and limits
RAFT_FILE_MANIFEST.tsv has366 original files,7789295609 bytes,22 split files. Recursive Git tree is complete (577 entries); all plain file sizes and all split-part summed sizes match manifest. resources.assets manifest SHA87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c matches existing authenticated source pin.
This is structural verification, NOT full7.79GB content SHA verification or successful Unity import. Every restored file must pass original size/SHA before use.

## Use
Fetch pinned zip2 into an isolated checkout with LFS smudge disabled, without switching or overwriting another client's worktree. Read README_ZIP2.txt, RAFT_FILE_MANIFEST.tsv and restore_raft.sh. Run bash restore_raft.sh /absolute/separate/Raft-restored in that checkout. Output must be separate from source and existing projects. Restore only needed providers if bandwidth/disk matters; concatenate part-00000 etc in exact order, verify final size and SHA, then stage under original path. Keep metadata and source hash checks. Never pass split folders as .assets/.resS/.bank files or execute Windows binaries.

Prefer ZIP2 verified reconstruction over new git lfs pull. Reuse already verified local/cache payloads. Do not silently fall back to LFS or claim unavailable payload success. Existing workflows still using LFS require a deliberate adapter/checkout/staging change; this documentation does not convert them automatically. Pin source SHA in experiment records and compare existing original fingerprints; investigate mismatches.

## Migration choice
Keep feature/android-native-port/Raft for now: existing pointer identity and Git blob validators rely on it. Do not copy7.79GB/split trees over it or delete it wholesale. ZIP2 is the external original-data provider; stage restored files in disposable experiment directories. Gradually adapt consumers while retaining original authenticity checks, .meta/GUIDs, scene/material links, kernel ordering and all content.

## All clients and tasks
A1–A15, W1/W2/W3 and recovery helpers: read this notice before further original-data acquisition. Communicate through coordination records; no immediate cross-session delivery is implied. Prioritize substantive water/FFT/shader/color/material/effect restoration and data recovery. Do not spend cycles on repetitive audits when original source progress is possible. Preserve each role's Unity/build restrictions and ongoing jobs. Successful reconstruction does not close rendering/audio/world/device gates.

## Owner B-team update — 4 November2026
Private provider https://github.com/alwansan/raf-archive/releases/tag/Raft-zip2-reconstructed is authorized for acquisition and isolated experiments, not presumed byte-identical. See [source and billing policy](../prompt/coordination/B_TEAM/SOURCES_AND_ACTIONS_AR.md). Metadata comparison of365 mapped original asset names found0 exact original size/digest matches; one original filename not exactly mapped. Multipart transport wrapping is a hypothesis, not yet payload-confirmed. Authenticate the downloaded payload against this pinned manifest before use; do not change fingerprints or delete currentRaft. ZIP2 remains a verified fallback without waiting for archive repair. No token/quota or raw assets are published by this notice.
