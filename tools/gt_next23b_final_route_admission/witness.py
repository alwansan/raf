"""Reuse the previous permanently retained, verified authored source packet.

Only new experiment: change final emitted fragment arithmetic AFTER the bound
stage proof. Compare exact standalone route module bytes against routed shader
modules using real glslang/spirv-val. Same resources/offsets and valid entry
points are deliberately held fixed. No previous parser/translation/marker
experiment rerun; no new authored DXBC or Unity assets.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from tools.gt_next23b_final_route_admission.audit import (
    build_routes, expected_modules, candidate_modules, compare, sha
)
from tools.gt_next23b_translation_replay.audit import TOOLS
from scripts.gt_original_921_shaderlab import verify_entrypoints

ARCHIVE_SHA="8a11b0947d864a409876136ac666e96d4e1cf2afeb41d0878c6b75e9e0dbc8c4"
KEY="GT_AUTHORED_ALT"
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def save(root,name,data):
    (root/name).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def main():
    p=argparse.ArgumentParser();p.add_argument("--archive",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    need(a.archive.stat().st_size==24551 and sha(a.archive.read_bytes())==ARCHIVE_SHA,"retained archive SHA")
    a.out.mkdir(exist_ok=True)
    with zipfile.ZipFile(a.archive) as z:
        need(len(z.infolist())==48 and z.testzip() is None,"retained archive member CRC")
        read=lambda n:json.loads(z.read(n))
        retained=read("report.json")
        need(retained["status"]=="PASS_ACTUAL_AUTHORED_SHARED_PROGRAM_SLOT_BINDING","previous witness")
        witness=read("binding-witness.json")
        source=read("source-fixture.json")
        params=read("actual-parameter-records.json")
        dxbc={ref:z.read(ref+"/source.dxbc") for ref in ("program-000","program-001")}
        bound={i:z.read(f"bound-stage-{i:03d}/resource-bound.hlsl") for i in range(4)}
        shader=z.read("baseline.shader").decode()
    pins={n:{"path":str(Path(shutil.which(n)).resolve()),"sha256":sha(Path(shutil.which(n)).read_bytes())} for n in TOOLS}
    routes=build_routes(witness=witness,keyword_names=source["original_shader_ParsedForm_full_private"]["m_KeywordNames"],
            records=params["stage_records"],bound_hlsl=bound,dxbc=dxbc,
            normalization={(0,()):(),(0,(KEY,)):(KEY,)},counts=(2,))
    # Legacy small fixture has a diagnostic fallback; the test proves ONLY
    # the two known routes, not fallback/pragma/runtime scope correctness.
    expected=expected_modules(routes,pins)
    actual=candidate_modules(shader,routes,pins)
    baseline=compare(expected,actual)
    old="gt_fs_o0 = r0 * gt_fs_raft921_cb0_read(0u);"
    new="gt_fs_o0 = r0 + gt_fs_raft921_cb0_read(0u);"
    first,tail=shader.split("#elif defined("+KEY+")",1)
    selected,rest=tail.split("#else",1)
    need(selected.count(old)==1,"mutation target")
    changed=first+"#elif defined("+KEY+")"+selected.replace(old,new,1)+"#else"+rest
    need(shader!=changed,"final text mutation")
    with tempfile.TemporaryDirectory(prefix="gt-final-old-gate-") as tmp:
        verify_entrypoints(changed,Path(tmp),routes=[[[],[KEY]]])
    mutated=candidate_modules(changed,routes,pins)
    altered=(0,(KEY,),0)
    need(set(k for k in expected if expected[k]!=mutated[k])=={altered},
         "mutation affected unexpected route or no module")
    try:compare(expected,mutated)
    except ValueError as exc:
        need(str(exc).endswith("compiled_module_identity_mismatch"),"wrong rejection")
    else:raise AssertionError("new admission accepted modified final arithmetic")
    # Reconstruct output modules from actual bytes, not caller-supplied receipts.
    # Compare real reflected interfaces and operation types.
    def inspect(raw,label):
        file=a.out/(label+".spv");file.write_bytes(raw)
        reflection=json.loads(subprocess.check_output(["spirv-cross",str(file),"--reflect"]))
        dis=subprocess.check_output(["spirv-dis",str(file)],text=True)
        save(a.out,label+"-reflection.json",reflection)
        (a.out/(label+".spvasm")).write_text(dis)
        return reflection,dis
    before,dis_before=inspect(expected[altered],"expected-alt-fragment")
    after,dis_after=inspect(mutated[altered],"mutated-alt-fragment")
    need(before==after,"reflection changed")
    need("OpFMul" in dis_before and "OpFAdd" in dis_after and "OpFMul" not in dis_after,
         "actual arithmetic operation did not change")
    (a.out/"candidate-baseline.shader").write_text(shader)
    (a.out/"candidate-mutated.shader").write_text(changed)
    rows=[]
    for i,(p,key) in enumerate(sorted(routes)):
        row=routes[p,key]
        (a.out/f"expected-route-{i}.hlsl").write_text(row["body"])
        for stage in (1,0):
            ident=(p,key,stage)
            for name,bank in (("expected",expected),("actual",actual),("mutated",mutated)):
                (a.out/f"route-{i}-stage-{stage}-{name}.spv").write_bytes(bank[ident])
            rows.append({"pass":p,"keywords":list(key),"stage":stage,"source_ref":row["source_refs"][stage],
                 "slot":row["slots"][stage],"expected_sha256":sha(expected[ident]),
                 "actual_sha256":sha(actual[ident]),"mutated_sha256":sha(mutated[ident]),
                 "transformed_stage_sha256":row["stage_source_sha256"][stage]})
    report={"status":"PASS_ACTUAL_FINAL_ROUTE_MODULE_ADMISSION_AUTHORED",
      "previous_archive_sha256":ARCHIVE_SHA,"reused_previous_fixture":True,
      "new_dxbc_programs":0,"original_assets_read":False,"source_routes":2,"expected_stage_modules":4,
      "baseline_exact_module_matches":baseline["route_stages"],
      "legacy_entrypoint_gate_accepted_final_arithmetic_mutation":True,
      "actual_mutated_stage_modules":1,"identical_actual_spirv_reflection":True,
      "actual_op_before":"OpFMul","actual_op_after":"OpFAdd",
      "new_exact_module_gate_rejects":True,"stage_rows":rows,
      "original_2312_stage_modules_verified":False,"unity_bundle_verified":False,
      "scope_or_semantic_equivalence_verified":False,"production_install_allowed":False}
    save(a.out,"tool-pins.json",pins);save(a.out,"report.json",report)
    print("GT_ACTUAL_FINAL_ROUTE_ADMISSION "+json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
