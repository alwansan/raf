#!/usr/bin/env python3
"""T3: authentic original NormalmapDXT5nm usage, NOT a pixel-correction tool.

The pinned public AssetRipperCLI TextureConverter runs UnpackNormal after
decoding a Texture2D when LightmapFormat == NormalmapDXT5nm (Unity enum 3).
Determine whether the 30 Gamma/DXT5 source objects differ from UnityPy's raw
DXT5 RGBA because that original source explicitly requests unpacking.
Read only three exact original SHA-pinned serialized owner files, not .resS.
Report aggregate counts, never original object identities or original bytes.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b05_verify_material_texenv_bindings import original_texenvs
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts
from scripts.t3_linked_texture_sampler_export import source_targets, OWNER
from scripts.w1_stage_zip2_owners import fingerprint

OWNERS=("sharedassets0.assets","sharedassets1.assets","sharedassets6.assets")
EXPECTED=106
NORMALMAP_DXT5NM=3


def summarize(records: dict, *, expected:int=EXPECTED) -> dict:
    """No per-object rows leak from authenticated original Texture2D cohort."""
    if not isinstance(records,dict) or len(records)!=expected or expected<=0:
        raise ValueError("incomplete_authenticated_source_texture_scope")
    tally=Counter()
    for key,tree in records.items():
        if (not isinstance(key,tuple) or len(key)!=2
            or key[0] not in OWNERS or type(key[1]) is not int
            or key[1]<=0 or not isinstance(tree,dict)):
            raise ValueError("untrusted_original_Texture2D_identity")
        fmt,space,usage=(tree.get("m_TextureFormat"),
                         tree.get("m_ColorSpace"),tree.get("m_LightmapFormat"))
        if (type(fmt) is not int or type(space) is not int or space not in (0,1)
            or type(usage) is not int or not 0<=usage<=11):
            raise ValueError("invalid_original_Texture2D_format_color_usage")
        tally["format_DXT1" if fmt==10 else "format_DXT5" if fmt==12 else "format_OTHER"]+=1
        tally["source_Gamma" if space==0 else "source_Linear"]+=1
        tally["usage_NormalmapDXT5nm" if usage==NORMALMAP_DXT5NM else "usage_Other"]+=1
        if fmt==12 and space==0:
            tally["Gamma_DXT5_source_objects"]+=1
            tally["Gamma_DXT5_NormalmapDXT5nm" if usage==NORMALMAP_DXT5NM else "Gamma_DXT5_not_NormalmapDXT5nm"]+=1
        if fmt==12 and space==1 and usage==NORMALMAP_DXT5NM:
            tally["Linear_DXT5_NormalmapDXT5nm"]+=1
        if fmt==10 and usage==NORMALMAP_DXT5NM:
            tally["DXT1_NormalmapDXT5nm"]+=1
    result={
       "schema_version":1,
       "experiment":"T3-authentic-original-106-Texture2D-DXT5nm-source-usage",
       "selected_original_Texture2D":len(records),
       "authenticated_original_owner_count":len(set(k[0] for k in records)),
       "source_counts":dict(sorted(tally.items())),
       "AssetRipper_unpacks_Normalmap_DXT5nm":True,
       "original_unity_pixels_or_android_device_verified":False,
       "real_source_PNG_transform_equivalence_proven":False,
    }
    result["status"]=(
       "ALL_GAMMA_DXT5_ORIGINAL_NORMALMAP_DXT5NM"
       if tally["Gamma_DXT5_source_objects"]==30
          and tally["Gamma_DXT5_NormalmapDXT5nm"]==30
       else "SOURCE_NORMALMAP_HYPOTHESIS_UNCONFIRMED")
    return result


def inspect(root:Path,manifest:Path):
    import UnityPy
    dataroot=root/"Raft_Data"
    if any(p.is_symlink() for p in (root,dataroot,manifest)):
        raise ValueError("unsafe_original_source_or_manifest")
    for name in OWNERS:
        p=dataroot/name
        if p.is_symlink() or not p.is_file() or fingerprint(p)!=SHADER_OWNERS[name]:
            raise ValueError("unverified_original_source_owner")
    materials=original_texenvs(root,owner_names={OWNER})
    env=UnityPy.load(str(dataroot/OWNER))
    paths=[r.path for r in env.file.externals]
    selected,_=source_targets(materials,paths,manifest_provider_basename_counts(manifest))
    if len(selected)!=EXPECTED:raise ValueError("source_unique_texture_count_drift")
    records={}
    for name in OWNERS:
        file=UnityPy.load(str(dataroot/name))
        needed={pid for provider,pid in selected if provider==name}
        for obj in file.file.objects.values():
            if obj.path_id not in needed:continue
            key=(name,obj.path_id)
            if key in records or obj.type.name!="Texture2D":
                raise ValueError("original_target_missing_or_wrong_type")
            records[key]=obj.read_typetree()
    if set(records)!=selected:raise ValueError("uncovered_original_Texture2D")
    return summarize(records)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("raw_original_source_report_location_refused")
    try:
        result=inspect(a.original,a.manifest)
    except Exception as e:
        result={"schema_version":1,"experiment":"T3-authentic-original-106-Texture2D-DXT5nm-source-usage",
                "status":"INCONCLUSIVE","exception_type":type(e).__name__,
                "original_unity_pixels_or_android_device_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("RAFT_T3_ORIGINAL_DXT5NM_USAGE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]!="INCONCLUSIVE" else 2


if __name__=="__main__":raise SystemExit(main())
