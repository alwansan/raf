"""Strict level38 isolated-editor receipt over the already proven export.

Recreate exact prior scene/meta; no new source assets or player/render path.
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from tools.gt_light_same_export import stage_import as old
from tools.gt_light_same_export.audit import require, Rejected

SCENE_SHA = "2a62ecdd103b3bbbca5c9c68bd6c50d47087f09402205344e1e204504254b915"
META_SHA = "da046194178ee77a2153222d5e2decfdcd52eafa56887dc47f6949173bc9fe15"
SOURCE_SHA = "205515429d83c0e502987f6c917fadd56bf3e8d5af18f6b38e95059db54a2932"
EXPECTED_CHECKS = 154
EXPECTED_OBJECTS = 42
STATUS = "PASS_LEVEL38_EXACT_SCENE_EDITOR_HIERARCHY"


def validate_stage(raw):
    require(type(raw) is dict and
            raw.get("scene_sha256")==SCENE_SHA and raw.get("scene_meta_sha256")==META_SHA and
            raw.get("source_scene_sha256")==SOURCE_SHA and
            raw.get("selected_objects")==EXPECTED_OBJECTS and
            raw.get("same_export_scene_copy_exact") is True and
            raw.get("other_original_assets_staged")==0 and
            raw.get("scene_dependency_closure_claimed") is False and
            raw.get("import_executed") is False,
            "level38_exact_prior_scene_or_scope_drift")
    return True


def validate_same_export(raw):
    require(raw.get("status")=="PASS_SAME_EXPORT" and raw.get("source_export_mapping_proven") is True
            and raw.get("private_trace_mapping_matched") is True
            and raw.get("same_export_hierarchy_parity") is True and not raw.get("mismatches")
            and raw.get("scene_sha256")==SOURCE_SHA
            and raw.get("mapped_objects")==raw.get("selected_source_objects")==EXPECTED_OBJECTS
            and sum(raw["checks"].values())==108,
            "level38_prior_same_export_evidence_drift")
    return True


def validate_editor(raw):
    return (raw.get("status")=="PASS_ISOLATED_IMPORT" and raw.get("editor_step_outcome")=="success" and
            raw.get("Unity_import_verified") is True and raw.get("scene_and_meta_unchanged_after_import") is True
            and raw.get("player_built") is False and raw.get("XAPK") is False and
            raw.get("editor_report",{}).get("matchedObjects")==EXPECTED_OBJECTS and
            raw.get("editor_report",{}).get("checks")==EXPECTED_CHECKS and
            raw.get("editor_report",{}).get("mismatches")==0 and
            raw.get("editor_report",{}).get("sceneOpened") is True and
            raw.get("editor_report",{}).get("sceneGuidMatched") is True and
            raw.get("editor_report",{}).get("mismatchCategories")==[])


def stage(x):
    result=dict(status="INCONCLUSIVE",Unity_import_verified=False,player_built=False,XAPK=False)
    try:
        validate_same_export(json.loads(x.same_export.read_text()))
        old.stage(x.source,x.project,x.trace,x.w1,x.b02,x.dest,x.raw_stage)
        validate_stage(json.loads(x.raw_stage.read_text()))
        result.update(status="PASS_EXACT_PRIOR_LEVEL38_SCENE_STAGED",prior_export_scene_sha256=SCENE_SHA,
                      prior_export_scene_meta_sha256=META_SHA,source_scene_sha256=SOURCE_SHA,
                      exact_scene_and_meta_reproduced=True,selected_objects=EXPECTED_OBJECTS,
                      same_export_checks=108,other_original_assets_staged=0,
                      full_scene_provider_closure_proven=False)
    except Rejected as exc:
        result["reason"]=str(exc)
    except Exception as exc:
        result["reason"]=type(exc).__name__
    x.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_LIGHT_EXACT_EDITOR_STAGE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="PASS_EXACT_PRIOR_LEVEL38_SCENE_STAGED" else 2


def verify(x):
    result=dict(status="INCONCLUSIVE",Unity_import_verified=False,player_built=False,
                XAPK=False,device_pixels_proven=False,full_scene_provider_closure_proven=False)
    try:
        validate_stage(json.loads(x.raw_stage.read_text()))
        old.verify(x.dest,x.raw_stage,x.outcome,x.raw_import)
        raw=json.loads(x.raw_import.read_text())
        result["prior_compatible_import_receipt"]=raw
        require(validate_editor(raw),"level38_exact_editor_hierarchy_not_proven")
        result.update(status=STATUS,Unity_import_verified=True,matched_objects=EXPECTED_OBJECTS,
                      exact_editor_checks=EXPECTED_CHECKS,prior_export_scene_and_meta_unchanged=True,
                      original_scene_sha256=SOURCE_SHA)
    except Rejected as exc:
        result["reason"]=str(exc)
    except Exception as exc:
        result["reason"]=type(exc).__name__
    x.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_LIGHT_EXACT_EDITOR_IMPORT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage")
    for k in ("source","project","trace","w1","b02","dest","same-export","raw-stage","report"):
        st.add_argument("--"+k,type=Path,required=True)
    v=sub.add_parser("verify")
    for k in ("dest","raw-stage","raw-import","report"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--outcome",required=True)
    x=p.parse_args()
    return stage(x) if x.action=="stage" else verify(x)


if __name__=="__main__":
    raise SystemExit(main())
