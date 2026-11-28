"""Same-instance, private original FFT ComputeShader[] reference and candidate install witness.

The selected ARGBFloat source is a diagnostic candidate, not a four-format
runtime solution. No player, shader bundle loader bypass or production change.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
from scripts import b21_stage_light_lineage as lineage
from scripts import gt_stage_indexed_fft_candidate as candidate
from scripts import verify_original_fft_array_provenance as original
from scripts import probe_fft_monoscript_field as mono
from scripts.verify_export_lineage import identity,pointer

def need(ok,why):
    if not ok:raise ValueError(why)

def digest(data):return hashlib.sha256(data).hexdigest()

def patch_helper(path):
    text=path.read_text()
    changes=(
        ('Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE")','Environment.GetEnvironmentVariable("RAFT_PRIVATE_EXPORT_FFT_COMPONENT_LINEAGE")',1),
        ('CaptureLightObjects(','CaptureFftComponent(',2),
        ('asset.ClassID is not (1 or 108)','asset.ClassID != 114 || asset.PathID != 23172',1),
        ('if (asset.ClassID == 108) nonExportable++;','if (asset.ClassID == 114) nonExportable++;',1),
        ('"nonexportable_light_objects_skipped"','"nonexportable_fft_components_skipped"',1),
    )
    for before,after,count in changes:
        need(text.count(before)==count,"helper_anchor")
        text=text.replace(before,after)
    path.write_text(text)

def trace_selected(trace,cls,source):
    need(trace.get("schema_version")==1 and re.fullmatch(r"[a-f0-9]{32}",trace.get("export_instance","")) is not None,"trace_instance")
    rows=[r for r in trace["objects"] if r.get("class_id")==cls and identity(r["source"])==source]
    need(len(rows)==1 and rows[0].get("exportable",True) is True,"trace_population")
    p=pointer(rows[0]["export"])
    need(p[0]!=0 and p[1]!="0"*32 and p[2] in ("2","3"),"trace_pointer")
    return p

def meta_path(assets,guid):
    matches=[]
    for p in assets.rglob("*.meta"):
        need(not p.is_symlink() and p.stat().st_size<=4*1024*1024,"meta_guard")
        m=re.findall(rb"(?m)^guid: *([a-fA-F0-9]{32}) *\r?$",p.read_bytes())
        if len(m)==1 and m[0].decode().lower()==guid:matches.append(p)
    need(len(matches)==1,"meta_population")
    return matches[0]

HEADER=re.compile(rb"(?m)^--- !u!(\d+) &(-?\d+)(?: stripped)?\r?$")
def selected_body(path,file_id,cls):
    need(path.is_file() and not path.is_symlink() and path.stat().st_size<=256*1024*1024,"document_guard")
    raw=path.read_bytes()
    headers=list(HEADER.finditer(raw));matches=[]
    for i,h in enumerate(headers):
        if int(h.group(2))==file_id:
            need(int(h.group(1))==cls and not h.group().endswith(b"stripped"),"document_class")
            matches.append(raw[h.end():headers[i+1].start() if i+1<len(headers) else len(raw)])
    need(len(matches)==1,"document_population")
    return matches[0]

def strict_yaml(data):
    import yaml
    class Loader(yaml.SafeLoader):
        def compose_node(self,parent,index):
            ev=self.peek_event()
            need(not isinstance(ev,yaml.AliasEvent) and getattr(ev,"anchor",None) is None,"yaml_alias")
            return super().compose_node(parent,index)
        def construct_mapping(self,node,deep=False):
            out={}
            for k,v in node.value:
                key=self.construct_object(k,deep=deep)
                need(type(key) in (str,int) and key not in out,"yaml_duplicate")
                if key=="guid" and isinstance(v,yaml.ScalarNode):v.tag="tag:yaml.org,2002:str"
                out[key]=self.construct_object(v,deep=deep)
            return out
    return yaml.load(data.decode("utf-8-sig"),Loader=Loader)

def verify_field(body,field_sha,target):
    d=strict_yaml(body)
    need(type(d) is dict and set(d)=={"MonoBehaviour"} and type(d["MonoBehaviour"]) is dict,"component_document")
    values=d["MonoBehaviour"]
    keys=[k for k in values if isinstance(k,str) and digest(k.encode())==field_sha]
    need(len(keys)==1,"managed_array_field_missing")
    arr=values[keys[0]]
    need(type(arr) is list and len(arr)==1 and type(arr[0]) is dict and set(arr[0])=={"fileID","guid","type"},"compute_array_shape")
    p=arr[0]
    need(type(p["fileID"]) is int and type(p["type"]) is int and (p["fileID"],p["guid"],str(p["type"]))==target,"compute_array_pointer")
    return True

def snapshot(project):
    files={}
    for p in project.rglob("*"):
        need(not p.is_symlink(),"unsafe_export")
        if p.is_file():
            need(len(files)<250000,"export_file_budget")
            with p.open("rb") as stream:files[str(p.relative_to(project))]=(p.stat().st_size,hashlib.file_digest(stream,"sha256").hexdigest())
    return files

def run(source,managed,project,w1,component_trace,work):
    p=original.verify(source,managed)
    need(p["original_compute_shader_array_source_verified"] and p["original_one_element_fft_array_tail_correlated"],"original_provenance")
    m=mono.inspect(managed)
    rows=m["matches"]
    need(len(rows)==1 and rows[0]["original_class_csharp_source_sha256"]==original.MANAGED_CLASS_SHA,"managed_identity")
    fields=rows[0]["original_direct_compute_shader_array_field_sha256"]
    need(len(fields)==1,"managed_array_population")
    field=fields[0]
    need(w1["export_instance"]==component_trace["export_instance"],"same_export")
    cp=trace_selected(component_trace,114,(original.OWNER,original.COMPONENT_PATH_ID))
    fp=trace_selected(w1,72,(original.OWNER,original.FFT_PATH_ID))
    need(fp[0]==7200000 and fp[2]=="2","original_compute_export_pointer")
    assets=project/"Assets"
    old,guid=candidate.exported_fft(assets,w1)
    need(guid==fp[1] and meta_path(assets,guid)==old.with_suffix(".asset.meta"),"compute_meta_identity")
    component=meta_path(assets,cp[1]).with_suffix("")
    original_body=selected_body(component,cp[0],114)
    verify_field(original_body,field,fp)
    stage=work/"candidate";backup=work/"backup";backup.mkdir()
    src_report=candidate.stage(source,stage)
    need(src_report["executable_spirv_matches_independent_candidates"]==20,"source_routes")
    shader=stage/"Assets/DX11 FFT.compute"
    base=shader.read_bytes();header=b"#pragma use_dxc\n#pragma only_renderers vulkan\n"
    need(header not in base and b"#pragma use_dxc" not in base,"source_directive")
    shader.write_bytes(header+base)
    before=snapshot(project)
    report=candidate.install_fft(project,w1,shader,backup)
    need(report["original_fft_guid_preserved"] and report["ordered_routes_installed"]==20 and report["serialized_fft_references_converted_to_importer_type"]>=1,"install_receipt")
    dest=old.with_suffix(".compute");meta=dest.with_suffix(".compute.meta")
    need(not old.exists() and not old.with_suffix(".asset.meta").exists() and dest.read_bytes()==header+base and meta_path(assets,guid)==meta,"candidate_target")
    need(re.findall(rb"(?m)^guid: *([a-fA-F0-9]{32}) *\r?$",meta.read_bytes())==[guid.encode()] and b"ComputeShaderImporter:" in meta.read_bytes(),"compute_importer")
    verify_field(selected_body(component,cp[0],114),field,(fp[0],fp[1],"3"))
    after=snapshot(project)
    removed={str(old.relative_to(project)),str(old.with_suffix(".asset.meta").relative_to(project))}
    added={str(dest.relative_to(project)),str(meta.relative_to(project))}
    need(set(before)-set(after)==removed and set(after)-set(before)==added,"unexpected_files")
    changed={k for k in before.keys()&after.keys() if before[k]!=after[k]}
    pattern=re.compile(rb"(\{fileID:\s*7200000,\s*guid:\s*"+guid.encode()+rb",\s*type:\s*)2(\s*\})")
    restored=0
    for rel in changed:
        saved=backup/rel
        need(saved.is_file() and not saved.is_symlink(),"backup_missing")
        raw=saved.read_bytes();need((len(raw),digest(raw))==before[rel],"backup_hash")
        expected,n=pattern.subn(rb"\g<1>3\2",raw)
        need(n>0 and (project/rel).read_bytes()==expected,"unrelated_mutation")
        restored+=n
    need(str(component.relative_to(project)) in changed and restored==report["serialized_fft_references_converted_to_importer_type"],"reference_population")
    return dict(status="OBSERVED_FFT_ORIGINAL_ARRAY_SAME_EXPORT",original_source_provenance=True,one_element_array_typed_name_matched=True,
        same_export_component_and_compute_guid_join=True,original_file_id=7200000,original_reference_type=2,candidate_reference_type=3,
        diagnostic_candidate_format="ARGBFloat",candidate_routes=20,candidate_sha256=digest(shader.read_bytes()),changed_reference_documents=len(changed),
        exact_reference_type_changes=restored,unrelated_files_unchanged=True,source_asset_bytes_unchanged=True,
        actual_unity_import_verified=False,original_runtime_kernel_mapping_proven=False,all_four_format_runtime_selection_verified=False,
        android_device=False,water_rendering_verified=False,production=False,XAPK=False)

def main():
    p=argparse.ArgumentParser();p.add_argument("--patch-helper",type=Path)
    for k in ("source","managed","project","w1","component-trace","out"):p.add_argument("--"+k,type=Path)
    a=p.parse_args()
    if a.patch_helper:patch_helper(a.patch_helper);return 0
    result=dict(status="INCONCLUSIVE",actual_unity_import_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)
    try:
        with tempfile.TemporaryDirectory(prefix="gt-fft-same-export-",dir=a.project.parent) as work:
            result.update(run(a.source,a.managed,a.project,json.loads(a.w1.read_text()),json.loads(a.component_trace.read_text()),Path(work)))
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
    a.out.write_text(json.dumps(result,sort_keys=True)+"\n")
    print("GT_FFT_SAME_EXPORT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="OBSERVED_FFT_ORIGINAL_ARRAY_SAME_EXPORT" else 2
if __name__=="__main__":raise SystemExit(main())
