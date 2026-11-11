#!/usr/bin/env python3
"""Read-only particle renderer -> material GUID census for Unity YAML trees.

Output is aggregate counts and optionally salted SHA-256 prefixes, never raw
game asset contents. This is structural evidence, not a shader/runtime test.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HEADER = re.compile(r"^--- !u!(\d+) &[^\r\n]*", re.MULTILINE)
MATERIAL_LINE = re.compile(r"^\s*-\s*\{([^{}]*)\}\s*$")
GUID = re.compile(r"(?:^|,)\s*guid:\s*([0-9a-fA-F]{32})\s*(?=,|$)")
FILE_ID = re.compile(r"(?:^|,)\s*fileID:\s*(-?\d+)\s*(?=,|$)")
MAX_BYTES = 32 * 1024 * 1024


def census(root: Path, salt: str = ""):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root_must_be_directory")
    counts = Counter()
    identities = Counter()
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {".prefab", ".unity"}:
            continue
        if path.stat().st_size > MAX_BYTES:
            counts["oversized_files_skipped"] += 1
            continue
        counts["files_scanned"] += 1
        data = path.read_text(encoding="utf-8", errors="replace")
        heads = list(HEADER.finditer(data))
        for index, head in enumerate(heads):
            if head.group(1) != "199":  # Unity ParticleSystemRenderer class ID
                continue
            counts["particle_renderers"] += 1
            doc = data[head.end():heads[index + 1].start() if index + 1 < len(heads) else len(data)]
            match = re.search(r"(?m)^[ \t]*m_Materials:[ \t]*([^\r\n]*)(?:\r?\n|$)", doc)
            if not match:
                counts["renderers_without_material_list"] += 1
                continue
            inline = match.group(1).strip()
            entries = []
            if inline:
                # Unity YAML supports flow-style material arrays as well as block lists.
                if inline == "[]":
                    counts["renderers_with_empty_material_list"] += 1
                    continue
                if not (inline.startswith("[") and inline.endswith("]")):
                    counts["unsupported_inline_material_lists"] += 1
                    continue
                # Require a comma between maps; stripping braces alone would
                # incorrectly accept malformed "[{...}{...}]" as two slots.
                body = inline[1:-1].strip()
                refs = []
                malformed = False
                while body:
                    item = re.match(r"^\{[^{}]*\}", body)
                    if item is None:
                        malformed = True
                        break
                    refs.append(item.group())
                    body = body[item.end():].lstrip()
                    if not body:
                        break
                    if not body.startswith(","):
                        malformed = True
                        break
                    body = body[1:].lstrip()
                    if not body:  # trailing comma is not a valid Unity YAML array
                        malformed = True
                        break
                if not refs or body or malformed:
                    counts["unsupported_inline_material_lists"] += 1
                    continue
                entries = ["- " + ref for ref in refs]
            else:
                # Block sequence items must be nested beneath m_Materials.
                # A later sibling YAML list (e.g. m_SubEmitters) is not a
                # material slot, even if its entries also begin with "-".
                # Unity's indentless block sequences permit '-' at the same
                # indentation as m_Materials; a sibling mapping key still
                # terminates this sequence before its own list is read.
                material_indent = len(match.group(0).split("m_Materials:", 1)[0])
                tail = doc[match.end():]
                for line in tail.splitlines():
                    if not line.strip():
                        continue
                    item_indent = len(line) - len(line.lstrip(" \t"))
                    if item_indent < material_indent or not line.lstrip().startswith("-"):
                        break
                    entries.append(line)
            if not entries:
                counts["renderers_with_empty_material_list"] += 1
            for line in entries:
                block = MATERIAL_LINE.match(line)
                if not block:
                    counts["unparsed_material_entries"] += 1
                    continue
                ref = block.group(1)
                fid = FILE_ID.search(ref)
                guid = GUID.search(ref)
                if not fid:
                    counts["entries_without_fileID"] += 1
                elif fid.group(1) == "0":
                    counts["null_material_slots"] += 1
                elif guid:
                    counts["external_material_slots"] += 1
                    digest = hashlib.sha256((salt + guid.group(1).lower()).encode()).hexdigest()[:16]
                    identities[digest] += 1
                else:
                    counts["local_or_builtin_material_slots"] += 1
    return {
        "status": "STATIC_PARTIAL_TREE_ONLY",
        "counts": dict(sorted(counts.items())),
        "external_material_guid_hashes": [
            {"sha256_prefix16": key, "slots": value} for key, value in sorted(identities.items())
        ],
        "limitations": "Only YAML ParticleSystemRenderer class 199 and inline m_Materials entries; no binary assets, shader/texture binding, GPU/phone proof. Unsalted hashes may be correlatable; use private salt for published reports."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--salt", default="")
    args = parser.parse_args()
    print(json.dumps(census(args.root, args.salt), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
