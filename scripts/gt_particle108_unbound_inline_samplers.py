#!/usr/bin/env python3
"""GT: private-only original-derived Shader48 Unity sampler COMPILE DIAGNOSTIC.

NO original sampler filtering/wrapping fidelity claimed. Unity recognizes
inline sampler names containing filter+wrap hints; only in an isolated
temporary Unity project, replace translated SamplerState identifiers with
individually unique fixed-Linear-Repeat names. This is an *approximation*.
Do not ship this diagnostic as original Raft's Shader48 or Material GUID.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts.gt_particle108_private_unity_project import (
    STAGE_BRANCH, RESOURCE_ANNOTATION,
)
from scripts.b49_shaderlab_pass_contract import pass_coverage

SAMPLER_DECL=re.compile(
    r'\bSamplerState\s+([A-Za-z_]\w*)\s*'
    r':\s*register\(\s*s\d+\s*(?:,\s*space0\s*)?\)\s*;'
)
ANY_SAMPLER=re.compile(r'\b(?:SamplerState|SamplerComparisonState)\s+[A-Za-z_]\w*')
SAMPLER_BAD_SPACE=re.compile(r'\bSamplerState\s+[A-Za-z_]\w*\s*'
                             r':\s*register\(\s*s\d+\s*,\s*space[1-9]\d*\s*\)')
MAX_BYTES=16*1024*1024
STATUS="GT_UNBOUND_SHADER48_INLINE_SAMPLER_APPROXIMATION_COMPILE_ONLY"

def inline_trial(source:str):
    """Only changes local HLSL SamplerState identifiers, not register() slots."""
    if type(source) is not str or not 0<len(source.encode("utf-8"))<=MAX_BYTES:
        raise ValueError("private_sampler_source_invalid")
    if (source.count("HLSLPROGRAM")!=1 or source.count("ENDHLSL")!=1
        or "//DummyShaderTextExporter" in source
        or SAMPLER_BAD_SPACE.search(source)):
        raise ValueError("private_sampler_shaderlab_invalid")
    if len(list(STAGE_BRANCH.finditer(source)))!=4:
        raise ValueError("source_original_four_private_stage_branches_required")
    proof=Counter()
    used=set()
    inverses={}
    def replace_block(match):
        parts=[match.group(i) for i in range(1,6)]
        for stage,slot in (("VS",1),("PS",3)):
            body=parts[slot]
            old_names=SAMPLER_DECL.findall(body)
            if len(old_names)!=len(ANY_SAMPLER.findall(body)) or len(set(old_names))!=len(old_names):
                raise ValueError("private_sampler_declaration_not_explicit_or_ambiguous")
            aliases={}
            for name in old_names:
                if not re.fullmatch(r'[A-Za-z_]\w*',name):
                    raise ValueError("private_sampler_name_invalid")
                # Compiler-only approximation, not original source filter/wrap.
                # The name contains the required Unity filter/wrap convention.
                candidate="GT_Unbound_"+stage+"_"+name+"_Linear_Repeat"
                # Keyword branches are mutually exclusive; the same
                # stage resource alias can recur across four variants.
                if (len(candidate)>180 or
                    (candidate in inverses and inverses[candidate]!=name)):
                    raise ValueError("private_sampler_trial_name_collision")
                used.add(candidate)
                aliases[name]=candidate
                inverses[candidate]=name
            if aliases:
                matcher=re.compile(r'\b(?:'+
                    '|'.join(re.escape(n) for n in sorted(aliases,key=len,reverse=True))+r')\b')
                body=matcher.sub(lambda m:aliases[m.group()],body)
            parts[slot]=body
            proof["source_private_"+stage+"_sampler_declarations_rewritten"]+=len(aliases)
        return "".join(parts)
    transformed=STAGE_BRANCH.sub(replace_block,source)
    if not inverses or transformed==source:
        raise ValueError("private_sampler_approximation_empty")
    restored=re.compile(r'\b(?:'+
        '|'.join(re.escape(n) for n in sorted(inverses,key=len,reverse=True))+r')\b')
    restored_source=restored.sub(lambda m:inverses[m.group()],transformed)
    before=RESOURCE_ANNOTATION.findall(source)
    after=RESOURCE_ANNOTATION.findall(transformed)
    coverage=pass_coverage(transformed)
    if (restored_source!=source or before!=after
        or coverage.get("pass_count")!=1
        or coverage.get("passes_with_complete_program")!=1
        or coverage.get("pass_braces_balanced") is not True):
        raise ValueError("private_sampler_approximation_changed_non_identifiers")
    return transformed,dict(sorted(proof.items()))

def main():
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("input","output","report"):
        ap.add_argument("--"+key,type=Path,required=True)
    a=ap.parse_args()
    if (a.input.is_symlink() or not a.input.is_file()
        or a.output.exists() or a.output.is_symlink()
        or a.report.exists() or a.report.is_symlink()
        or a.output.resolve().is_relative_to(a.input.parent.resolve())
        or a.report.resolve().is_relative_to(a.input.parent.resolve())
        or not a.output.parent.is_dir() or not a.report.parent.is_dir()):
        raise SystemExit("unsafe_original_private_sampler_diagnostic_paths")
    report={"schema":1,"status":"INCONCLUSIVE",
            "source_original_sampler_filter_wrap_equivalence_proven":False,
            "source_original_Material_sampler_binding_proven":False,
            "original_game_Shader_GUID_Materials_modified":False,
            "Unity_Editor_compilation_or_Adreno_pixels_proven":False,
            "original_sampler_names_shader_bytes_or_GUIDs_published":False}
    try:
        raw=a.input.read_text(encoding="utf-8")
        candidate,counts=inline_trial(raw)
        if not 0<len(candidate.encode("utf-8"))<=MAX_BYTES:
            raise ValueError("private_sampler_trial_oversize")
        a.output.write_text(candidate,encoding="utf-8")
        report["status"]=STATUS
        report["counts"]=counts
        report["approximate_linear_repeat_filter_wrap_used_for_private_compiler_probe"]=True
    except Exception as exc:
        a.output.unlink(missing_ok=True)
        report["failure_type"]=type(exc).__name__
    a.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_UNBOUND_INLINE_SAMPLER_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
