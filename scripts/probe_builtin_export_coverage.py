"""Read-only path-bound ShaderLab coverage evidence for an exported file set.

A sampled subset is never proof of a full AssetRipper export. No shader
substitution is performed and no proprietary identities are disclosed.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.restore_builtin_shaders import archive_sources, exported_shader_identity


def inspect(root, archive):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Shader inventory root must be a real directory')
    if any(parent.is_symlink() for parent in root.parents):
        raise ValueError('Symlinked shader inventory root parent')
    # The same SHA-pinned vendor archive verification and declaration decoder
    # used by restoration; never accept a weaker second identity matcher.
    archive = Path(archive)
    if archive.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('Over-limit built-in shader archive')
    vendor, _, _ = archive_sources(archive.read_bytes())
    counts = dict(files=0, empty=0, parseable=0, exact_vendor_matches=0,
                  nonvendor=0, duplicate_declarations=0)
    content_digest = hashlib.sha256()
    path_digest = hashlib.sha256()
    seen = set()
    for shader in sorted(root.rglob('*.shader')):
        relative = shader.relative_to(root)
        if shader.is_symlink() or any(
            p.is_symlink() for p in shader.parents if p == root or root in p.parents
        ):
            raise ValueError('Symlinked shader inventory path')
        if not shader.is_file() or not shader.resolve().is_relative_to(root.resolve()):
            raise ValueError('Unsafe shader inventory path')
        raw = shader.read_bytes()
        content_hash = hashlib.sha256(raw).digest()
        content_digest.update(content_hash)  # keep historic digest for comparison
        relative_bytes = relative.as_posix().encode('utf-8')
        path_digest.update(len(relative_bytes).to_bytes(8, 'big'))
        path_digest.update(relative_bytes)
        path_digest.update(len(raw).to_bytes(8, 'big'))
        path_digest.update(content_hash)
        counts['files'] += 1
        counts['empty'] += not raw
        # Malformed UTF-8 is not silently treated as an unmatched declaration.
        identity = exported_shader_identity(raw.decode('utf-8-sig'))
        if identity is not None:
            counts['parseable'] += 1
            counts['exact_vendor_matches'] += identity in vendor
            counts['nonvendor'] += identity not in vendor
            counts['duplicate_declarations'] += identity in seen
            seen.add(identity)
    if not counts['files']:
        raise ValueError('Empty shader inventory')
    return dict(counts=counts, vendor_identity_count=len(vendor),
                ordered_content_digest=content_digest.hexdigest(),
                path_bound_inventory_digest=path_digest.hexdigest(),
                comment_aware_shaderlab_headers=True,
                lexical_header_counts_only=True,
                original_game_identity_authenticated=False,
                full_export_scope_verified=False,
                shader_names_or_sources_disclosed=False,
                source_modified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--archive', required=True)
    args = parser.parse_args()
    print(json.dumps(inspect(args.source, args.archive), sort_keys=True))


if __name__ == '__main__':
    main()
