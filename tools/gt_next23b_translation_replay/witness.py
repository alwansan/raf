"""Real authored compiler replay, with one distinct legacy counterfactual."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import tempfile

from tools.gt_next23b_translation_replay.audit import FILES, TOOLS, replay, sha, snapshot
from scripts.w1_recover_graphics_programs import translate
from scripts.gt_original_921_keyword_routes import compile_routed_stages
from scripts.probe_directx_shader_bridge import inspect_dxbc

def require(ok, why):
    if not ok: raise AssertionError(why)

def reject(fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(str(exc).endswith(reason), "unexpected rejection: "+str(exc))
        return reason
    raise AssertionError("counterfactual accepted: "+reason)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    meta=json.loads((a.fixture/"fixture.json").read_text())
    names={"vertex":1,"fragment_a":0,"fragment_b":0}
    pins={}
    for name in TOOLS:
        path=Path(shutil.which(name)).resolve()
        pins[name]={"path":str(path),"sha256":sha(path.read_bytes())}
    a.out.mkdir(exist_ok=True)
    (a.out/"tool-pins.json").write_text(json.dumps(pins,indent=2)+"\n")
    proof={}
    with tempfile.TemporaryDirectory(prefix="gt-authored-legacy-") as tmp:
        root=Path(tmp)
        retained={}
        for name,stage in names.items():
            source=(a.fixture/(name+".hlsl")).read_bytes()
            code=(a.fixture/(name+".dxbc")).read_bytes()
            item=meta["programs"][name]
            require(sha(source)==item["source_sha256"] and sha(code)==item["dxbc_sha256"]
                    and len(code)==item["dxbc_bytes"],"fixture digest")
            require(inspect_dxbc(code)["executable_shader_chunk"],"authored DXBC executable chunk")
            folder=root/name;folder.mkdir()
            result=translate(code,stage,folder)
            require(all(result.get(k) is True for k in
                        ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")),"legacy translation")
            retained[name]=snapshot(folder)
            proof[name]=replay(stage,item["dxbc_sha256"],retained[name],pins)
            dest=a.out/name;dest.mkdir()
            for file in FILES: (dest/file).write_bytes(retained[name][file])
        for field in FILES:
            require(retained["fragment_a"][field]!=retained["fragment_b"][field],
                    "indistinguishable fragment outputs")
        packet=[{"subshader":0,"pass":0,"keyword_universe":[{"name":"GT_AUTHORED_ALT"}],
                 "routes":[{"enabled":[],"vs":"vertex","fs":"fragment_a"},
                           {"enabled":["GT_AUTHORED_ALT"],"vs":"vertex","fs":"fragment_b"}]}]
        before=compile_routed_stages(packet,root)
        require(before==4,"legacy baseline route gate")
        # Replace both artifacts that the old routed gate uses; leave its
        # actual DXBC and original.spv untouched. Both shaders still validate.
        for field in ("private.hlsl","roundtrip.spv"):
            for left,right in (("fragment_a","fragment_b"),("fragment_b","fragment_a")):
                (root/left/field).write_bytes(retained[right][field])
        after=compile_routed_stages(packet,root)
        require(after==4,"legacy swap acceptance not reproduced")
        swapped=snapshot(root/"fragment_a")
        expected=meta["programs"]["fragment_a"]["dxbc_sha256"]
        controls={"paired_valid_hlsl_roundtrip_swap":
                  reject(lambda:replay(0,expected,swapped,pins),"hlsl_mismatch")}
        for field,reason in (("original.spv","original_spv_mismatch"),
                             ("roundtrip.spv","roundtrip_spv_mismatch")):
            drift=dict(retained["fragment_a"],**{field:retained["fragment_b"][field]})
            controls[field]=reject(lambda:replay(0,expected,drift,pins),reason)
        bad=copy.deepcopy(pins);bad["spirv-val"]["sha256"]="0"*64
        controls["tool_pin"]=reject(lambda:replay(0,expected,retained["fragment_a"],bad),"tool_digest")
        report={"status":"PASS_ACTUAL_AUTHORED_TRANSLATION_BYTE_REPLAY",
                "compiled_dxbc_programs":3,"independently_replayed_programs":3,
                "original_spirv_validations":3,"roundtrip_spirv_validations":3,
                "legacy_route_gate_before":before,"legacy_route_gate_after_valid_swap":after,
                "new_replay_rejects_swap":True,"negative_controls":controls,
                "proof":proof,"source_authorization_proven":False,
                "original_assets_read":False,"semantic_equivalence_proven":False,
                "unity_bundle_or_gpu_proven":False,"production_install_allowed":False}
        (a.out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
        print("GT_ACTUAL_TRANSLATION_REPLAY "+json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
