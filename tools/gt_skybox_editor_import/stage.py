"""Stage exact verified original skybox wrapper/material in an isolated editor.
No original scene import, runtime bindings, pixel equivalence or player proof.
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import shutil
import struct
from types import SimpleNamespace

from tools.gt_skybox_shader_wrapper import wrapper as w
from tools.gt_skybox_source_register_join import audit as join
from tools.gt_skybox_shader_program import audit as prior
from tools.gt_ambient_same_export import audit as ambient
from tools.gt_light_same_export.audit import require, Rejected
from scripts.b44_verify_material_colors import normalize_colors
from scripts.b22_verify_material_scalars import normalize

CANDIDATE_SHA = "06b9c2f7dd5f213c653d3a5304eadab557a39273a542a1c4bf2af708628aae6c"
VERSION = "2021.3.45f2"
STAGE_STATUS = "PASS_EXACT_SKYBOX_EDITOR_STAGING"
PASS = "PASS_EXACT_SKYBOX_ANDROID_VULKAN_BUNDLE"
SAFE_EDITOR_FIELDS = {"status","version","shaderIdentity","materialIdentity","materialShaderReference",
    "shaderNameExact","sourcePropertyCount","colorSlots","colorMatches","floatSlots","floatMatches",
    "intSlots","texEnvSlots","passCount","androidVulkanOnly","shaderErrorsBefore","shaderErrorsAfter",
    "privateBundleBytes","bundleBuilt","playerBuilt","errorCategory","candidateSha256"}
BOOL_FIELDS = {"shaderIdentity","materialIdentity","materialShaderReference","shaderNameExact",
               "androidVulkanOnly","bundleBuilt","playerBuilt"}
COUNT_FIELDS = {"sourcePropertyCount","colorSlots","colorMatches","floatSlots","floatMatches",
                "intSlots","texEnvSlots","passCount","shaderErrorsBefore","shaderErrorsAfter","privateBundleBytes"}


def bits(value):
    return format(struct.unpack("<I",struct.pack("<f",value))[0],"08x")


def expected_saved(body):
    props=body["m_SavedProperties"]
    colors=normalize_colors(props["m_Colors"])
    scalars=normalize(props)
    require(len(colors)==6 and len(scalars["m_Floats"])==20 and not scalars["m_Ints"] and
            not props["m_TexEnvs"],"skybox_editor_source_saved_population")
    return {"colors":[{"name":k,"bits":[bits(v) for v in rgba]} for k,rgba in sorted(colors.items())],
            "floats":[{"name":k,"bits":format(v,"08x")} for k,v in sorted(scalars["m_Floats"].items())]}


def copy_exact(source,target):
    require(source.is_file() and not any(p.is_symlink() for p in (source,*source.parents))
            and not target.exists(),"skybox_editor_unsafe_copy")
    shutil.copyfile(source,target)
    require(w.digest(source)==w.digest(target),"skybox_editor_copy_digest")
    return w.digest(target)


def stage(x):
    out=dict(status="INCONCLUSIVE",phase="same_export_replay",Unity_import_verified=False,
             player_built=False,XAPK=False,original_assets_published=False)
    try:
        require(not x.dest.exists() and not any(p.is_symlink() for p in x.dest.parents),
                "skybox_editor_project_not_fresh")
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            sh,shader,protected,src=w.exact_source_and_export(
                x,x.destination/"Raft_Data",json.loads(x.skybox_plan.read_text()),
                json.loads(x.plan.read_text()))
            material=protected[3]
            require(material.suffix==".mat","skybox_editor_material_not_standalone_mat")
            mat,body,target,source,sha=prior.source_shader(x.destination/"Raft_Data",
                json.loads(x.skybox_plan.read_text()),json.loads(x.plan.read_text()))
            w1=ambient.read_trace(x.w1)
            mp=ambient.material_mapping(w1,*mat)
            sm=prior.exact_row(w1,(Path(target[0]).name,target[1]),48)
            sp=prior.shader_trace_pointer(sm["export"])
            saved=expected_saved(body)
            manifest=dict(saved,shaderGuid=sp[1],shaderFileId=str(sp[0]),
                          materialGuid=mp[0],materialFileId=str(mp[1]),
                          shaderName=sh["m_ParsedForm"]["m_Name"],candidateSha256=CANDIDATE_SHA)
            before=[w.digest(p) for p in protected]
            replay=SimpleNamespace(**vars(x)); replay.report=x.replay_report
            require(join.run(replay)==0,"skybox_editor_static_replay_failed")
            receipt=json.loads(x.replay_report.read_text())
            require(receipt["status"]==join.STATUS and receipt["private_wrapper_installed"] is True
                    and receipt["private_install"]["after_sha256"]==CANDIDATE_SHA
                    and receipt["private_install"]["protected_files_unchanged"]==5
                    and receipt["selected_mode"]=="unmodified_stage_isolated_hlsl"
                    and w.digest(shader)==CANDIDATE_SHA
                    and [w.digest(p) for p in protected]==before,
                    "skybox_editor_prior_candidate_digest_or_protected_drift")
            out["phase"]="isolated_exact_file_stage"
            (x.dest/"Assets/Editor").mkdir(parents=True)
            (x.dest/"ProjectSettings").mkdir()
            (x.dest/"Packages").mkdir()
            files={}
            for src,rel in [(shader,"Assets/Original.shader"),(protected[0],"Assets/Original.shader.meta"),
                            (material,"Assets/Original.mat"),(protected[4],"Assets/Original.mat.meta")]:
                files[rel]=copy_exact(src,x.dest/rel)
            shutil.copyfile(Path(__file__).with_name("PrivateSkyboxImport.cs"),
                            x.dest/"Assets/Editor/PrivateSkyboxImport.cs")
            (x.dest/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: "+VERSION+"\n")
            (x.dest/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
            (x.dest/"expected-private.json").write_text(json.dumps(manifest))
            out.update(status=STAGE_STATUS,phase="complete",candidate_sha256=CANDIDATE_SHA,
                exact_same_export_files=files,protected_export_files_unchanged=5,
                source_color_slots=6,source_float_slots=20,source_int_slots=0,source_texenv_slots=0,
                prior_static_wrapper_digest_reproduced=True,scene_import_staged=False,
                original_scene_reference_proven_statically=True)
    except Exception as exc:
        out["reason"]=w.error_category(exc)
    x.report.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_EDITOR_STAGE "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STAGE_STATUS else 2


def verify_editor(raw):
    require(type(raw) is dict and set(raw)==SAFE_EDITOR_FIELDS,"skybox_editor_receipt_schema")
    require(all(type(raw[k]) is bool for k in BOOL_FIELDS)
            and all(type(raw[k]) is int and 0<=raw[k]<=2**31-1 for k in COUNT_FIELDS),
            "skybox_editor_receipt_type")
    require(raw["status"] in ("PASS","FAIL","INCONCLUSIVE") and
            raw["errorCategory"] in ("none","identity_or_saved_property_drift","compiler_or_bundle_failed","editor_exception")
            and raw["version"] in (VERSION,"unknown") and
            raw["candidateSha256"] in (CANDIDATE_SHA,""),"skybox_editor_receipt_values")
    return (raw["status"]=="PASS" and raw["version"]==VERSION
            and raw["candidateSha256"]==CANDIDATE_SHA and
            all(raw[k] for k in BOOL_FIELDS-{"playerBuilt"}) and not raw["playerBuilt"]
            and tuple(raw[k] for k in ("sourcePropertyCount","colorSlots","colorMatches",
                "floatSlots","floatMatches","intSlots","texEnvSlots","passCount",
                "shaderErrorsBefore","shaderErrorsAfter"))==(0,6,6,20,20,0,0,1,0,0)
            and raw["privateBundleBytes"]>0 and raw["errorCategory"]=="none")


def verify(x):
    report=dict(status="INCONCLUSIVE",editor_outcome=x.outcome,Unity_import_verified=False,
                android_vulkan_bundle_verified=False,scene_import_verified=False,
                device_pixels_proven=False,player_built=False,XAPK=False)
    try:
        s=json.loads(x.stage_report.read_text())
        require(s["status"]==STAGE_STATUS and s["candidate_sha256"]==CANDIDATE_SHA,
                "skybox_editor_no_valid_stage")
        path=x.dest/"editor-safe.json"
        require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<65536,
                "skybox_editor_no_bounded_receipt")
        raw=json.loads(path.read_text())
        passed=verify_editor(raw)
        report["editor"]=raw
        files=s["exact_same_export_files"]
        require(set(files)=={"Assets/Original.shader","Assets/Original.shader.meta",
                "Assets/Original.mat","Assets/Original.mat.meta"},
                "skybox_editor_staged_file_schema")
        count=sum(w.digest(x.dest/rel)==digest for rel,digest in files.items())
        report["same_export_files_unchanged_after_editor"]=count
        require(x.outcome=="success" and passed and count==4,"skybox_editor_compile_or_import_not_proven")
        report.update(status=PASS,Unity_import_verified=True,android_vulkan_bundle_verified=True)
    except Exception as exc:
        report["reason"]=w.error_category(exc)
    x.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_EDITOR_IMPORT "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==PASS else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="action",required=True)
    s=sub.add_parser("stage")
    for k in ("destination","skybox-plan","plan","project","trace","w1","b02","report","replay-report","dest"):
        s.add_argument("--"+k,type=Path,required=True)
    v=sub.add_parser("verify")
    for k in ("dest","stage-report","report"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--outcome",required=True)
    x=parser.parse_args()
    return stage(x) if x.action=="stage" else verify(x)


if __name__=="__main__":
    raise SystemExit(main())
