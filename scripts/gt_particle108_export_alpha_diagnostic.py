"""GT Particle108 three linked Texture2D export-alpha diagnostic (NO APK).

Original SHA-authenticated six-scene five-Material graph and Texture2D owners
identify the three targets. A same-instance AssetRipper trace selects exported
TextureImporter GUIDs. This classifies actual exported image alpha and importer
metadata without changing assets or publishing names, IDs, GUIDs, or pixels.

An opaque input does NOT prove the shader is wrong: shader alpha may be derived
from RGB or uniforms. Exported alpha is NOT Android Vulkan blending parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts import t3_original_particle_material_texenv as material_source
from scripts import t3_original_particle_texture_targets as texture_source
from scripts.verify_export_lineage import identity, pointer
from scripts.verify_exported_material_texture_links import GUID, IMAGES, BUILTIN, ZERO, is_texture
from scripts.gt_next23b_unity_receipt import strict_json, read_snapshot
from scripts.gt_particle108_source_pixel_parity import decode_original_texture, external_parity

MAX_IMAGE_BYTES = 256 * 1024 * 1024
MAX_PIXELS = 64 * 1024 * 1024
MAX_META = 256 * 1024
EXPECTED_TARGETS = 3
STATUS = "GT_PARTICLE108_THREE_SAME_EXPORT_TEXTURE_ALPHA_CLASSIFIED"
PARTIAL_STATUS = "GT_PARTICLE108_TWO_EXTERNAL_ALPHA_IMAGES_ONE_LOCAL_TEXTURE_PPTR_PENDING"
UNPROVEN_STATUS = "GT_PARTICLE108_EXTERNAL_ALPHA_CLASSIFIED_TEXTURE_TRACE_UNPROVEN"
TRACE_LIMIT = 40 * 1024 * 1024
META_FIELDS = ("alphaSource", "alphaIsTransparency", "sRGBTexture", "mipmapEnabled")


def alpha_profile(image):
    """Private pixel analysis: return only aggregate alpha coverage."""
    if not 0 < image.width * image.height <= MAX_PIXELS:
        raise ValueError("unsupported_or_oversize_particle_texture_dimensions")
    has_alpha = "A" in image.getbands() or "transparency" in image.info
    rgba = image.convert("RGBA")
    bins = rgba.getchannel("A").histogram()
    if len(bins) != 256 or sum(bins) != image.width * image.height:
        raise ValueError("invalid_decoded_alpha_histogram")
    return {
        "has_explicit_alpha": bool(has_alpha),
        "all_opaque": bins[255] == image.width * image.height,
        "has_transparent_pixels": sum(bins[:255]) > 0,
        "has_partially_transparent_pixels": sum(bins[1:255]) > 0,
        "fully_transparent_pixel_present": bins[0] > 0,
    }


def validate_trace(trace, originals):
    if (type(trace) is not dict or type(trace.get("schema_version")) is not int
            or trace["schema_version"] != 1 or type(trace.get("export_instance")) is not str
            or not re.fullmatch("[a-fA-F0-9]{32}", trace["export_instance"])
            or type(trace.get("objects")) is not list or len(originals) != EXPECTED_TARGETS):
        raise ValueError("untrusted_particle_source_export_linkage")


def external_image_pointer(value):
    """TextureImporter Texture2D must resolve the full PPtr, not merely GUID."""
    if (type(value) is not tuple or len(value) != 3
            or type(value[0]) is not int or value[0] != 2800000
            or type(value[1]) is not str or not re.fullmatch("[a-fA-F0-9]{32}", value[1])
            or value[1].lower() in {ZERO, *BUILTIN}
            or type(value[2]) is not int or value[2] not in (2, 3)):
        raise ValueError("invalid_same_export_Texture2D_image_pointer")
    return value[0], value[1].lower(), value[2]


def selected_texture_trace(trace, originals, *, metrics=None, private_exportability=None):
    """Retain every selected trace row, including local and missing ones.

    A missing/unsupported row cannot erase independent valid rows or authorize
    an inferred image. No source identifiers enter returned public metrics.
    """
    validate_trace(trace, originals)
    counts = {
        "original_selected_Texture2D28": EXPECTED_TARGETS,
        "all_export_trace_Texture2D28_rows": 0,
        "rows_matching_original_selected_Texture2D28": 0,
        "duplicate_original_selected_texture_rows": 0,
        "matched_original_selected_unique_targets": 0,
        "distinct_exported_GUIDs_for_matched_original": 0,
        "selected_trace_local_type0_rows": 0,
        "selected_trace_external_image_rows": 0,
        "selected_trace_global_nonimage_anchor_rows": 0,
        "selected_trace_missing_targets": EXPECTED_TARGETS,
    }
    if metrics is not None:
        if type(metrics) is not dict or metrics:
            raise ValueError("invalid_export_trace_numeric_diagnostic")
        metrics.update(counts)
        counts = metrics
    if private_exportability is not None and (type(private_exportability) is not dict or private_exportability):
        raise ValueError("invalid_private_texture_exportability_outparam")
    selected, external_guids = {}, set()
    for row in trace["objects"]:
        if type(row) is not dict or row.get("class_id") != 28:
            continue
        counts["all_export_trace_Texture2D28_rows"] += 1
        key = identity(row["source"])
        if key not in originals:
            continue
        counts["rows_matching_original_selected_Texture2D28"] += 1
        if key in selected:
            counts["duplicate_original_selected_texture_rows"] += 1
            raise ValueError("duplicated_original_particle_Texture2D_export")
        fid, guid, kind = pointer(row["export"])
        actual = (fid, guid, int(kind))
        if fid <= 0 or actual[2] not in (0, 2, 3):
            raise ValueError("invalid_same_export_Texture2D_pointer")
        exportable=row.get("exportable")
        if exportable is not None and type(exportable) is not bool:
            raise ValueError("invalid_local_Texture2D_exportability")
        if actual[2] != 0:
            if guid in {ZERO,*BUILTIN} or exportable is False:
                raise ValueError("invalid_same_export_Texture2D_pointer")
            # A serialized embedded Texture2D can have an arbitrary anchor.
            # Strict image fileID=2800000 validation still applies to actual
            # external image routes, not document-local references.
            if guid in external_guids:
                raise ValueError("original_particle_Texture2D_Guid_not_unique")
            external_guids.add(guid)
            if fid==2800000:
                counts["selected_trace_external_image_rows"] += 1
            else:
                counts["selected_trace_global_nonimage_anchor_rows"] += 1
        else:
            counts["selected_trace_local_type0_rows"] += 1
        selected[key] = actual
        if private_exportability is not None:
            private_exportability[key]=exportable
        counts["matched_original_selected_unique_targets"] = len(selected)
        counts["distinct_exported_GUIDs_for_matched_original"] = len(external_guids)
        counts["selected_trace_missing_targets"] = EXPECTED_TARGETS - len(selected)
    return selected


def compare_texture_trace_routes(selected, routes, *, local_documents=None, exportability=None):
    """Classify independently traced references vs inferred Material routes."""
    if type(selected) is not dict or type(routes) is not dict or not set(selected) <= set(routes):
        raise ValueError("untrusted_particle_texture_trace_scope")
    documents,exportability=local_documents or {},exportability or {}
    counts = dict(independently_traced_external_targets=0, inferred_external_targets=0,
                  local_type0_rows_equal_unscoped=0, local_type0_targets_unresolved=0,
                  document_scoped_local_targets_proven=0,document_scoped_local_slots_proven=0,
                  independently_traced_external_slots=0, inferred_external_slots=0)
    for key, route in routes.items():
        actual, slots = route["pointer"], route["slots"]
        expected = selected.get(key)
        if actual[2] == 0:
            # A local reference may be proven ONLY by a global, exportable
            # Texture2D trace plus its actual same-file nonstripped anchor.
            # Equal unscoped triples or nonzero GUID hints remain unresolved.
            if expected == actual:
                counts["local_type0_rows_equal_unscoped"] += 1
            doc_guids=route.get("document_guids",set())
            if (actual[1]==ZERO and len(doc_guids)==1 and expected is not None
                    and expected[2] in (2,3) and exportability.get(key) is True
                    and expected[:2]==(actual[0],next(iter(doc_guids)))
                    and documents.get(expected[:2])==28):
                counts["document_scoped_local_targets_proven"] += 1
                counts["document_scoped_local_slots_proven"] += slots
            else:
                counts["local_type0_targets_unresolved"] += 1
        elif expected is None:
            counts["inferred_external_targets"] += 1
            counts["inferred_external_slots"] += slots
        elif expected != actual:
            raise ValueError("original_texture_trace_and_Material_YAML_PPtr_mismatch")
        else:
            counts["independently_traced_external_targets"] += 1
            counts["independently_traced_external_slots"] += slots
    counts["all_external_texture_targets_independently_traced"] = not counts["inferred_external_targets"]
    counts["all_selected_texture_targets_independently_traced"] = (
        counts["all_external_texture_targets_independently_traced"]
        and not counts["local_type0_targets_unresolved"])
    return counts


def source_texture_export_map(trace, originals, *, metrics=None):
    """One original Texture2D28 => one exported pointer; only numeric telemetry."""
    selected = selected_texture_trace(trace, originals, metrics=metrics)
    if any(value[2] == 0 for value in selected.values()):
        raise ValueError("invalid_same_export_Texture2D_pointer")
    if set(selected) != set(originals):
        raise ValueError("original_particle_Texture2D_Guid_not_unique")
    return {key: external_image_pointer(value)[1] for key, value in selected.items()}


def source_material_to_exported_texture_guids(trace, source_materials, originals, exported, *, metrics=None, private_local_pointers=None, private_texture_routes=None):
    """Derive 3 texture GUIDs from 10 exact original/exported Material TexEnvs.

    This join uses source-authenticated Material21 PPtrs, the same-instance
    exporter Material21 source GUID trace, the true exported Material YAML,
    and the unchanged original texture property labels and UVs. Does not
    substitute a guessed texture name, GUID or encoded image.
    """
    validate_trace(trace, originals)
    if (type(source_materials) is not dict or len(source_materials) != 5
            or type(exported) is not dict):
        raise ValueError("untrusted_source_export_particle_Material_mapping")
    if metrics is not None:
        if type(metrics) is not dict or metrics:
            raise ValueError("unsafe_nonempty_texture_pointer_diagnostic")
        metrics.update({
            "source_original_Material21":len(source_materials),
            "selected_source_materials_with_export_trace":0,
            "source_original_TexEnv_slots_compared":0,
            "exported_Texture2D_PPtr_fileID_null":0,
            "exported_Texture2D_PPtr_fileID_nonzero":0,
            "exported_Texture2D_PPtr_type_0":0,
            "exported_Texture2D_PPtr_type_2":0,
            "exported_Texture2D_PPtr_type_3":0,
            "exported_Texture2D_PPtr_other_type":0,
            "exported_Texture2D_PPtr_fileID_2800000":0,
            "exported_Texture2D_PPtr_fileID_not_2800000":0,
            "source_to_export_texture_UV_pairs_verified":0,
            "source_Texture2D_to_export_GUIDs_unique":0,
            "source_Type0_local_texture_pointer_slots":0,
            "source_Type0_local_original_Texture2D_targets":0,
            "source_Type0_PPtr_nonzero_GUID_hints_not_used_as_export_image":0,
        })
    if private_local_pointers is not None and (
            type(private_local_pointers) is not dict or private_local_pointers):
        raise ValueError("invalid_private_original_local_pointer_outparam")
    if private_texture_routes is not None and (type(private_texture_routes) is not dict or private_texture_routes):
        raise ValueError("invalid_private_particle_texture_routes_outparam")
    mapped = {}
    outsider_pointers = set()
    for row in trace["objects"]:
        if not isinstance(row, dict) or row.get("class_id") != 21:
            continue
        key = identity(row["source"])
        if key not in source_materials:
            # An unrelated Material cannot also own a selected exported doc.
            dst = row.get("export")
            if type(dst) is dict and dst.get("type") in (2, 3):
                fid, guid, kind = pointer(dst)
                outsider_pointers.add((fid, guid))
            continue
        if key in mapped:
            raise ValueError("duplicate_particle_source_Material_trace")
        file_id, guid, kind = pointer(row["export"])
        if file_id <= 0 or kind not in ("2", "3") or guid in {ZERO, *BUILTIN}:
            raise ValueError("invalid_traced_particle_Material21_export")
        mapped[key] = (file_id, guid)
        if metrics is not None:
            metrics["selected_source_materials_with_export_trace"] = len(mapped)
    if set(mapped) != set(source_materials) or len(set(mapped.values())) != 5:
        raise ValueError("missing_original_particle_Material_same_export_trace")
    if set(mapped.values()) & outsider_pointers:
        raise ValueError("selected_particle_Material_export_document_collision")
    result = {}
    local_targets = set()
    routes = {}
    exact_slots = 0
    for source_key, ptr in mapped.items():
        if ptr not in exported:
            raise ValueError("missing_same_export_particle_Material_YAML")
        before, after = source_materials[source_key], exported[ptr]
        if set(before) != set(after):
            raise ValueError("changed_same_export_particle_Material_TexEnv_schema")
        for name in before:
            original_pointer, original_uv = before[name]
            exported_pointer, exported_uv = after[name]
            if metrics is not None:
                metrics["source_original_TexEnv_slots_compared"] += 1
            if (type(original_pointer) is not tuple or len(original_pointer) != 2
                    or type(original_pointer[0]) is not int or original_pointer[0] != 0
                    or type(original_pointer[1]) is not int or original_pointer[1] <= 0):
                raise ValueError("unverified_source_particle_texture_PPtr")
            texture_key = source_key[0], original_pointer[1]
            if texture_key not in originals:
                raise ValueError("particle_Material_source_Texture2D_not_in_3_authentic_targets")
            if type(exported_pointer) is not tuple or len(exported_pointer) != 3:
                raise ValueError("broken_same_export_particle_texture_Material_ref")
            file_id, guid, kind = exported_pointer
            if (type(file_id) is not int or type(guid) is not str or type(kind) is not int
                    or not re.fullmatch("[a-fA-F0-9]{32}", guid)):
                raise ValueError("broken_same_export_particle_texture_Material_ref")
            guid = guid.lower()
            if metrics is not None:
                metrics["exported_Texture2D_PPtr_fileID_null" if file_id == 0 else "exported_Texture2D_PPtr_fileID_nonzero"] += 1
                if kind in (0,2,3):
                    metrics["exported_Texture2D_PPtr_type_" + str(kind)] += 1
                else:
                    metrics["exported_Texture2D_PPtr_other_type"] += 1
                metrics["exported_Texture2D_PPtr_fileID_2800000" if file_id == 2800000 else "exported_Texture2D_PPtr_fileID_not_2800000"] += 1
            # A kind=0 PPtr with a nonzero fileID can be a Unity-local
            # reference, not a TextureImporter GUID. Keep the original source
            # target identity and the exact UV, but NEVER manufacture an
            # external GUID or count this as an exported PNG image.
            if file_id <= 0 or kind not in (0, 2, 3):
                raise ValueError("broken_same_export_particle_texture_Material_ref")
            actual = (file_id, guid, kind)
            if kind != 0:
                actual = external_image_pointer(actual)
            if kind == 0 and metrics is not None and guid.lower() != "0" * 32:
                # Type0 with nonzero GUID is a nonstandard same-export PPtr,
                # NOT proof of a standalone TextureImporter or image file.
                # Keep its source-authenticated owner/PathID and UV only.
                metrics["source_Type0_PPtr_nonzero_GUID_hints_not_used_as_export_image"] += 1
            if (type(original_uv) is not tuple or type(exported_uv) is not tuple
                    or len(original_uv) != 4 or len(exported_uv) != 4):
                raise ValueError("missing_same_export_particle_texture_UV")
            import math
            if (any(type(v) not in (float, int) or not math.isfinite(v)
                    for v in original_uv + exported_uv)
                    or any(not math.isclose(a,b,abs_tol=1e-6,rel_tol=1e-6)
                           for a,b in zip(original_uv, exported_uv))):
                raise ValueError("changed_same_export_particle_texture_UV")
            if metrics is not None:
                metrics["source_to_export_texture_UV_pairs_verified"] += 1
            route = routes.setdefault(texture_key, {"pointer": actual, "slots": 0, "document_guids": set()})
            if route["pointer"] != actual:
                if kind == 0 and route["pointer"][2] == 0:
                    raise ValueError("one_original_local_Texture2D_has_conflicting_exported_PPtrs")
                if kind != 0 and route["pointer"][2] != 0:
                    if route["pointer"][1] != guid:
                        raise ValueError("one_original_particle_Texture2D_maps_to_two_export_GUIDs")
                    raise ValueError("one_original_particle_Texture2D_has_conflicting_exported_PPtrs")
                raise ValueError("one_original_particle_Texture2D_mixed_local_external_export")
            route["slots"] += 1
            route["document_guids"].add(ptr[1])
            if kind == 0:
                if texture_key in result:
                    raise ValueError("one_original_particle_Texture2D_mixed_local_external_export")
                local_targets.add(texture_key)
                if private_local_pointers is not None:
                    old=private_local_pointers.setdefault(texture_key,(file_id,guid.lower(),kind))
                    if old!=(file_id,guid.lower(),kind):
                        raise ValueError("one_original_local_Texture2D_has_conflicting_exported_PPtrs")
                if metrics is not None:
                    metrics["source_Type0_local_texture_pointer_slots"] += 1
                    metrics["source_Type0_local_original_Texture2D_targets"] = len(local_targets)
            else:
                if texture_key in local_targets:
                    raise ValueError("one_original_particle_Texture2D_mixed_local_external_export")
                if texture_key in result and result[texture_key] != guid:
                    raise ValueError("one_original_particle_Texture2D_maps_to_two_export_GUIDs")
                result[texture_key] = guid
                if metrics is not None:
                    metrics["source_Texture2D_to_export_GUIDs_unique"] = len(set(result.values()))
            exact_slots += 1
    covered = set(result) | local_targets
    if (covered != set(originals) or set(result) & local_targets
            or len(set(result.values())) != len(result)
            or exact_slots != 10
            or len(local_targets) not in (0, 1)
            or (len(local_targets) == 1 and len(result) != 2)
            or (not local_targets and len(result) != EXPECTED_TARGETS)):
        raise ValueError("incomplete_original_particle_Material_TexEnv_10_to_3_join")
    if private_texture_routes is not None:
        private_texture_routes.update(routes)
    return result


def verify_external_texture_guid_subset(direct_mapping, material_mapping):
    """The same source local type0 PPtr is not an external TextureImporter GUID.

    Trace may independently identify three source Texture2D exports, while
    the Material's exact ten TexEnv slots expose only two external GUIDs
    and one local type0 pointer. Compare only truly external source keys;
    never pretend the local pointer is an exported image or replace its GUID.
    """
    if direct_mapping is None:
        return
    if (type(direct_mapping) is not dict or type(material_mapping) is not dict
            or not set(material_mapping).issubset(direct_mapping)
            or any(direct_mapping[key] != guid
                   for key, guid in material_mapping.items())):
        raise ValueError("original_texture_trace_and_Material_YAML_GUID_mismatch")


def classify_original_local_texture_trace(trace, local_pointers):
    """Check original local Material PPtr against SAME export's Texture2D28 trace.

    A type0 PPtr may be an internal reference and MUST NOT be promoted to
    an external image GUID. Even when a matching source Texture2D trace
    object exists, this is only pointer identity, not pixel restoration.
    Return aggregate counts only; never publish owner, PathID or GUID.
    """
    if (type(trace) is not dict or type(local_pointers) is not dict
            or len(local_pointers)!=1 or not isinstance(trace.get("objects"),list)):
        raise ValueError("invalid_local_Texture2D_export_trace_proof_scope")
    [(target,local)]=list(local_pointers.items())
    if (not isinstance(target,tuple) or len(target)!=2
            or type(local)!=tuple or len(local)!=3 or local[2]!=0
            or type(local[0]) is not int or local[0]<=0):
        raise ValueError("unverified_original_local_Texture2D_PPtr")
    rows=[]
    for row in trace["objects"]:
        if type(row) is not dict or row.get("class_id")!=28:
            continue
        if identity(row["source"])==target:
            rows.append(row)
    if len(rows)>1:
        raise ValueError("ambiguous_source_Texture2D28_local_trace_rows")
    if not rows:
        return {"same_export_original_local_Texture2D28_trace_rows":0,
                "same_export_original_local_PPtr_matches_Texture2D28_trace":False,
                "original_local_Type0_Texture2D_export_status":"NO_DIRECT_SOURCE_TEXTURE28_TRACE",
                "original_local_Type0_collection_exportable":None,
                "original_local_Type0_nonexportable_collection_proven":False,
                "original_local_Type0_external_GUID_inferred":False}
    # A same-instance pointer does not imply a separately exported image.
    # Preserve missing legacy metadata as unknown; do not infer from type0.
    exportable=rows[0].get("exportable")
    if exportable is not None and type(exportable) is not bool:
        raise ValueError("invalid_local_Texture2D_exportability")
    fid,guid,kind=pointer(rows[0]["export"])
    is_match=(fid,guid,int(kind))==local
    return {"same_export_original_local_Texture2D28_trace_rows":1,
            "same_export_original_local_PPtr_matches_Texture2D28_trace":is_match,
            "original_local_Type0_collection_exportable":exportable,
            "original_local_Type0_nonexportable_collection_proven":(
                is_match and exportable is False),
            "original_local_Type0_Texture2D_export_status":(
                "ORIGINAL_LOCAL_POINTER_EXACT_TRACE_MATCH" if is_match
                else "SOURCE_TEXTURE_TRACE_POINTER_DIFFERS_FROM_LOCAL_MATERIAL_PPTR"),
            "original_local_Type0_external_GUID_inferred":False}


def original_local_type0_source_pixel_alpha(original, private_local_pointers, manifest=None):
    """Decode exact source bytes; no local export image is inferred."""
    if type(private_local_pointers) is not dict or len(private_local_pointers)!=1:
        raise ValueError("invalid_original_local_Texture2D28_source_pixel_scope")
    [(key,local_ptr)]=list(private_local_pointers.items())
    if type(local_ptr) is not tuple or len(local_ptr)!=3 or local_ptr[2]!=0:
        raise ValueError("unverified_original_local_Texture2D28_source_identity")
    source_image,kind=decode_original_texture(original,manifest,key)
    return {
        "original_local_Type0_Texture2D28_source_top_mip_alpha_decoded":True,
        "original_local_Type0_Texture2D28_source_top_mip_alpha_profile":alpha_profile(source_image),
        "original_local_Type0_source_payload_kind":kind,
        "original_local_Type0_source_payload_byte_binding_verified":True,
        "original_local_Type0_texture_has_exported_image_proof":False,
        "original_local_Type0_original_and_exported_pixels_compared":False,
        "source_original_texture_bytes_or_identifiers_disclosed":False,
    }


def image_meta_index(assets, wanted):
    """Use exactly the previously traced GUIDs; never infer assets by names."""
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_exported_Unity_Assets")
    indexed = {}
    files = sorted(assets.rglob("*"))
    if len(files) > 150000 or any(path.is_symlink() for path in files):
        raise ValueError("unsafe_exported_asset_inventory")
    for meta in files:
        if not meta.is_file() or not meta.name.endswith(".meta"):
            continue
        if meta.stat().st_size > MAX_META:
            continue
        text = meta.read_text(encoding="utf-8-sig")
        found = GUID.findall(text)
        if len(found) != 1 or found[0].lower() not in wanted:
            continue
        guid = found[0].lower()
        image = meta.with_suffix("")
        if guid in indexed:
            raise ValueError("duplicate_particle_exported_Texture2D_GUID")
        if (not image.is_file() or image.is_symlink()
                or image.suffix.lower() not in IMAGES or not is_texture(image, text, 2800000)):
            raise ValueError("selected_particle_Texture2D_not_exported_as_image")
        fields = {}
        for name in META_FIELDS:
            matches = re.findall(r"(?m)^\s+" + name + r":\s*(-?\d+)\s*$", text)
            fields[name] = int(matches[0]) if len(matches) == 1 else None
        indexed[guid] = (image, fields, True)
    if set(indexed) != set(wanted):
        raise ValueError("selected_particle_texture_image_importer_missing")
    return indexed


def analyze_exported_images(index, *, expected_count=EXPECTED_TARGETS):
    from PIL import Image
    total = Counter()
    importer_values = {k: Counter() for k in META_FIELDS}
    for path, fields, is_importer in index.values():
        if not is_importer or not 0 < path.stat().st_size <= MAX_IMAGE_BYTES:
            raise ValueError("particle_image_or_importer_unusable")
        with Image.open(path) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("particle_image_multiframe_unproven")
            profile = alpha_profile(image)
        total["linked_exported_images_decoded"] += 1
        for key, truth in profile.items():
            total[key] += int(truth)
        for key, value in fields.items():
            importer_values[key]["missing" if value is None else str(value)] += 1
        if profile["has_transparent_pixels"]:
            # Metadata hazard, not proof of what Unity imported or rendered.
            alpha_source = fields.get("alphaSource")
            label = {0: "none", 1: "input", 2: "grayscale"}.get(alpha_source, "unknown")
            total["nonopaque_source_image_alphaSource_" + label] += 1
    if (expected_count not in (2, EXPECTED_TARGETS)
            or total["linked_exported_images_decoded"] != expected_count):
        raise ValueError("missing_exported_particle_alpha_classification")
    return total, {key: dict(sorted(value.items())) for key, value in importer_values.items()}


def audit(original, manifest, project, trace_path, *, checkpoint=None, trace_metrics=None, material_metrics=None):
    def mark(step):
        if checkpoint is not None:
            checkpoint(step)
    original = original.absolute()
    project = project.absolute()
    trace_path = trace_path.absolute()
    if (not original.is_dir() or original.is_symlink()
            or project.is_symlink() or trace_path.is_symlink()
            or not trace_path.is_file()
            or trace_path.is_relative_to(project)
            or any(path.is_symlink() for path in (original, project, trace_path))):
        raise ValueError("unsafe_original_or_exported_particle_data")
    mark("original_material_shader_Texture2D_PPtrs")
    original_targets = {}
    original_material_texenvs = {}
    materials = material_source.run(
        original, manifest, private_local_texture_targets=original_targets,
        private_material_texenvs=original_material_texenvs)
    mark("original_Texture2D28_manifest_and_stream")
    source = texture_source.run(original, manifest)
    if (materials["status"] != material_source.STATUS
            or source["status"] != texture_source.STATUS
            or source["original_selected_typed_Texture2D28_targets"] != EXPECTED_TARGETS
            or sum(original_targets.values()) != 10):
        raise ValueError("unverified_particle_original_Texture2D_scope")
    if trace_path.stat().st_size > 40 * 1024 * 1024:
        raise ValueError("oversize_private_export_trace")
    mark("read_private_export_trace")
    trace = strict_json(read_snapshot(trace_path, TRACE_LIMIT))
    mark("join_same_export_Texture2D28_GUID")
    trace_exportability={}
    selected = selected_texture_trace(trace, original_targets, metrics=trace_metrics,
                                      private_exportability=trace_exportability)
    mark("parse_exported_Material_TexEnv_YAML")
    from scripts.b05_verify_material_texenv_bindings import exported_texenvs
    local_documents={}
    exported_materials = exported_texenvs(project,private_texture_documents=local_documents)
    mark("join_original_Material_TexEnv_to_exported_Texture2D_GUID")
    local_pointers, routes = {}, {}
    mapping = source_material_to_exported_texture_guids(
        trace, original_material_texenvs, original_targets, exported_materials,
        metrics=material_metrics, private_local_pointers=local_pointers,
        private_texture_routes=routes)
    if any(routes[key]["slots"]!=count for key,count in original_targets.items()):
        raise ValueError("particle_original_target_slot_count_mismatch")
    provenance = compare_texture_trace_routes(selected, routes, local_documents=local_documents,
                                               exportability=trace_exportability)
    mark("classify_same_export_local_Texture2D28_type0_pointer")
    local_proof=(classify_original_local_texture_trace(trace,local_pointers)
                 if local_pointers else {
                     "same_export_original_local_Texture2D28_trace_rows":0,
                     "same_export_original_local_PPtr_matches_Texture2D28_trace":False,
                     "original_local_Type0_Texture2D_export_status":"NO_LOCAL_PPTR",
                     "original_local_Type0_collection_exportable":None,
                     "original_local_Type0_nonexportable_collection_proven":False,
                     "original_local_Type0_external_GUID_inferred":False})
    local_identity_proven=bool(provenance["document_scoped_local_targets_proven"])
    if local_identity_proven:
        local_proof["original_local_Type0_Texture2D_export_status"]="ORIGINAL_LOCAL_DOCUMENT_SCOPED_TARGET_IDENTITY_PROVEN"
    local_document_count = sum(len(route["document_guids"]) for route in routes.values()
                               if route["pointer"][2] == 0)
    mark("decode_original_local_type0_Texture2D28_top_mip")
    source_local_alpha={
        "original_local_Type0_Texture2D28_source_top_mip_alpha_decoded":False,
        "original_local_Type0_Texture2D28_source_top_mip_alpha_profile":None,
        "original_local_Type0_texture_has_exported_image_proof":False,
        "original_local_Type0_original_and_exported_pixels_compared":False,
        "source_original_texture_bytes_or_identifiers_disclosed":False,
    }
    if local_pointers:
        try:
            source_local_alpha=original_local_type0_source_pixel_alpha(original,local_pointers,manifest)
        except Exception as failure:
            # The original image can depend on a separate verified .resS
            # decoder. An unavailable source mip must remain inconclusive,
            # never be silently fabricated from an exported image.
            source_local_alpha["original_local_Type0_source_alpha_safe_error_type"]=type(failure).__name__
    mark("locate_exported_TextureImporter_image")
    if len(mapping) not in (2, EXPECTED_TARGETS):
        raise ValueError("incomplete_original_particle_two_external_texture_alpha_scope")
    local_count = EXPECTED_TARGETS - len(mapping)
    if material_metrics is not None:
        if material_metrics.get("source_Type0_local_original_Texture2D_targets") != local_count:
            raise ValueError("original_local_texture_pointer_metrics_drift")
        if material_metrics.get("source_to_export_texture_UV_pairs_verified") != 10:
            raise ValueError("original_full_source_to_export_texenv_UV_drift")
    exported = image_meta_index(project / "Assets", set(mapping.values()))
    mark("decode_exported_image_alpha")
    counts, importers = analyze_exported_images(exported, expected_count=len(mapping))
    mark("compare_byte_bound_source_export_top_mip_pixels")
    parity = external_parity(original,manifest,selected,routes,exported)
    mark("completed")
    all_proven = provenance["all_selected_texture_targets_independently_traced"]
    all_image_routes_proven = not local_count and all_proven
    return {
        "schema_version": 4,
        "status": PARTIAL_STATUS if local_count else STATUS if all_proven else UNPROVEN_STATUS,
        "source_original_texture2d_sha_verified": True,
        "source_particle_material_to_texture_references": 10,
        "source_original_texture2d_objects": EXPECTED_TARGETS,
        "same_export_source_texture_guids_joined": len(mapping),
        "same_export_original_Material_TexEnv_slots_compared": 10,
        "same_export_original_Material_TexEnv_PPtr_slots_exact": (provenance["independently_traced_external_slots"]
                                                                  +provenance["document_scoped_local_slots_proven"]),
        "local_type0_Material_document_count": local_document_count,
        "local_type0_exported_target_identity_proven": local_identity_proven,
        **provenance,
        "source_SHA_original_Texture2D28_local_type0_pointer_targets": local_count,
        "same_export_original_external_TextureImporter_images_confirmed": len(mapping),
        "source_original_all_three_Texture2D_as_exported_images_verified": all_image_routes_proven,
        **local_proof,
        **source_local_alpha,
        "original_local_Type0_texture_pixel_alpha_verified": False,
        "original_texture_direct_export_trace_guid_usable": all_image_routes_proven,
        "original_material_same_export_GUID_and_UV_linkage_verified": all_image_routes_proven,
        "original_material_exact_texture_PPtr_and_UV_routes_checked": all_proven,
        "source_to_export_UV_slots_compared": 10,
        "actual_exported_alpha_image_counts": dict(sorted(counts.items())),
        "exported_importer_metadata_numeric_counts": importers,
        "original_source_texture_pixels_compared": parity["coordinate_compared_targets"] > 0,
        "texture_alpha_loss_from_original_proven": parity["targets_with_alpha_loss"] > 0,
        "texture_all_source_transparency_lost_in_export_targets": parity["targets_with_all_transparency_lost"],
        "source_export_byte_bound_top_mip_parity": parity,
        "all_three_source_export_RGBA8_samples_equal": all_proven and parity["exact_rgba8_targets"] == EXPECTED_TARGETS,
        "correct_runtime_particle_shader_blend_proven": False,
        "android_device_fire_pixels_verified": False,
        "original_source_or_exported_assets_modified": False,
        "private_ids_guids_paths_or_pixels_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("original", "manifest", "project", "trace", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    if (a.out.is_symlink() or a.out.exists() or
            a.out.resolve().is_relative_to(a.project.resolve()) or
            a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_particle_alpha_report_destination")
    progress = {"stage": "input_paths_and_layout"}
    numeric_trace_metrics = {}
    numeric_material_metrics = {}
    stages = {
        "input_paths_and_layout",
        "original_material_shader_Texture2D_PPtrs",
        "original_Texture2D28_manifest_and_stream",
        "read_private_export_trace",
        "join_same_export_Texture2D28_GUID",
        "parse_exported_Material_TexEnv_YAML",
        "join_original_Material_TexEnv_to_exported_Texture2D_GUID",
        "classify_same_export_local_Texture2D28_type0_pointer",
        "decode_original_local_type0_Texture2D28_top_mip",
        "locate_exported_TextureImporter_image",
        "decode_exported_image_alpha",
        "compare_byte_bound_source_export_top_mip_pixels",
        "completed",
    }
    def mark(stage):
        if stage not in stages:
            raise ValueError("invalid_private_diagnostic_stage")
        progress["stage"] = stage
    try:
        report = audit(a.original, a.manifest, a.project, a.trace, checkpoint=mark,
                       trace_metrics=numeric_trace_metrics, material_metrics=numeric_material_metrics)
    except Exception as error:
        report = {
            "schema_version": 1,
            "status": "INCONCLUSIVE",
            "error_type": type(error).__name__,
            "failure_code": (str(error) if str(error) in ["untrusted_particle_source_export_linkage","duplicated_original_particle_Texture2D_export","invalid_same_export_Texture2D_pointer","invalid_same_export_Texture2D_image_pointer","particle_original_target_slot_count_mismatch","invalid_local_Texture2D_exportability","original_texture_trace_and_Material_YAML_PPtr_mismatch","selected_particle_Material_export_document_collision","one_original_particle_Texture2D_has_conflicting_exported_PPtrs","one_original_local_Texture2D_has_conflicting_exported_PPtrs","particle_image_multiframe_unproven","original_particle_Texture2D_Guid_not_unique","untrusted_source_export_particle_Material_mapping","duplicate_particle_source_Material_trace","invalid_traced_particle_Material21_export","missing_original_particle_Material_same_export_trace","missing_same_export_particle_Material_YAML","changed_same_export_particle_Material_TexEnv_schema","unverified_source_particle_texture_PPtr","particle_Material_source_Texture2D_not_in_3_authentic_targets","broken_same_export_particle_texture_Material_ref","missing_same_export_particle_texture_UV","changed_same_export_particle_texture_UV","one_original_particle_Texture2D_maps_to_two_export_GUIDs","incomplete_original_particle_Material_TexEnv_10_to_3_join","original_texture_trace_and_Material_YAML_GUID_mismatch","untrusted_original_local_Texture2D_nonzero_GUID","one_original_particle_Texture2D_mixed_local_external_export","incomplete_original_particle_two_external_texture_alpha_scope","original_local_texture_pointer_metrics_drift","original_full_source_to_export_texenv_UV_drift","selected_particle_Texture2D_not_exported_as_image","selected_particle_texture_image_importer_missing","particle_image_or_importer_unusable","missing_exported_particle_alpha_classification","Missing/redirected Unity Assets root","Linked export path is unsafe","Missing or linked Material metadata","Invalid exported Material GUID","Malformed private Material YAML","Duplicate exported Material YAML mapping key","Material texture data absent in export","Duplicated exported Material pointer","No exported Material texture documents"]
                             else "UNCLASSIFIED_SAFE_ERROR"),
            "failure_stage": progress["stage"],
            "trace_source_export_match_counts": numeric_trace_metrics,
            "source_Material21_to_export_Texture2D_pointer_counts": numeric_material_metrics,
            "android_device_fire_pixels_verified": False,
            "private_ids_guids_paths_or_pixels_published": False,
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("GT_PARTICLE108_EXPORTED_TEXTURE_ALPHA " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] in (STATUS, PARTIAL_STATUS, UNPROVEN_STATUS) else 2


if __name__ == "__main__":
    raise SystemExit(main())
