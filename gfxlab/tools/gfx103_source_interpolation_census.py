"""GFX103 source-private Shader48 DXBC interpolation census for actual 524 pairs.

Existing ZIP2 source is fetched into the isolated Actions runner at an immutable
SHA. DO NOT print original bytes, shader text, private identifiers, names,
keyword sets, registers, or per-program data. Only safe aggregate counters.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.gfx103_source_interpolation_gate import dxbc_fragment_input_classes

def census(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7:
        raise ValueError("GFX103_SOURCE_PASS_COUNT_DRIFT")
    cached={}
    ordinary=Counter();siv=Counter();generated=0
    pair_count=0;pair_ordinary_np=0;pair_siv_np=0
    for row in passes:
        pairs=row.get("pairs")
        if not isinstance(pairs,list) or not pairs:
            raise ValueError("GFX103_EMPTY_OR_BAD_EXACT_PASS_PAIRS")
        for vs,fs in pairs:
            pair_count+=1
            idx=fs.get("m_BlobIndex")
            if type(idx) is not int:
                raise ValueError("GFX103_PIXEL_STAGE_BLOB_INDEX_INVALID")
            if idx not in cached:
                source=code_from_ref(fs,programs,"Pixel")
                cached[idx]=dxbc_fragment_input_classes(source_shader_chunk(source))
            decl=cached[idx]
            ordinary.update(decl["ordinary_modes"])
            siv.update(decl["system_interpreted_modes"])
            generated+=decl["system_generated_count"]
            pair_ordinary_np+=bool(decl["ordinary_noperspective_declarations"])
            pair_siv_np+=bool(decl["system_interpreted_noperspective_declarations"])
    if pair_count!=524:
        raise ValueError("GFX103_ORIGINAL_524_PAIRS_DRIFT")
    unique_ordinary=Counter();unique_siv=Counter();unique_sgv=0
    for decl in cached.values():
        unique_ordinary.update(decl["ordinary_modes"])
        unique_siv.update(decl["system_interpreted_modes"])
        unique_sgv+=decl["system_generated_count"]
    return {
        "experiment":"GFX-MULTI-103",
        "source_zip2_sha":ZIP2_SHA,
        "original_shader48_source_authentic":True,
        "source_pass_count":7,
        "original_exact_pair_count":pair_count,
        "distinct_original_pixel_stages_in_exact_pairs":len(cached),
        "pair_occurrence_ordinary_interpolation_modes":dict(ordinary),
        "pair_occurrence_siv_interpolation_modes":dict(siv),
        "pair_occurrence_system_generated_count":generated,
        "unique_pixel_stage_ordinary_modes":dict(unique_ordinary),
        "unique_pixel_stage_siv_modes":dict(unique_siv),
        "unique_pixel_stage_system_generated_count":unique_sgv,
        "pair_occurrences_with_ordinary_noperspective":pair_ordinary_np,
        "pair_occurrences_with_siv_noperspective":pair_siv_np,
        "device_GLES310_qualifier_probe_synthetic_pass":True,
        "source_to_generated_spirv_semantics_verified":False,
        "source_to_adreno_original_stage_pixels_verified":False,
        "original_material_cb_binding_verified":False,
        "original_rig_animation_verified":False,
        "originalShaderRestored":False,
        "phase_closed":False,
        "original_source_bytes_exported":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--safe",required=True,type=Path)
    args=p.parse_args()
    source=stage_originals(args.zip2,args.stage)
    report=census(source)
    args.safe.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX103_SAFE_INTERPOLATION_COUNTS "+json.dumps(report,sort_keys=True))
if __name__=="__main__":
    main()
