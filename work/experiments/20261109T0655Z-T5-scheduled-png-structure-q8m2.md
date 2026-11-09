# T5 scoped work 20261109T0655Z-T5-scheduled-png-structure-q8m2
origin=scheduled
baseline_sha=7bcc268625def40e3d40c877f344e3066c5f2b8c
scope: scripts/t5_verify_png_bytes.py and isolated clients/T5/sessions/20261109T0655Z-T5-scheduled-png-structure-q8m2.md only.
hypothesis: CRC-valid and zlib-decodable PNG with invalid IHDR color/bit-depth or truncated scanline bytes is incorrectly accepted as image integrity evidence.
experiment_key=T5-PNG-IHDR-SCANLINE-20261109
shared_resource=none; no Unity or APK build.
T4 mouse files, T1/T2 water files and T3 graphics files excluded. Read-only CL and artifact provenance; no visual parity claim.
