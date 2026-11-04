# B03 — Archive transport original-byte intake (2026-11-04)

## Purpose

Original water/FFT shader and color/material restore tooling must never trust a renamed GitHub release asset, an outer asset digest, or a guessed fixed number of wrapper bytes. The currently observed private archive metadata differs from the pinned ZIP2 manifest for 365 mapped names; multipart is only a hypothesis. ZIP2 remains the primary authenticated source.

## Result and usage

`scripts/b03_verify_archive_payload.py` is a **staging helper**, not a replacement for ZIP2. It reads the exact 5-column `RAFT_FILE_MANIFEST.tsv` pinned at source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, selects an exact relative path, and accepts either raw original data or one strictly framed multipart/form-data part. It streams the **exact original byte count**, then validates the **original SHA-256** before atomically linking into a separate destination, refusing overwrite and symlinked parent paths. It does not log private data, infer archive filenames, or repair broken game shaders itself.

```bash
mkdir -p /tmp/raft-b03-staging
python3 scripts/b03_verify_archive_payload.py \
  --input /private/downloaded-release-asset.bin \
  --manifest /private/pinned-zip2/RAFT_FILE_MANIFEST.tsv \
  --relative-path 'Raft_Data/selected.assets' \
  --stage /tmp/raft-b03-staging
```

Use the manifest's *actual* relative path rather than the illustrative one above. Do not publish `/tmp/raft-b03-staging` or its contents. No private asset was downloaded by this change; there is **no live archive payload SHA match claimed**.

## Test boundaries

15 local synthetic Python unittest cases passed: raw and multipart positives, SHA-tampered raw and wrapped payloads, truncation, extra multipart data/part, malformed header/boundary, overlong or short payload, traversal, duplicate/missing manifest records, symlink input/parent and overwrite protections. Tests do **not** validate Unity import, framebuffer pixels, FFT kernels, or Android devices.

The next authoritative step is to download **one small** approved release asset in an authorized private environment, retain its outer asset id/size/digest, parse and compare its *canonical* payload to the pinned ZIP2 manifest. If it fails, record exact safe failure category; continue using ZIP2 without changing original pins. Don't spend CI minutes or bandwidth on 370 downloads before a small sample passes.
