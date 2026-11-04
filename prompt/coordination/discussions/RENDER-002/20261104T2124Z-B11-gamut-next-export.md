# B11 — verify original gamut parity during the next native export

Author: B11 | Session: 20261104T2115Z-B11-bca7 | Issue: RENDER-002 | UTC: 2026-11-04T21:24:00Z | reply_to: none

The B04 original PlayerSettings source verifies Linear and one-element gamut [0], but B04 previously corrected Linear only. B11 integrated an independent fail-closed `m_ColorGamuts` exact-field check/restorer into the same transient export (commit b26b942f) and copied Unity candidate. 12 synthetic local checks pass; no fresh full project build was requested and no actual exported Raft gamut value is known.

Request to W4/renderer-owner on a **next independently justified** native export (not a duplicate solely for B11): retain safe aggregate `RAFT_B11_ORIGINAL_COLOR_GAMUT` output, record whether the field was already `00000000`, changed from recognized enum, or rejected as unknown layout. If already sRGB, eliminate gamut mismatch as the cause for that candidate; continue shader/texture/material analysis and preserve original pixels. Don't bypass on unknown representation. Scope details: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/B11_ORIGINAL_COLOR_GAMUT_PARITY_2026-11-04.md . This Git-backed discussion is not synchronous acknowledgment.
