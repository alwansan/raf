"""Source-scene context admission for Particle108 (NO PLAYER, no alpha replay).

The original scene, exact material and shader owners are authenticated again.
Serialized camera/quality state is evidence of context, not a runtime selection.
Only aggregate counts leave the runner; missing runtime depth is never assumed.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

STATUS = "OBSERVED_ORIGINAL_PARTICLE108_SCENE_CONTEXT"
SWITCHES = {"SOFTPARTICLES_ON", "INSTANCING_ON"}

class Reject(ValueError):
    pass

def need(ok, code):
    if not ok:
        raise Reject(code)

def bit(value):
    return int(value) if type(value) in (bool, int) and value in (0, 1) else None

def local(pointer, allow_null=False):
    need(type(pointer) is dict and set(pointer) == {"m_FileID", "m_PathID"}
         and type(pointer["m_FileID"]) is int and pointer["m_FileID"] == 0
         and type(pointer["m_PathID"]) is int, "nonlocal_scene_pointer")
    pid = pointer["m_PathID"]
    need(pid != 0 or allow_null, "null_scene_pointer")
    return pid

def members(go):
    from tools.gt_particle108_native_route.emitter import component_ptr
    ids = [local(component_ptr(x)) for x in go["m_Component"]]
    need(len(ids) == len(set(ids)), "duplicate_scene_component")
    return ids

def hierarchy(go_id, read, kind):
    """Trace exact GameObject/Transform ownership and reciprocal parent links."""
    seen = set()
    child = None
    active = []
    while True:
        need(go_id not in seen and len(seen) < 256, "scene_hierarchy_cycle")
        seen.add(go_id)
        go = read(go_id, "GameObject")
        transforms = [i for i in members(go) if kind(i) in ("Transform", "RectTransform")]
        need(len(transforms) == 1, "scene_transform_not_unique")
        tid = transforms[0]
        tf = read(tid, kind(tid))
        need(local(tf["m_GameObject"]) == go_id, "transform_owner_mismatch")
        if child is not None:
            children = [local(x) for x in tf["m_Children"]]
            need(len(children) == len(set(children)) and child in children,
                 "nonreciprocal_scene_parent")
        active.append(bit(go.get("m_IsActive")))
        father = local(tf["m_Father"], allow_null=True)
        if not father:
            break
        need(kind(father) in ("Transform", "RectTransform"), "scene_parent_class")
        child = tid
        go_id = local(read(father, kind(father))["m_GameObject"])
        need(father in members(read(go_id, "GameObject")), "parent_transform_not_member")
    state = 0 if 0 in active else None if None in active else 1
    return state, len(seen)

def camera_candidate(camera, active, layer):
    mask = camera.get("m_CullingMask")
    if type(mask) is dict and set(mask) == {"m_Bits"}:
        mask = mask["m_Bits"]
    enabled = bit(camera.get("m_Enabled"))
    need(type(layer) is int and 0 <= layer < 32, "scene_layer_schema")
    if enabled == 0 or active == 0:
        return "inactive", "not_applicable"
    if enabled is None or active is None or type(mask) is not int or not -(2**31) <= mask < 2**32:
        return "unclassified", "unknown"
    if not ((mask & 0xffffffff) & (1 << layer)):
        return "excluded_layer", "not_applicable"
    # m_Depth is ordering, not DepthTextureMode. Absence is UNKNOWN.
    depth = camera.get("m_DepthTextureMode")
    if type(depth) is not int or not 0 <= depth <= 7:
        return "eligible_layer", "unknown"
    return "eligible_layer", "depth_requested" if depth & 1 else "no_depth_bit"

def exact_variant(routes, bits, observed):
    """No default route: reject unknown, incomplete and wrong branch identity."""
    need(set(routes) == {(0,0), (0,1), (1,0), (1,1)}
         and set(routes.values()) == {0,1,2,3}, "incomplete_route_lattice")
    need(type(bits) is tuple and len(bits) == 2
         and all(type(x) is int and x in (0,1) for x in bits), "unknown_route_bits")
    need(type(observed) is int and observed == routes[bits], "route_identity_mismatch")
    return observed

def reject_wrong_routes(routes):
    rejected = 0
    for bits, expected in routes.items():
        exact_variant(routes, bits, expected)
        for wrong in set(routes.values()) - {expected}:
            try:
                exact_variant(routes, bits, wrong)
            except Reject:
                rejected += 1
            else:
                raise Reject("wrong_variant_accepted")
    need(rejected == 12, "wrong_route_control_coverage")
    return rejected

def quality_context(tree):
    levels = tree.get("m_QualitySettings")
    if type(levels) is not list:
        return {"quality_levels": 0, "quality_soft_on": 0, "quality_soft_off": 0,
                "quality_soft_unknown": 0, "quality_schema_known": False}
    counts = Counter()
    for level in levels:
        if type(level) is not dict:
            counts["unknown"] += 1
            continue
        keys = [k for k in ("softParticles", "m_SoftParticles") if k in level]
        v = bit(level[keys[0]]) if len(keys) == 1 else None
        counts[{0:"off",1:"on",None:"unknown"}[v]] += 1
    return {"quality_levels": len(levels), "quality_soft_on": counts["on"],
            "quality_soft_off": counts["off"], "quality_soft_unknown": counts["unknown"],
            "quality_schema_known": True}

def observe(original, manifest, out):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.b21_scene_lightmap_links import PIN, verify_source
    from scripts.b04_restore_original_color_settings import ORIGINAL_SIZE, ORIGINAL_SHA256
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_probe_original_shader_links import resolve_pointer
    from scripts.t3_particle108_private_keyword_routed_shaderlab import source_routes
    from scripts.t3_original_particle_shader_state import inspect_parsed
    from tools.gt_particle108_native_route import emitter, probe
    data = original / "Raft_Data"
    rows = {}
    out["phase"] = "authenticated_emitter_join"
    old = emitter.census(original, manifest, private_rows=rows)
    need(old["status"] == emitter.STATUS and len(rows) == 12, "source_emitter_scope")
    out["phase"] = "material_and_source_routes"
    mats = set().union(*(x["selected_materials"] for x in rows.values()))
    need(len(mats) == 1, "selected_material_scope")
    files = {}
    def load(owner, pin):
        if owner not in files:
            path = data / owner
            need(path.is_file() and not path.is_symlink() and fingerprint(path) == pin,
                 "source_owner_fingerprint")
            files[owner] = UnityPy.load(str(path)).file
        return files[owner]
    mo, mid = next(iter(mats))
    mf = load(mo, SHADER_OWNERS[mo])
    m = mf.objects[mid]
    need(m.type.name == "Material", "source_material_class")
    mt = m.read_typetree()
    shader = resolve_pointer(mo, [x.path for x in mf.externals], mt["m_Shader"])
    need(shader is not None and shader[0] in SHADER_OWNERS, "source_shader_pointer")
    sf = load(shader[0], SHADER_OWNERS[shader[0]])
    so = sf.objects[shader[1]]
    need(so.type.name == "Shader", "source_shader_class")
    parsed = so.read_typetree()["m_ParsedForm"]
    switches, routes = source_routes(parsed)
    need(set(switches) == SWITCHES, "source_switch_scope")
    valid, invalid = probe.keywords(mt)
    bits = tuple(int(x in valid | invalid) for x in switches)
    saved = probe.choose_route(valid | invalid, switches, routes)
    exact_variant(routes, bits, saved)
    out.update(source_original_route_count=len(routes), source_saved_material_route=saved,
               source_saved_soft_keyword=int("SOFTPARTICLES_ON" in valid | invalid),
               source_saved_instancing_keyword=int("INSTANCING_ON" in valid | invalid),
               source_material_instancing_flag=bit(mt.get("m_EnableInstancingVariants")),
               source_wrong_route_controls_rejected=reject_wrong_routes(routes),
               source_fixed_function_state=inspect_parsed(parsed))
    out["phase"] = "source_quality_context"
    gf = load("globalgamemanagers", (ORIGINAL_SIZE, ORIGINAL_SHA256))
    quality = [x for x in gf.objects.values() if x.type.name == "QualitySettings"]
    need(len(quality) <= 1, "quality_settings_not_unique")
    out["source_quality"] = quality_context(quality[0].read_typetree(check_read=False) if quality else {})
    out["phase"] = "source_scene_hierarchy_camera_context"
    counts = Counter()
    for owner in sorted({key[0] for key in rows}):
        verify_source(data / owner, PIN[owner])
        scene = load(owner, PIN[owner])
        objs = scene.objects
        cache = {}
        def kind(pid):
            obj = objs.get(pid)
            return None if obj is None else obj.type.name
        def read(pid, cls):
            need(kind(pid) == cls, "scene_component_class")
            if pid not in cache:
                cache[pid] = objs[pid].read_typetree(check_read=False)
            return cache[pid]
        cameras = []
        for obj in objs.values():
            if obj.type.name != "Camera":
                continue
            cam = read(obj.path_id, "Camera")
            gid = local(cam["m_GameObject"])
            need(obj.path_id in members(read(gid, "GameObject")), "camera_not_member")
            active, _ = hierarchy(gid, read, kind)
            cameras.append((cam, active))
        counts["source_scenes_with_selected_emitters"] += 1
        counts["scene_camera_components"] += len(cameras)
        for (own, rid), row in sorted(rows.items()):
            if own != owner:
                continue
            gid = row["go_key"][1]
            go = read(gid, "GameObject")
            need(rid in members(go), "renderer_not_member")
            active, length = hierarchy(gid, read, kind)
            ren = row["renderer"]
            counts["emitters_with_hierarchy"] += 1
            counts["emitters_parented"] += int(length > 1)
            counts["emitter_hierarchy_" + {0:"inactive",1:"active",None:"unknown"}[active]] += 1
            for field, prefix in (("m_Enabled","renderer_enabled"),
                                  ("m_EnableGPUInstancing","renderer_gpu_instancing")):
                value = bit(ren.get(field))
                counts[prefix + "_" + {0:"off",1:"on",None:"unknown"}[value]] += 1
            eligible = 0
            for cam, cam_active in cameras:
                status, depth = camera_candidate(cam, cam_active, go.get("m_Layer"))
                counts["camera_pair_" + status] += 1
                if status == "eligible_layer":
                    eligible += 1
                    counts["eligible_camera_depth_" + depth] += 1
            counts["emitters_with_layer_eligible_camera"] += int(eligible > 0)
            counts["emitters_without_layer_eligible_camera"] += int(eligible == 0)
            counts["emitters_with_multiple_layer_eligible_cameras"] += int(eligible > 1)
    need(counts["emitters_with_hierarchy"] == 12, "scene_context_coverage")
    out["counts"] = dict(counts)
    out.update(status=STATUS, phase="complete", source_scene_context_observed=True)

def main():
    p = argparse.ArgumentParser()
    for key in ("original", "manifest", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    need(not a.out.exists() and not a.out.resolve().is_relative_to(a.original.resolve()), "unsafe_report_path")
    out = dict(status="INCONCLUSIVE", phase="start", source_scene_context_observed=False,
               original_keyword_scope_verified=False, engine_depth_texture_bound=False,
               runtime_keyword_selection_verified=False, black_fire_restored=False,
               Android_device=False, production=False, XAPK=False, private_payload_published=False)
    try:
        observe(a.original, a.manifest, out)
    except Reject as e:
        out["failure_category"] = str(e)
    except Exception as e:
        out["failure_type"] = type(e).__name__
    with a.out.open("x") as f:
        json.dump(out, f, sort_keys=True, allow_nan=False, indent=2)
        f.write("\n")
    print("GT_PARTICLE108_SOURCE_SCENE_CONTEXT " + json.dumps(out, sort_keys=True))
    return 0 if out["status"] == STATUS else 2

if __name__ == "__main__":
    raise SystemExit(main())
