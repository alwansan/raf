"""B37: source-authenticated private original Cursor.SetCursor callsite census.

Original C# stays in the private CI runner's temporary directory. Only bounded
counts and cryptographic provenance leave the runner, never game C# or paths.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ORIGINAL_DLL_SIZE = 3211776
ORIGINAL_DLL_SHA256 = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"
DIRECT = re.compile(r"\b(?:UnityEngine\s*\.\s*)?Cursor\s*\.\s*SetCursor\s*\(")
UNQUALIFIED = re.compile(r"(?<![\w.])SetCursor\s*\(")
USING_STATIC = re.compile(r"\busing\s+static\s+UnityEngine\s*\.\s*Cursor\s*;")
USING_ALIAS = re.compile(r"\busing\s+\w+\s*=\s*UnityEngine\s*\.\s*Cursor\s*;")


def verify_dll(path, size=ORIGINAL_DLL_SIZE, sha=ORIGINAL_DLL_SHA256):
    if path.is_symlink() or not path.is_file() or path.stat().st_size != size:
        raise ValueError("Expected exact regular original managed DLL")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    if h.hexdigest() != sha:
        raise ValueError("Original DLL SHA mismatch")
    return h.hexdigest()


def code_only(source):
    """Blank C# line/block comments and quoted strings, preserving newlines."""
    output = list(source)
    i, n = 0, len(source)
    while i < n:
        if source.startswith("//", i):
            end = source.find("\n", i)
            end = n if end == -1 else end
        elif source.startswith("/*", i):
            close = source.find("*/", i + 2)
            if close == -1:
                raise ValueError("Unterminated C# block comment")
            end = close + 2
        elif source[i] == '"' or source[i] == "'":
            quote = source[i]
            j = i + 1
            verbatim = quote == '"' and i > 0 and source[i - 1] == "@"
            while j < n:
                if not verbatim and source[j] == "\\":
                    j += 2
                    continue
                if verbatim and source[j:j+2] == '""':
                    j += 2
                    continue
                if source[j] == quote:
                    j += 1
                    break
                j += 1
            else:
                raise ValueError("Unterminated C# quoted token")
            end = j
        else:
            i += 1
            continue
        for k in range(i, min(end, n)):
            if output[k] not in "\r\n":
                output[k] = " "
        i = end
    return "".join(output)



def classify_first_arguments(live):
    """Classify exact call shape without exposing expressions, names or arguments.

    This is a lexical balance check, not runtime source execution.
    """
    flags = []
    for match in DIRECT.finditer(live):
        position = match.end()
        start = position
        nested = 0
        commas = []
        while position < len(live):
            ch = live[position]
            if ch in "([{":
                nested += 1
            elif ch in ")]}":
                if ch == ")" and nested == 0:
                    break
                if nested == 0:
                    raise ValueError("Unbalanced original cursor invocation")
                nested -= 1
            elif ch == "," and nested == 0:
                commas.append(position)
            position += 1
        if position == len(live) or len(commas) != 2:
            raise ValueError("Noncanonical original Cursor.SetCursor arity")
        argument = live[start:commas[0]].strip()
        if not argument:
            raise ValueError("Empty original cursor texture argument")
        flags.append(argument == "null")
    return flags


def scan(root, dll, *, size=ORIGINAL_DLL_SIZE, sha=ORIGINAL_DLL_SHA256):
    digest = verify_dll(dll, size, sha)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe private source root")
    callers = []
    total = aliases = unqualified = count = null_args = 0
    per_source_sha = []
    for path in sorted(root.rglob("*.cs")):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Unsafe or oversized private source")
        parent = path.parent
        while parent != root:
            if parent.is_symlink() or parent == parent.parent:
                raise ValueError("Redirected private source path")
            parent = parent.parent
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        live = code_only(text)
        hits = len(DIRECT.findall(live))
        aliases += len(USING_ALIAS.findall(live)) + len(USING_STATIC.findall(live))
        unqualified += len(UNQUALIFIED.findall(live))
        total += hits
        count += 1
        if hits:
            flags = classify_first_arguments(live)
            if len(flags) != hits:
                raise ValueError('Cursor invocation classification drift')
            null_args += sum(flags)
            per_source_sha.append({'source_sha256': hashlib.sha256(text.encode()).hexdigest(), 'calls': hits, 'literal_null_first_arguments': sum(flags)})
            identity = hashlib.sha256((str(path.relative_to(root)) + "\0" +
                hashlib.sha256(text.encode()).hexdigest()).encode()).hexdigest()
            callers.append((identity, hits))
    if count == 0:
        raise ValueError("Empty original C# export")
    return {
        "schema_version": 1, "original_dll_sha256": digest,
        "source_files_scanned": count,
        "direct_cursor_setcursor_calls": total,
        "direct_callsite_source_files": len(callers),
        "direct_literal_null_texture_arguments": null_args,
        "direct_nonliteral_cursor_texture_arguments": total - null_args,
        "source_digest_callsite_counts": sorted(per_source_sha, key=lambda row: row['source_sha256']),
        "unqualified_setcursor_tokens_including_direct": unqualified,
        "unity_cursor_alias_directives": aliases,
        "caller_identity_digest": hashlib.sha256(json.dumps(sorted(callers)).encode()).hexdigest(),
        "original_csharp_or_paths_published": False,
        "texture_format_root_cause_verified": False,
        "android_device_executed": False,
        "source_modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-managed-dll", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(args.source.resolve()):
        raise ValueError("Sanitized report must remain outside private source")
    result = scan(args.source, args.original_managed_dll)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("B37_ORIGINAL_CURSOR_CALLSITE_AUDIT " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
