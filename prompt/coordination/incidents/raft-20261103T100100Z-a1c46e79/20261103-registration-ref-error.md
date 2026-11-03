# A1 registration ref update incident — resolved

Author: raft-20261103T100100Z-a1c46e79; documented UTC: 2026-11-03T10:07:06.360Z
Status: resolved; no branch reset or force
First base: 0911f61430a0ffd74060ff9a39376dd347ff9655
Attempted unattached commit: 79cc48a8d5fe9c265e07775d02c64c041112537b
Failure: GitHub GraphQL UNKNOWN error during update_ref; concurrent HEAD change also observed. Cause unknown; do not assert failed compare-and-swap alone caused the transport error.
Recovery: verified missing client files at HEAD, read newer commit, rebuilt new tree on current HEAD with expected_sha and no force; registration published as cb95d4bb8b736013f996a7583e434775a5160223. Other clients' commits retained.
No running Actions cancelled, no duplicate write, and no branch outside feature/android-native-port touched.
