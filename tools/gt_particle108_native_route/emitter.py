"""Particle108 source-only original emitter component join. No image/GPU replay."""
import argparse
from collections import Counter
import json
from pathlib import Path
from scripts import t3_original_particle_material_texenv as source
from scripts.t3_original_particle_shader_state import inspect_parsed
from scripts.w1_probe_original_shader_links import resolve_pointer
from scripts.b21_scene_lightmap_links import PIN, verify_source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from tools.gt_particle108_native_mips import probe as native
from tools.gt_particle108_redirect_target import audit

STATUS="SOURCE_PARTICLE108_NATIVE_MATERIAL_EMITTER_COMPONENT_JOIN"
class Reject(ValueError): pass
def need(ok,code):
    if not ok: raise Reject(code)

def component_ptr(entry):
    need(type(entry) is dict,"component_entry_schema")
    if set(entry)=={"component"}: return entry["component"]
    if set(entry)=={"first","second"}: return entry["second"]
    if set(entry)=={"m_FileID","m_PathID"}: return entry
    raise Reject("component_pointer_schema")

def emitter_link(owner,external,go,renderer,classes):
    need(type(go.get("m_Component")) is list,"gameobject_component_list")
    members=[resolve_pointer(owner,external,component_ptr(e)) for e in go["m_Component"]]
    need(None not in members and len(members)==len(set(members)),"null_or_duplicate_component")
    need(renderer in members and classes.get(renderer)=="ParticleSystemRenderer","renderer_not_member")
    candidates=[p for p in members if classes.get(p)=="ParticleSystem"]
    need(len(candidates)==1 and candidates[0][0]==owner,"emitter_not_unique_local_component")
    return candidates[0]

def select_material(slots,selected):
    found={key for key,entries in slots.items() if any(ptr[0]==0 and (key[0],ptr[1])==selected for ptr,_ in entries.values())}
    need(len(found)==1,"native_material_not_unique")
    return found

def census(root,manifest):
    import UnityPy
    slots,targets={},{}
    scope=source.run(root,manifest,private_material_texenvs=slots,private_local_texture_targets=targets)
    need(scope["status"]==source.STATUS and len(slots)==5 and len(targets)==3
         and scope["six_original_scene_SHA_verified"] is True
         and scope["four_original_shader_Material_owner_SHA_verified"] is True
         and scope["original_108_use_ParticleShader48_reference_authenticated"] is True,"source_scope")
    data=root/"Raft_Data"
    desc={}
    for key in targets:
        owner,pid=key
        need(owner in SHADER_OWNERS,"texture_owner")
        _,tex=audit.load_texture(data/owner,SHADER_OWNERS[owner],pid)
        desc[key]={k:getattr(tex,k,None) for k in (*native.FIELDS,"m_MipsStripped","m_LightmapFormat","m_ColorSpace")}
    selected=native.select(desc)
    chosen=select_material(slots,selected)
    need(targets[selected]==1,"native_texture_slot_multiplicity")
    owners={}
    def load(owner):
        if owner not in owners:
            need(owner in SHADER_OWNERS,"unadmitted_dependency_owner")
            path=data/owner
            need(not path.is_symlink() and fingerprint(path)==SHADER_OWNERS[owner],"dependency_owner_sha")
            owners[owner]=UnityPy.load(str(path)).file
        return owners[owner]
    shaders=set()
    for owner,pid in slots:
        file=load(owner);obj=file.objects.get(pid)
        need(obj is not None and obj.type.name=="Material","material_class")
        shaders.add(resolve_pointer(owner,[x.path for x in file.externals],obj.read_typetree()["m_Shader"]))
    need(len(shaders)==1 and None not in shaders,"shader_identity")
    owner,pid=next(iter(shaders)); shader=load(owner).objects.get(pid)
    need(shader is not None and shader.type.name=="Shader","shader_class")
    blend=inspect_parsed(shader.read_typetree()["m_ParsedForm"])
    stats=Counter();modes=Counter()
    for name,pin in PIN.items():
        verify_source(data/name,pin)
        file=UnityPy.load(str(data/name)).file
        ext=[x.path for x in file.externals]
        classes={(name,obj.path_id):obj.type.name for obj in file.objects.values()}
        for obj in file.objects.values():
            if obj.type.name!="ParticleSystemRenderer":continue
            t=obj.read_typetree(check_read=False)
            need(type(t.get("m_Materials")) is list,"renderer_material_list")
            mats=[resolve_pointer(name,ext,p) for p in t["m_Materials"]]
            count=sum(p in slots for p in mats)
            if not count:continue
            stats["all_shader_slots"]+=count;stats["all_shader_renderers"]+=1
            native_count=sum(p in chosen for p in mats)
            if not native_count:continue
            stats["native_material_slots"]+=native_count;stats["native_material_renderers"]+=1
            go=resolve_pointer(name,ext,t["m_GameObject"])
            need(go is not None and classes.get(go)=="GameObject","renderer_gameobject_pointer")
            ps=emitter_link(name,ext,file.objects[go[1]].read_typetree(check_read=False),(name,obj.path_id),classes)
            pt=file.objects[ps[1]].read_typetree(check_read=False)
            need(resolve_pointer(name,ext,pt["m_GameObject"])==go,"emitter_owner_backlink")
            stats["reciprocal_emitter_links"]+=1
            mode=t.get("m_RenderMode")
            need(type(mode) is int and 0<=mode<=16,"renderer_mode_unclassified")
            modes[str(mode)]+=1
            refs=[resolve_pointer(name,ext,v) for k,v in t.items() if k in ("m_Mesh","m_Mesh0","m_Mesh1","m_Mesh2","m_Mesh3")]
            stats["mesh_pointer_fields"]+=len(refs)
            for ref in (p for p in refs if p is not None):
                stats["mesh_nonnull_pointers"]+=1
                if ref[0]==name:cls=classes.get(ref)
                elif ref[0] in SHADER_OWNERS:
                    target=load(ref[0]).objects.get(ref[1]);cls=target.type.name if target is not None else None
                else:cls=None
                stats["typed_mesh_pointer_targets" if cls=="Mesh" else "unresolved_mesh_pointer_targets"]+=1
            stats["vertex_stream_field_present"]+=int("m_VertexStreams" in t)
            stats["shape_module_field_present"]+=int("ShapeModule" in pt or "m_ShapeModule" in pt)
            stats["emission_module_field_present"]+=int("EmissionModule" in pt or "m_EmissionModule" in pt)
    need(stats["all_shader_slots"]==108 and stats["all_shader_renderers"]==54,"original_renderer_census_drift")
    need(stats["native_material_renderers"]>0 and stats["native_material_renderers"]==stats["reciprocal_emitter_links"],"native_emitter_coverage")
    need(sum(modes.values())==stats["native_material_renderers"],"renderer_mode_coverage")
    return dict(status=STATUS,source_emitter_component_graph_verified=True,source_native_texture_descriptor_unique=True,
                source_texture_payload_retested=False,source_material_shader_identity_verified=True,
                source_renderer_mode_histogram=modes,source_counts=dict(stats),source_fixed_function_state=blend,
                source_geometry_mesh_payload_verified=False,original_emitter_geometry_verified=False,
                runtime_keyword_selection_verified=False,black_fire_restored=False,Android_device=False,
                production=False,XAPK=False,private_payload_published=False)

def main():
    p=argparse.ArgumentParser()
    for k in ("original","manifest","out"):p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    need(not a.out.exists() and not a.out.resolve().is_relative_to(a.original.resolve()),"unsafe_report_path")
    try: result=census(a.original,a.manifest)
    except Reject as e:result=dict(status="INCONCLUSIVE",failure_category=str(e),private_payload_published=False)
    except Exception as e:result=dict(status="INCONCLUSIVE",failure_type=type(e).__name__,private_payload_published=False)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_PARTICLE108_SOURCE_EMITTER "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2
if __name__=="__main__":raise SystemExit(main())
