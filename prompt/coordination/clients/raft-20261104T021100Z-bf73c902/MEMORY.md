

## BuildFix authenticated graphics reuse — 4 November 2026
BuildFix changed graphics acquisition to reuse regular files only after original size AND SHA256 match; missing/tampered files remain acquisition candidates, symlinks fail closed, and full final authentication remains mandatory. Two local regression tests passed (valid reuse, same-size tamper, missing/truncated and symlink rejection). No Unity/native request or new APK. Native41741108965 shader/export-lineage blocker remains OPEN; NOT_READY. Next integrate ZIP2 for remaining missing graphics owners and resolve original-to-export shader lineage with W1/We.
