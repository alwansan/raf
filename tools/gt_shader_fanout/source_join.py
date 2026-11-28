"""Join private exact source Shader48 priority to current actual exported
serialized Renderer->Material->Shader GUID fanout in one bounded export.

Different populations: source six-scene slots vs exported scene/prefab/other
documents. Never claim renderer assignment parity, visibility or GPU repair.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts import gt_restore_first_shader_priority as priority
from tools.gt_shader_fanout import audit

STATUS="AUTHENTIC_ORIGINAL_SHADER48_TO_ACTUAL_EXPORTED_DUMMY_GUID_FANOUT"
GUID=re.compile(r"[0-9a-f]{32}\Z")

def need(x,reason):
    if not x: raise ValueError(reason)

def join(queue,source,export,ranked):
    need(source.get("status")==priority.STATUS and
         source.get("source_original_6_scene_sha_authenticated") is True and
         source.get("same_instance_original_Shader48_export_trace_verified") is True and
         source.get("private_priority_queue_complete") is True,
         "source_queue_not_authenticated")
    need(export.get("status")==audit.STATUS,"actual_export_fanout_missing")
    need(type(queue) is list and len(queue)==source["same_instance_original_source_count"]==21,
         "source_queue_population")
    need(type(ranked) is list and len(ranked)==export["dummy_shader_guid_targets"],
         "export_rank_population")
    counts=Counter();source_keys=set();local_guids=set();dummy={}
    for row in queue:
        key=(row["original_owner"],row["original_shader_path_id"])
        slots=row["original_scene_renderer_material_slots"]
        guid=row["exported_Shader_GUID"];status=row["program_status"]
        need(key not in source_keys and type(slots) is int and slots>0,"source_identity_or_slots")
        source_keys.add(key)
        need(status in ("dummy","vendor_non_dummy","unity_builtin"),"source_program_status")
        if status=="unity_builtin":
            need(guid is None,"builtin_must_not_be_local_guid")
        else:
            need(type(guid) is str and GUID.fullmatch(guid) and guid not in local_guids,
                 "source_export_guid_not_unique")
            local_guids.add(guid)
        counts["source_"+status+"_slots"]+=slots
        if status=="dummy": dummy[guid]=slots
    need(sum(counts.values())==source["original_typed_renderer_material_slots"]==1633 and
         len(dummy)==source["still_dummy_distinct_original_Shader48_targets"] and
         sum(dummy.values())==source["still_dummy_original_renderer_material_slots"],
         "source_slot_accounting")
    by_guid={}
    for guid,group in ranked:
        need(type(guid) is str and GUID.fullmatch(guid) and guid not in by_guid,"duplicate_export_rank_guid")
        keys=("material_documents","renderer_slots","scene_slots","prefab_slots","other_slots",
              "renderer_objects","exclusive_dummy_renderer_objects")
        need(set(group)==set(keys) and all(type(group[k]) is int and group[k]>=0 for k in keys),
             "invalid_actual_guid_fanout")
        need(group["material_documents"]>0 and
             group["scene_slots"]+group["prefab_slots"]+group["other_slots"]==group["renderer_slots"] and
             group["exclusive_dummy_renderer_objects"]<=group["renderer_objects"]<=group["renderer_slots"],
             "export_guid_fanout_accounting")
        by_guid[guid]=group
    need(sum(g["renderer_slots"] for g in by_guid.values())==export["counts"].get("slot_dummy",0) and
         sum(g["material_documents"] for g in by_guid.values())==export["counts"].get("material_dummy",0),
         "export_population_accounting")
    need(not (set(by_guid)&(local_guids-set(dummy))),"source_non_dummy_guid_classification_conflict")
    joint=set(dummy)&set(by_guid)
    unmatched_source=set(dummy)-joint
    unmatched_export=set(by_guid)-joint
    # Keep source ranking and actual-export ranking independent. Only exact
    # GUID intersections support a joint restoration priority. No identity
    # or source/export slot equality inference from anonymous counts.
    source_order=sorted(dummy,key=lambda g:(-dummy[g],g))
    export_order=[g for g,_ in ranked]
    rows=[]
    for g in sorted(joint,key=lambda g:(-by_guid[g]["renderer_slots"],-by_guid[g]["renderer_objects"],-dummy[g],g)):
        rows.append(dict(source_scene_slots=dummy[g],source_rank=source_order.index(g)+1,
                         actual_export_rank=export_order.index(g)+1,**by_guid[g]))
    return {"schema":1,"status":STATUS,
            "source_six_scene_typed_slots":1633,"source_typed_shader_targets":21,
            "source_dummy_targets":len(dummy),"source_dummy_slots":sum(dummy.values()),
            "actual_export_dummy_targets_with_material_documents":len(by_guid),
            "actual_export_dummy_renderer_slots":export["counts"].get("slot_dummy",0),
            "actual_export_dummy_material_documents":export["counts"].get("material_dummy",0),
            "exact_guid_intersection":len(joint),
            "source_dummy_targets_without_export_material_fanout":len(unmatched_source),
            "source_slots_without_export_material_fanout":sum(dummy[g] for g in unmatched_source),
            "export_dummy_targets_outside_selected_source_scope":len(unmatched_export),
            "export_dummy_slots_outside_selected_source_scope":sum(by_guid[g]["renderer_slots"] for g in unmatched_export),
            "source_top_dummy_has_actual_export_fanout":bool(source_order and source_order[0] in joint),
            "source_top_dummy_is_actual_export_top":bool(source_order and export_order and source_order[0]==export_order[0]),
            "joint_anonymous_priority":rows,"source_and_export_populations_distinct":True,
            "export_scope_commitment":export["snapshot_commitment_sha256"],
            "source_to_export_renderer_assignment_parity":False,
            "original_compiled_shader_program_restored":False,"white_mesh_pixels_verified":False,
            "android_pixels_verified":False,"private_ids_paths_or_payload_published":False,"production":False,"XAPK":False}

def run(original,manifest,project,w1,b02):
    queue,source=priority.real_authenticated_queue(original,manifest,project,w1,b02)
    export,ranked=audit.scan(project)
    return join(queue,source,export,ranked)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ("original","manifest","project","w1","b02","out"):
        p.add_argument("--"+arg,type=Path,required=True)
    a=p.parse_args()
    phase="original_source_queue"
    try:
        queue,source=priority.real_authenticated_queue(a.original,a.manifest,a.project,a.w1,a.b02)
        phase="actual_export_fanout"
        export,ranked=audit.scan(a.project)
        phase="exact_guid_join"
        result=join(queue,source,export,ranked)
    except Exception as e:
        result={"status":"INCONCLUSIVE","phase":phase,"failure_type":type(e).__name__,
                "private_ids_paths_or_payload_published":False,"white_mesh_pixels_verified":False,"production":False,"XAPK":False}
    with a.out.open("x",encoding="utf-8") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("GT_ORIGINAL_EXPORTED_GUID_FANOUT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2
if __name__=="__main__":raise SystemExit(main())
