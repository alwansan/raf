# B11 transient GitHub coordination incidents — resolved

Session 20261104T2115Z-B11-bca7 | 2026-11-04T21:24:00Z | impact: no original data or other agent changes lost.

- Contents API 409 race during registration and workflow integration when B agents advanced HEAD; remediation: re-fetch latest HEAD/blob and retry exact edit, never force update.
- Attempted Git tree+commit+expected-lease publish produced transient GitHub GraphQL UNKNOWN responses while branch was changing; orphan Git objects were not branch-visible. Switched to per-file GitHub Contents API create_file with fresh HEAD and retry, then checked actual commit diff.
- Local negative-control fixture incorrectly expected a YAML comment to count as an additional field; corrected the **test**, not production parser. All 12 final tests passed.
- No credentials, sources or private assets logged, no cancelled workflows. Status: closed/recovered. Future: re-read live SHA and use optimistic Contents updates; old orphan candidates must not be force-pushed.
