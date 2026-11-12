#!/usr/bin/env python3
"""Stage SHA-original Spectrum Shader.m_Name to a private file for typed managed IL.

The string is never printed, committed, or added to GitHub artifacts. B09
source identity is SHA-attested before writing; this only prepares a query.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.b09_spectrum_topology_contract import TARGET, OWNER, PASSES
from scripts.b09_stage_original_spectrum import _selected_original
from scripts.verify_targeted_lfs_compute_sources import verify_sources, EXPECTED


def validate_name(value):
    if type(value) is not str or value!=TARGET or not 0<len(value)<=256 or any(
            ch in value for ch in "\x00\r\n"):
        raise ValueError("Spectrum_original_shader_name_invalid")
    return value


def prepare(source:Path, out:Path, *, reader=_selected_original):
    source,out=Path(source).absolute(),Path(out).absolute()
    if (not source.is_dir() or source.is_symlink() or not out.parent.is_dir()
            or out.exists() or out.is_symlink() or out.is_relative_to(source)
            or any(p.is_symlink() for p in (out.parent,source.parent))):
        raise ValueError("Spectrum_private_source_name_path_invalid")
    verify_sources(source,expected={OWNER:EXPECTED[OWNER]})
    pathid,_sha,tree,auth=reader(source)
    if (pathid!=2432 or auth.get("authenticated_original_passes")!=PASSES
            or auth.get("authenticated_variant_stage_programs")!=28):
        raise ValueError("Spectrum_original_B09_source_attestation_invalid")
    name=validate_name(tree.get("m_ParsedForm",{}).get("m_Name"))
    fd=os.open(str(out),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as stream:
        stream.write(name)
    return True


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--private-out",required=True,type=Path)
    a=p.parse_args()
    try:
        prepare(a.source,a.private_out)
    except BaseException as e:
        print("GT_SPECTRUM_MANAGED_FIND_NAME_SAFE status=INCONCLUSIVE error_type="+type(e).__name__)
        return 2
    print("GT_SPECTRUM_MANAGED_FIND_NAME_SAFE status=SOURCE_ORIGINAL_NAME_ATTESTED private_only=true")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
