#!/usr/bin/env python3
"""Repair only invalid AssetRipper synthetic MonoBehaviour stub filenames.

Examples:
    HeapString.gen.cs -> RecoveredStub_<stable hash>.cs
    public class HeapString.gen : MonoBehaviour -> public class RecoveredStub_<hash> : MonoBehaviour

The original file's .cs.meta bytes (including serialized Unity GUID) are renamed
along with the file, NOT rewritten. Never changes source from ILSpy, which has
already been overlaid separately. Only operate on TEMP exported Unity projects.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re

VALID_CSHARP_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*$")
DECL = re.compile(
    r"(?m)^(?P<prefix>[ \t]*(?:(?:public|internal|private|protected|sealed|abstract|partial)[ \t]+)*class[ \t]+)"
    r"(?P<classname>[^\s:{]+)(?P<suffix>[ \t]*:[ \t]*(?:global::)?MonoBehaviour\b)"
)
# Markers below characterize AssetRipper minimal script placeholder, not gameplay C#.
MINIMAL_USINGS = {"using UnityEngine;", "using UnityEngine.UI;", "using System;"}
# Two AssetRipper-generated Timeline MonoBehaviour stubs produce CS0101
# duplicate type errors under Unity 2021. Use only in diagnostic imports.
KNOWN_TIMELINE_TEMPLATES = {
    "Unity.Timeline/UnityEngine/Timeline/AnimationPlayableAsset.cs",
    "Unity.Timeline/UnityEngine/Timeline/AnimationTrack.cs",
}

def fix_stubs(assets: Path, *, apply: bool, repair_timeline: bool = False) -> dict:
    if not assets.is_dir():
        raise FileNotFoundError(f"Expected Unity Assets root: {assets}")
    scripts=assets/"Scripts"
    if not scripts.is_dir():
        raise FileNotFoundError("Expected AssetRipper Assets/Scripts layout")
    count=Counter()
    examples=[]
    for path in sorted(scripts.rglob("*.cs")):
        count["inspected"]+=1
        bad_name=path.name[:-3]  # Remove only final .cs; may still contain .gen/.partial
        timeline_template = (
            repair_timeline and path.relative_to(scripts).as_posix() in KNOWN_TIMELINE_TEMPLATES
        )
        if VALID_CSHARP_IDENTIFIER.fullmatch(bad_name) and not timeline_template:
            continue
        if timeline_template:
            count["timeline_collisions"]+=1
        else:
            count["invalid_filename"]+=1
        original=path.read_text(encoding="utf-8-sig",errors="replace")
        matches=[m for m in DECL.finditer(original) if m.group("classname")==bad_name]
        if len(matches)!=1:
            # A real Decompiled SDK type is NOT the old synthetic Timeline MonoBehaviour.
            # Keep it and its original GUID intact; Unity/sdk isolation checks compilation.
            if timeline_template and len(matches)==0:
                count["preserved_real_timeline_source"]+=1
                continue
            # A C# filename may legally start with a hyphen; only a TYPE declaration
            # containing that invalid identifier would need a source repair.
            if bad_name.startswith("-") and len(matches)==0:
                illegal_type=re.search(r"\b(?:class|struct|interface|enum|record|delegate)\s+"+
                                       re.escape(bad_name)+r"(?=[\s:{(<])",original)
                if not illegal_type:
                    count["preserved_non_script_filename"]+=1
                    continue
            count["unmatched_or_ambiguous"]+=1
            if len(examples)<12: examples.append({"file":str(path.relative_to(assets)),"reason":"no single matching invalid MonoBehaviour class declaration"})
            continue
        # Strictly restrict edits to generated minimal stubs; never rewrite real logic.
        first_lines=[x.strip() for x in original.splitlines()[:3]]
        if "using UnityEngine;" not in first_lines:
            count["not_minimal_stub"]+=1
            if len(examples)<12: examples.append({"file":str(path.relative_to(assets)),"reason":"not recognized as UnityEngine template"})
            continue
        meta=path.with_name(path.name+".meta")
        if not meta.is_file():
            count["missing_meta"]+=1
            continue
        relative=path.relative_to(scripts).as_posix()
        safe="RecoveredStub_"+hashlib.sha256(relative.encode("utf-8")).hexdigest()[:20]
        dst=path.with_name(safe+".cs")
        dstmeta=path.with_name(safe+".cs.meta")
        if dst.exists() or dstmeta.exists():
            raise FileExistsError(f"Refusing to overwrite a source or .meta file for {relative}")
        m=matches[0]
        fixed=original[:m.start("classname")]+safe+original[m.end("classname"):]
        count["fixed_candidates"]+=1
        if len(examples)<12:
            examples.append({"file":str(path.relative_to(assets)),"new_stem":safe})
        if apply:
            # Move .meta unchanged. Its GUID remains the authoritative scene link.
            dst.write_text(fixed,encoding="utf-8")
            dstmeta.write_bytes(meta.read_bytes())
            path.unlink()
            meta.unlink()
    print("AssetRipper invalid stub audit:",dict(count))
    print("Examples (filenames only, no original game CSharp):",examples)
    return dict(count)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--assets",required=True,type=Path)
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--require-clean",action="store_true")
    parser.add_argument("--repair-timeline",action="store_true",
                        help="Diagnostic-only rename of 2 Timeline collision placeholders")
    args=parser.parse_args()
    result=fix_stubs(args.assets,apply=args.apply,repair_timeline=args.repair_timeline)
    if result.get("unmatched_or_ambiguous",0) or result.get("not_minimal_stub",0) or result.get("missing_meta",0):
        raise SystemExit("Unsupported invalid classes still present; inspect before modifying")
    if args.require_clean and args.apply:
        after=fix_stubs(args.assets,apply=False,repair_timeline=args.repair_timeline)
        if after.get("fixed_candidates",0):
            raise SystemExit("Unfixed invalid AssetRipper stubs remain")
