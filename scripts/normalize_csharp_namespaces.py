#!/usr/bin/env python3
"""Convert C# 10 file-scoped namespaces to C# 9 block-scoped namespaces.

AssetRipper may emit C# 10 script templates, while Unity 2021.3's C# compiler
expects C# 9. Original assemblies and .meta GUID files are never modified.
Designed for generated temporary Unity project copies, NOT repository game data.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re

NAMESPACE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)namespace[ \t]+"
    r"(?P<name>[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)"
    r"[ \t]*;[ \t]*(?://[^\r\n]*)?(?:\r?\n|$)"
)

def convert(text: str) -> tuple[str, bool]:
    matches=list(NAMESPACE.finditer(text))
    if not matches:
        return text, False
    if len(matches)!=1:
        raise ValueError("Multiple file-scoped namespace declarations; manual review required")
    match=matches[0]
    namespace=match.group("name")
    before=text[:match.start()]
    after=text[match.end():]
    # The file-scoped form is only legal as a top-level namespace. Preserve
    # prefix (usings, assembly attributes) and wrap all succeeding declarations.
    eol="\r\n" if "\r\n" in text else "\n"
    if re.search(r"(?m)^[ \t]*namespace[ \t]+[\w.]+[ \t]*\{", before):
        raise ValueError("Mixed namespace declarations before file-scoped namespace")
    changed=before+"namespace "+namespace+eol+"{"+eol+after
    if not changed.endswith(eol):changed+=eol
    changed+="}"+eol
    return changed,True

def process(root:Path,apply:bool)->dict:
    if not root.is_dir(): raise FileNotFoundError(root)
    result=Counter()
    examples=[]
    for path in sorted(root.rglob("*.cs")):
        result["source_files"]+=1
        data=path.read_bytes()
        try:text=data.decode("utf-8-sig")
        except UnicodeDecodeError:
            result["non_utf8"]+=1
            continue
        try:updated,needed=convert(text)
        except ValueError:
            result["needs_manual_review"]+=1
            if len(examples)<12: examples.append(str(path.relative_to(root)))
            continue
        if needed:
            result["converted"]+=1
            if apply:path.write_bytes(updated.encode("utf8"))
        else:result["already_compatible"]+=1
    print("CSharp syntax audit:",dict(result))
    print("Manual-review path examples:",examples)
    return dict(result)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--require-clean",action="store_true",
                   help="Fail when any file-scoped namespace remains after conversion")
    a=p.parse_args()
    result=process(a.root,a.apply)
    if result.get("needs_manual_review",0):
        raise SystemExit("Ambiguous files require manual review")
    if a.require_clean:
        post=process(a.root,False) if a.apply else result
        if post.get("converted",0):
            raise SystemExit("C#10 file-scoped namespaces still present after compatibility conversion")
