#!/usr/bin/env python3
"""Recover empty ILSpy project files from exact original top-level type identities.

Focused decompilation supplies the original code; no method bodies are invented.
Nonempty source files and all .meta files are retained unchanged.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess


def original_type_index(assembly):
    import dnfile
    pe = dnfile.dnPE(str(assembly))
    nested = {id(row.NestedClass.row) for row in (pe.net.mdtables.NestedClass or [])}
    result = defaultdict(list)
    for row in pe.net.mdtables.TypeDef:
        if id(row) in nested or str(row.TypeName) == '<Module>':
            continue
        namespace, name = str(row.TypeNamespace), str(row.TypeName)
        result[(namespace, name.split('`', 1)[0])].append(namespace + '.' + name if namespace else name)
    return dict(result)


def recover(root, identities, decompile):
    sources = sorted(root.rglob('*.cs'))
    empty = [path for path in sources if not path.read_text(encoding='utf-8-sig').strip()]
    metas = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob('*.meta')}
    plans = []
    for path in empty:
        relative = path.relative_to(root)
        namespace = '' if relative.parent == Path('.') else relative.parent.as_posix().replace('/', '.')
        candidates = identities.get((namespace, path.stem), [])
        if len(candidates) != 1:
            raise ValueError('Empty source does not have one exact original top-level type identity')
        text = decompile(candidates[0])
        declaration = re.search(r'\b(?:class|struct|enum|interface)\s+@?' + re.escape(path.stem) + r'(?:\s|[<:{])', text)
        delegate = re.search(r'\bdelegate\b[^;{}\n]*\b@?' + re.escape(path.stem) + r'\s*(?:<[^>\n]+>)?\s*\(', text)
        ns = re.search(r'(?m)^\s*namespace\s+([\w.]+)\s*\{', text)
        if not (declaration or delegate) or (ns[1] if ns else '') != namespace:
            raise ValueError('Focused decompilation does not match the original source identity')
        plans.append((path, text))
    for path, _ in plans:
        if path.read_text(encoding='utf-8-sig').strip():
            raise ValueError('Empty source changed while recovery was being prepared')
    for path, text in plans:
        path.write_text(text, encoding='utf8')
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != digest for path, digest in metas.items()):
        raise RuntimeError('Original source meta changed')
    remaining = sum(not path.read_text(encoding='utf-8-sig').strip() for path in sources)
    if remaining:
        raise ValueError('Original project sources remain empty')
    report = {'source_files': len(sources), 'empty_sources_before': len(empty),
              'focused_original_sources_recovered': len(plans), 'empty_sources_after': remaining,
              'meta_bytes_unchanged': True}
    print('RAFT_ILSPY_EMPTY_SOURCE_RECOVERY ' + json.dumps(report, sort_keys=True))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--assembly', type=Path, required=True)
    parser.add_argument('--ilspy', type=Path, required=True)
    args = parser.parse_args()
    def decompile(identity):
        result = subprocess.run([str(args.ilspy.resolve()), '-lv', 'CSharp9_0', '-t', identity,
                                 str(args.assembly.resolve())], check=True, capture_output=True, text=True, timeout=180)
        return result.stdout
    recover(args.root, original_type_index(args.assembly), decompile)
