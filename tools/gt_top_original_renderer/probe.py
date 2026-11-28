"""Original rank-one Shader48: select a traced native mesh/material/renderer and its source program pair.

No source identifiers, material values, geometry, shaders or compiler output are published.
Source slots and actual export renderer objects are not equated. No Unity/GPU claim.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import tempfile
import yaml

from tools.gt_shader_fanout import audit
from scripts import gt_restore_first_shader_priority as priority
from scripts.t3_original_renderer_shader_impact import MATERIAL_OWNERS
from scripts.b21_scene_lightmap_links import PIN, verify_source
from scripts.w1_probe_original_shader_links import resolve_pointer
from scripts.verify_export_lineage import identity, pointer
from scripts.gt_original_921_all_variants import authenticated_shader_reader, enumerate_all
from scripts.gt_original_921_keyword_routes import keyword_routes
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key

STATUS = "GT_TOP_ORIGINAL_RENDERER_MATERIAL_MESH_AND_EXPLICIT_SOURCE_PAIR"
ROOTS = {21:"Material",23:"MeshRenderer",33:"MeshFilter",43:"Mesh"}
GUID = re.compile(r"[0-9a-f]{32}\Z")

def need(ok, code):
    if not ok:
        raise ValueError(code)

def trace_map(trace, classes):
    out = {}
    for row in trace["objects"]:
        cls = row.get("class_id")
        if cls not in classes:
            continue
        key = (cls, *identity(row["source"]))
        need(key not in out, "duplicate_trace_source")
        out[key] = pointer(row["export"])
    return out

def native_key(p):
    fid, guid, kind = p
    need(kind in ("2","3") and fid != 0 and GUID.fullmatch(guid) and guid != "0"*32,
         "invalid_native_document_trace")
    return guid, fid

def actual_key(p, owner):
    kind, target = audit.pointer(p, owner)
    need(kind in ("local","native","importer"), "nonlocal_or_missing_document_edge")
    return target

def keywords(tree):
    if "m_ShaderKeywords" in tree:
        raw = tree["m_ShaderKeywords"]
        need(type(raw) is str, "saved_keyword_string")
        words = raw.split()
    elif "m_ValidKeywords" in tree:
        valid = tree["m_ValidKeywords"]
        invalid = tree.get("m_InvalidKeywords", [])
        need(type(valid) is list and type(invalid) is list, "saved_keyword_lists")
        words = valid + invalid
    else:
        raise ValueError("saved_keyword_schema_unobserved")
    need(all(type(w) is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", w) for w in words)
         and len(set(words)) == len(words), "invalid_saved_keyword_set")
    return frozenset(words)

def select_route(packet, saved):
    rows = [r for r in packet if r["subshader"] == 0 and r["pass"] == 0]
    need(len(rows) == 1, "unique_first_source_pass")
    row = rows[0]
    universe = {v["name"] for v in row["keyword_universe"]}
    # One explicit diagnostic context: directional if present, all other
    # non-saved pass keywords absent. Not inference of the actual game state.
    desired = (set(saved) & universe) | ({"DIRECTIONAL"} & universe)
    matches = [r for r in row["routes"] if set(r["enabled"]) == desired]
    need(len(matches) == 1, "explicit_source_route_missing_or_ambiguous")
    return matches[0]

def check_links(renderer, filt, mat, rg, fg, mg, shader_key, mesh_key):
    need(len(renderer["m_Materials"]) == 1, "not_single_material_renderer")
    need(actual_key(renderer["m_Materials"][0], rg) == mg, "renderer_material_pointer_drift")
    need(actual_key(renderer["m_GameObject"], rg) == actual_key(filt["m_GameObject"], fg),
         "renderer_meshfilter_owner_drift")
    need(actual_key(filt["m_Mesh"], fg) == mesh_key, "meshfilter_mesh_pointer_drift")
    need(actual_key(mat["m_Shader"], mg[0]) == shader_key, "material_shader_pointer_drift")

def actual_docs(project, wanted):
    assets = project/"Assets"
    paths, _ = audit.registry.physical_entries(assets)
    by_guid = {}
    for path in sorted(paths):
        if not path.name.endswith(".meta"):
            continue
        txt = audit.snapshot(path, 4*1024*1024).decode("utf-8-sig").replace("\r\n","\n")
        guid, folder = audit.registry.meta_identity(txt)
        if guid not in wanted:
            continue
        need(not folder and guid not in by_guid, "ambiguous_actual_target_meta")
        by_guid[guid] = path.with_name(path.name[:-5])
    docs = {}
    for guid, path in by_guid.items():
        raw = audit.snapshot(path, audit.MAX_FILE)
        if not raw.lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
            continue
        text = raw.decode("utf-8-sig").replace("\r\n","\n")
        heads = list(re.finditer(r"(?m)^---[^\n]*$",text))
        seen = set()
        for i, h in enumerate(heads):
            m = audit.HEAD.fullmatch(h.group())
            need(m is not None, "invalid_actual_yaml_header")
            cls, fid = int(m[1]), audit.integer(m[2])
            need(fid and fid not in seen, "duplicate_actual_anchor")
            seen.add(fid)
            if cls not in ROOTS or m[3] or fid not in wanted[guid]:
                continue
            body = text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)]
            # Mesh43 identity is sufficient here; payload validation is a subsequent gate.
            if cls == 43:
                need(body.lstrip().startswith("Mesh:\n"), "invalid_actual_mesh_document")
                docs[(guid,fid)] = (cls, None)
                continue
            data = yaml.load(body, Loader=audit.UniqueLoader)
            need(type(data) is dict and set(data)=={ROOTS[cls]} and type(data[ROOTS[cls]]) is dict,
                 "actual_typed_yaml_root")
            docs[(guid,fid)] = (cls,data[ROOTS[cls]])
    return docs

def source_candidates(original, shader, material_trace=None, render_trace=None, *, source_only=False):
    import UnityPy
    root = original/"Raft_Data"
    cache = {}
    def load(owner):
        if owner not in cache:
            # Only files staged and verified by the pinned 12-owner workflow.
            p = root/owner
            need(p.is_file() and not p.is_symlink() and p.parent==root, "source_owner_not_staged")
            cache[owner] = UnityPy.load(str(p)).file
        return cache[owner]
    def obj(key, cls):
        o = load(key[0]).objects.get(key[1])
        need(o is not None and o.type.name==cls, "wrong_original_native_class")
        return o
    def resolve(owner, p):
        return resolve_pointer(owner,[x.path for x in load(owner).externals],p)
    mats = {}
    candidates = []
    counts = Counter()
    for scene,pin in PIN.items():
        verify_source(root/scene,pin)
        f = load(scene)
        filters = defaultdict(list)
        for o in f.objects.values():
            if o.type.name=="MeshFilter":
                t = o.read_typetree(check_read=False)
                filters[resolve(scene,t["m_GameObject"])].append((o.path_id,t))
        for o in f.objects.values():
            if o.type.name!="MeshRenderer":
                continue
            t = o.read_typetree(check_read=False)
            for slot in t["m_Materials"]:
                m = resolve(scene,slot)
                if m is None or m[0] not in MATERIAL_OWNERS:
                    continue
                if m not in mats:
                    mt = obj(m,"Material").read_typetree(check_read=False)
                    mats[m] = (resolve(m[0],mt["m_Shader"]),mt)
                if mats[m][0]!=shader:
                    continue
                counts["original_mesh_renderer_slots_to_top_shader"]+=1
                if len(t["m_Materials"])!=1:
                    continue
                counts["original_single_slot_mesh_renderers"]+=1
                go = resolve(scene,t["m_GameObject"])
                fs = filters.get(go,[])
                if len(fs)!=1:
                    counts["missing_or_multiple_original_meshfilters"]+=1
                    continue
                filter_id,ft = fs[0]
                mesh = resolve(scene,ft["m_Mesh"])
                if mesh is None or mesh[0] not in cache and not (root/mesh[0]).is_file():
                    counts["mesh_provider_outside_stage_or_null"]+=1
                    continue
                obj(mesh,"Mesh")
                keys=((23,scene,o.path_id),(33,scene,filter_id),(21,*m),(43,*mesh))
                if source_only:
                    # Original typed identities only; no fabricated export trace.
                    candidates.append((m,(scene,o.path_id),keys,mats[m][1]))
                    continue
                if keys[0] not in render_trace or keys[1] not in render_trace or keys[2] not in material_trace or keys[3] not in render_trace:
                    counts["missing_typed_export_trace"]+=1
                    continue
                export=[native_key(render_trace[keys[0]]),native_key(render_trace[keys[1]]),
                        native_key(material_trace[keys[2]]),native_key(render_trace[keys[3]])]
                candidates.append((m,(scene,o.path_id),export,mats[m][1]))
    return candidates,counts

def run(a, report):
    queue, source = priority.real_authenticated_queue(a.original,a.manifest,a.project,a.w1,a.b02)
    top = [v for v in queue if v["program_status"]=="dummy" and v["original_scene_renderer_material_slots"]==921]
    need(len(top)==1, "rank_one_source_identity")
    top = top[0]
    shader = top["original_owner"],top["original_shader_path_id"]
    sg = top["exported_Shader_GUID"]
    report["rank_one_source_slots"]=921
    w1 = json.loads(a.w1.read_text())
    b02 = json.loads(a.b02.read_text())
    rt = json.loads(a.renderer_trace.read_text())
    need(w1["schema_version"]==b02["schema_version"]==rt["schema_version"]==1
         and GUID.fullmatch(w1["export_instance"])
         and w1["export_instance"]==b02["export_instance"]==rt["export_instance"],"different_export_instances")
    mt=trace_map(w1,{21,48})
    rr=trace_map(rt,{23,33,43})
    need(mt[(48,*shader)]==(4800000,sg,"3"),"source_shader_export_pointer_drift")
    report["same_instance_typed_shader_trace"]=True
    report["phase"]="select_original_mesh_renderer_material"
    candidates,counts=source_candidates(a.original,shader,mt,rr)
    report["source_candidate_counts"]=dict(counts)
    report["typed_trace_candidate_count"]=len(candidates)
    need(candidates,"no_fully_traced_original_mesh_candidate")
    wanted=defaultdict(set)
    for _,_,keys,_ in candidates:
        for guid,fid in keys:
            wanted[guid].add(fid)
    actual=actual_docs(a.project,wanted)
    valid=[]
    rejected=Counter()
    for matkey,rkey,keys,source_material in candidates:
        try:
            need(all(k in actual and actual[k][0]==cls for k,cls in zip(keys,(23,33,21,43))),
                 "typed_export_document_missing")
            rk,fk,mk,xk=keys
            check_links(actual[rk][1],actual[fk][1],actual[mk][1],rk[0],fk[0],mk,(sg,4800000),xk)
            need(keywords(source_material)==keywords(actual[mk][1]), "saved_material_keywords_drift")
            valid.append((matkey,rkey,keys,source_material))
        except (ValueError,KeyError,TypeError) as exc:
            # Only fixed exception category, never serialized identifiers.
            rejected[type(exc).__name__]+=1
    report["exact_native_graph_candidates"]=len(valid)
    report["unverified_candidate_categories"]=dict(rejected)
    need(valid,"no_exact_native_graph_candidate")
    freq=Counter(v[0] for v in valid)
    selected=min(valid,key=lambda v:(-freq[v[0]],v[0],v[1]))
    report["selected_material_eligible_source_renderer_count"]=freq[selected[0]]
    report["selected_material_is_top_among_exact_eligible_candidates"]=True
    report["selected_renderer_material_shader_and_sibling_mesh_filter_mesh_pointer_verified"]=True
    report["selected_saved_material_keyword_count"]=len(keywords(selected[3]))
    report["saved_material_keywords_exact"]=True
    report["phase"]="explicit_original_program_pair"
    tree=authenticated_shader_reader(a.original)(shader)
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    need(len(tables)==1,"original_d3d11_table")
    pairs,orphans,passes,unique=enumerate_all(tree["m_ParsedForm"],tables[0],variants=stage_variants,
         permutation=variant_key,linker=linked_program)
    packet,_=keyword_routes(tree["m_ParsedForm"],pairs,orphans,passes)
    route=select_route(packet,keywords(selected[3]))
    report["selected_explicit_source_pass"]=0
    report["selected_explicit_source_keyword_count"]=len(route["enabled"])
    report["explicit_context_not_actual_game_runtime_route"]=True
    report["phase"]="selected_source_stage_translation"
    with tempfile.TemporaryDirectory(prefix="gt-top-private-",dir=a.out.parent) as td:
        translated=0
        for stage,role in ((1,"vs"),(0,"fs")):
            ident=route[role]
            need(ident[0]==stage,"source_stage_role")
            folder=Path(td)/role
            folder.mkdir(mode=0o700)
            result=translate(unique[ident]["source_code"],stage,folder)
            need(result["dxbc_sha256"]==ident[1] and all(result[k] is True for k in
                 ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")),"selected_original_stage_translation_failed")
            translated+=1
    report["selected_source_stage_programs_translated"]=translated
    report["status"]=STATUS
    report["phase"]="complete_source_and_export_diagnostic"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","project","w1","b02","renderer-trace","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    report={"status":"INCONCLUSIVE","phase":"authenticate_rank_one_source",
            "runtime_keyword_selection_verified":False,"original_mesh_payload_parity_verified":False,
            "original_program_installed":False,"unity_gpu_pixels_verified":False,
            "white_mesh_repair_verified":False,"android_device":False,"XAPK":False,"production":False}
    try:
        run(a,report)
    except Exception as exc:
        report["failure_type"]=type(exc).__name__
    with a.out.open("x") as out:
        json.dump(report,out,indent=2,sort_keys=True)
        out.write("\n")
    print("GT_TOP_ORIGINAL_RENDERER_PROGRAM "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
