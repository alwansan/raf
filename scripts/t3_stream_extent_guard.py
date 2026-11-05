"""Validate metadata-only Texture2D stream ranges against authenticated provider lengths."""
from collections import defaultdict

def validate_extents(provider_sizes, extents):
    """Fail closed on malformed/out-of-bounds ranges; return aggregate statistics."""
    if not isinstance(provider_sizes, dict):
        raise ValueError("provider_sizes must be a dictionary")
    for name, length in provider_sizes.items():
        if not isinstance(name, str) or not name or type(length) is not int or length < 0:
            raise ValueError("invalid provider manifest")
    grouped = defaultdict(list)
    count = 0
    for item in extents:
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError("invalid extent tuple")
        name, offset, size = item
        if name not in provider_sizes or type(offset) is not int or type(size) is not int:
            raise ValueError("unresolved provider or invalid extent types")
        if offset < 0 or size <= 0 or offset > provider_sizes[name] or size > provider_sizes[name] - offset:
            raise ValueError("out-of-bounds stream extent")
        grouped[name].append((offset, offset + size))
        count += 1
    overlaps = duplicates = 0
    for ranges in grouped.values():
        ranges.sort()
        prior_start, prior_end = -1, -1
        for start, end in ranges:
            if start == prior_start and end == prior_end:
                duplicates += 1
            elif start < prior_end:
                overlaps += 1
            if end > prior_end:
                prior_start, prior_end = start, end
    return {"extents": count, "providers": len(grouped), "partial_overlaps": overlaps, "duplicate_ranges": duplicates}
