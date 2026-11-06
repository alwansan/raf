"""Fail-closed external Unity file candidate lookup; no private data logging."""
from pathlib import PurePosixPath
import re

_SHA = re.compile(r"^[0-9a-f]{64}$")


def resolve_external_target(reference_basename, manifest_entries):
    """Return unique pinned candidate, NOT an authenticated Unity GUID/PathID link."""
    if not isinstance(reference_basename, str) or not reference_basename or '/' in reference_basename or '\\' in reference_basename:
        return None
    matches = []
    for entry in manifest_entries:
        if not isinstance(entry, dict):
            return None
        path, digest = entry.get('path'), entry.get('sha256')
        if not isinstance(path, str) or not isinstance(digest, str) or not _SHA.fullmatch(digest):
            return None
        if '..' in PurePosixPath(path).parts or path.startswith('/') or '\\' in path:
            return None
        if PurePosixPath(path).name.casefold() == reference_basename.casefold():
            matches.append((path, digest))
    return matches[0] if len(matches) == 1 else None
