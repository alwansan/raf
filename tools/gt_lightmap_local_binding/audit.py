"""G6: typed local lightmap pointer and renderer-slot admission, source only.

This is a stricter *additional* audit, not a reinterpretation of B21 presence
counts. Operates on one serialized scene's object table. Never reads external
providers, invents GUIDs, mutates data, or asserts export/runtime parity.
"""
from collections import Counter
from scripts.b21_scene_lightmap_links import (
    LIGHTMAP_PROPS, MAX_LIGHTMAPS, MAX_OBJECTS, RENDERERS, SourceError,
    pointer_state,
)

def native_type(obj):
    kind = getattr(obj, "type", None)
    name = getattr(kind, "name", None)
    cid = getattr(kind, "value", None)
    return name, cid if type(cid) is int else None

def typed_pointer(value, objects):
    state = pointer_state(value, objects.keys())
    if state != "local_target_present":
        return state
    name, cid = native_type(objects[value["m_PathID"]])
    if name == "Texture2D" and cid == 28:
        return "local_texture2d"
    if name is None or cid is None or (name == "Texture2D") != (cid == 28):
        return "local_target_type_unverified"
    return "local_target_wrong_class"

def analyze(objects):
    if len(objects) > MAX_OBJECTS:
        raise SourceError("scene_objects_over_budget")
    table = {}
    for obj in objects:
        pid = getattr(obj, "path_id", None)
        if type(pid) is not int or pid <= 0:
            raise SourceError("invalid_object_path_id")
        if pid in table:
            raise SourceError("duplicate_object_path_id")
        table[pid] = obj
    counts = Counter()
    settings = []
    assigned = []
    for obj in objects:
        kind, _ = native_type(obj)
        if kind != "LightmapSettings" and kind not in RENDERERS:
            continue
        try:
            tree = obj.read_typetree(check_read=False)
        except Exception:
            tree = None
        if kind == "LightmapSettings":
            counts["settings_objects"] += 1
            maps = tree.get("m_Lightmaps") if isinstance(tree, dict) else None
            if not isinstance(maps, list):
                counts["settings_undecodable"] += 1
                maps = None
            elif len(maps) > MAX_LIGHTMAPS:
                raise SourceError("lightmap_array_over_budget")
            # Count physical objects, not merely decoded arrays.
            settings.append(maps)
            continue
        counts["renderer_objects"] += 1
        index = tree.get("m_LightmapIndex") if isinstance(tree, dict) else None
        if type(index) is not int:
            counts["renderer_index_unknown"] += 1
        elif index in (-1, 65535):
            counts["renderer_unassigned"] += 1
        elif index == 65534:
            # Do not treat the reserved value as an ordinary array offset.
            counts["renderer_index_reserved_unverified"] += 1
        elif 0 <= index < 65534:
            assigned.append(index)
        else:
            counts["renderer_index_unknown"] += 1
    counts["renderer_assigned"] = len(assigned)
    if len(settings) != 1 or settings[0] is None:
        counts["renderer_settings_unresolved"] = len(assigned)
        counts["settings_ambiguous_or_missing"] = 1
    else:
        maps = settings[0]
        counts["map_entries"] = len(maps)
        local_complete = []
        color_states = []
        for entry in maps:
            fields = entry if isinstance(entry, dict) else {}
            states = {key: typed_pointer(fields.get(key), table) for key in LIGHTMAP_PROPS}
            for key, state in states.items():
                counts[key + "_" + state] += 1
            color = states["m_LightmapColor"]
            color_states.append(color)
            local_complete.append(color == "local_texture2d" and all(
                states[key] in ("null_pointer", "local_texture2d")
                for key in ("m_LightmapDir", "m_ShadowMask")
            ))
        for index in assigned:
            if index >= len(maps):
                counts["renderer_index_out_of_range"] += 1
            elif local_complete[index]:
                counts["renderer_local_texture_links_complete"] += 1
            else:
                counts["renderer_in_range_but_texture_links_unresolved"] += 1
                counts["renderer_color_" + color_states[index]] += 1
    complete = counts["renderer_local_texture_links_complete"]
    return {
        "counts": dict(sorted(counts.items())),
        "all_assigned_renderers_local_texture_links_complete": bool(assigned) and complete == len(assigned)
            and not counts["renderer_index_unknown"] and not counts["renderer_index_reserved_unverified"],
        "external_provider_targets_verified": False,
        "source_export_pptr_mapping_proven": False,
        "lighting_pixels_or_device_proven": False,
        "assets_mutated": False,
    }
