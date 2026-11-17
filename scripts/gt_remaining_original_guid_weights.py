"""Safe count-only inventory of still-Dummy original Shader GUID targets.

Input must be the accepted SAME-EXPORT post23 material quality JSON from ZIP2.
Never print original shader names/digests, material names or exported GUIDs.
"""
import argparse
from collections import Counter
import json
import re
from pathlib import Path

SCHEMA=1
STATUS="GT_POST23_ORIGINAL_SHADER_GUID_REMAINING_WEIGHT_HISTOGRAM_NO_APK"


def safe_remaining_weights(quality):
    if not isinstance(quality, dict):
        raise ValueError("untrusted_source_material_report")
    counts=quality.get("counts")
    values=quality.get("dummy_shader_material_counts_by_name_digest")
    if (quality.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
            or type(counts) is not dict or type(values) is not dict
            or counts.get("material_documents")!=1536
            or counts.get("material_docs_using_local_custom_Shader")!=786
            or counts.get("material_docs_using_non_dummy_Shader")!=688
            or counts.get("material_docs_using_dummy_Shader")!=98
            or counts.get("distinct_dummy_Shader_targets_referenced")!=37):
        raise ValueError("untrusted_original_post23_material_population")
    # A shader name digest and the original exported Shader GUID are NOT
    # necessarily bijective: several original owners may share a source name.
    # Never impose the 37 GUID count on the digest-key population.
    if not 1<=len(values)<=98:
        raise ValueError("untrusted_original_post23_shader_name_group_population")
    for digest,weight in values.items():
        if (type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}",digest) is None
                or type(weight) is not int or not 1<=weight<=98):
            raise ValueError("untrusted_original_post23_source_digest_weight")
    if sum(values.values())!=98:
        raise ValueError("inconsistent_original_post23_dummy_source_materials")
    counts_only=Counter(values.values())
    if sum(weight*groups for weight,groups in counts_only.items())!=98:
        raise ValueError("incorrect_original_post23_weight_histogram")
    return {
        "schema_version": SCHEMA, "status": STATUS,
        "source": "actual_20261116_next7p33_post23_same_export_only",
        "source_export_run": 43929698985,
        "custom_material_total":786,
        "custom_non_dummy_actual":688,
        "custom_dummy_actual":98,
        "remaining_original_shader_guid_targets_actual":37,
        "remaining_original_shader_name_digest_groups_actual":len(values),
        "original_materials_per_name_digest_weight_histogram":
            {str(weight):counts_only[weight] for weight in sorted(counts_only,reverse=True)},
        "source_names_guids_and_digest_identifiers_exported":False,
        "original_same_export_new_shader_installs_done_by_this_workflow":False,
        "device_pixels_or_full_graphics_restored":False,
        "APK_OBB_XAPK_created":False,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    raw=json.loads(args.quality.read_text(encoding="utf-8"))
    safe=safe_remaining_weights(raw)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("GT_POST23_ORIGINAL_SHADER_GUID_REMAINING_SAFE_COUNTS "+json.dumps(safe,sort_keys=True))


if __name__=="__main__":
    main()
