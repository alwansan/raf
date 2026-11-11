"""Reconstruct bounded M02 clip poses from typed source and packed channels."""
import argparse
from bisect import bisect_right
import json
import math
from pathlib import Path
import struct
import zlib

from gfxlab.tools.gfx107_source_bindpose_math import source_matrix4, source_world_matrix
from gfxlab.tools.gfx108_indexed_skinning_cpu import (
    decoded_handler_skin, positions_from_parsed_mesh, skin_positions_cpu,
)
from gfxlab.tools.gfx108_original_indexed_skin_cpu import direct_mesh_handler
from gfxlab.tools.gfx110_original_animation_links import audit
from gfxlab.tools.original_model_probe import ZIP2_SHA, ptr, stage_originals

TRANSFORM = {"Transform", "RectTransform"}
ATTRIBUTES = {1: ("m_LocalPosition", "xyz"), 2: ("m_LocalRotation", "xyzw"),
              3: ("m_LocalScale", "xyz")}


def read_stream(words, count):
    # AssetStudio AnimationClip.cs reads float32 time, int32 key count,
    # then int32 curve index and four float32 coefficients per key.
    packed = b"".join(struct.pack("<I", word & 0xffffffff) for word in words)
    curves = [[] for _ in range(count)]
    offset = 0
    previous = -math.inf
    while offset < len(packed):
        time, size = struct.unpack_from("<fi", packed, offset)
        offset += 8
        if not 0 <= size <= count or offset + 20 * size > len(packed):
            raise ValueError("Invalid streamed animation frame size")
        if time < previous or math.isnan(time):
            raise ValueError("Streamed frame times out of order")
        previous = time
        seen = set()
        for _ in range(size):
            index, *coeff = struct.unpack_from("<i4f", packed, offset)
            offset += 20
            if (not 0 <= index < count or index in seen
                    or not all(math.isfinite(v) for v in coeff)):
                raise ValueError("Invalid streamed animation key")
            seen.add(index)
            if math.isfinite(time):
                curve = curves[index]
                if curve and curve[-1][0] >= time:
                    raise ValueError("Duplicate streamed animation key time")
                curve.append((time, coeff))
    if any(not curve for curve in curves):
        raise ValueError("Missing finite key for streamed curve")
    return curves


def value_at(curve, time):
    index = bisect_right(curve, time, key=lambda row: row[0]) - 1
    if index < 0:
        raise ValueError("Clip sample precedes first finite curve key")
    start, (a, b, c, d) = curve[index]
    dt = time - start if index + 1 < len(curve) else 0.0
    value = ((a * dt + b) * dt + c) * dt + d
    if not math.isfinite(value):
        raise ValueError("Nonfinite sampled curve")
    return value


def clip_channels(graph, clip, path_nodes):
    data = graph.data(clip)
    muscle = data["m_MuscleClip"]
    packed = muscle["m_Clip"]["data"]
    dense = packed["m_DenseClip"]
    if dense["m_CurveCount"] != 0 or dense["m_SampleArray"]:
        raise ValueError("This probe only supports original M02 streamed and constant curves")
    streamed = packed["m_StreamedClip"]
    curves = read_stream(streamed["data"], streamed["curveCount"])
    constants = packed["m_ConstantClip"]["data"]
    if not all(math.isfinite(v) for v in constants):
        raise ValueError("Nonfinite constant clip values")
    bindings = []
    seen = set()
    width = 0
    for binding in data["m_ClipBindingConstant"]["genericBindings"]:
        attribute = ATTRIBUTES.get(binding["attribute"])
        node = path_nodes.get(binding["path"] & 0xffffffff)
        if (binding["typeID"] != 4 or binding["customType"] != 0
                or binding["isPPtrCurve"] or attribute is None or node is None):
            raise ValueError("Unexpected M02 binding")
        field, axes = attribute
        if (node, field) in seen:
            raise ValueError("Duplicate M02 binding")
        seen.add((node, field))
        bindings.append((node, field, axes))
        width += len(axes)
    if width != len(curves) + len(constants) or len(seen) != len(path_nodes) * 3:
        raise ValueError("M02 clip binding coverage mismatch")
    start, stop = muscle["m_StartTime"], muscle["m_StopTime"]
    if not math.isfinite(start) or not math.isfinite(stop) or not 0 <= start < stop:
        raise ValueError("Invalid M02 clip interval")
    return curves, constants, bindings, start, stop


def snapshot(graph, bindings, values):
    overrides = {}
    cursor = 0
    for node, field, axes in bindings:
        local = overrides.setdefault(node, dict(graph.data(node)))
        vector = values[cursor:cursor + len(axes)]
        cursor += len(axes)
        if field == "m_LocalRotation":
            norm = math.sqrt(sum(v*v for v in vector))
            if not 0.9 < norm < 1.1:
                raise ValueError("Sampled M02 quaternion has unexpected magnitude")
            vector = [v / norm for v in vector]
        local[field] = dict(zip(axes, vector, strict=True))
    return overrides


def sample_m02(entry, graph, renderer, bones, animators):
    if len(bones) != 8 or len(animators) != 1:
        raise ValueError("M02 exact source rig selection changed")
    animator = animators[0]
    data = graph.data(animator)
    go = graph.target(data["m_GameObject"], animator[0], {"GameObject"})
    root, = graph.transforms[go]
    avatar = graph.target(data["m_Avatar"], animator[0], {"Avatar"})
    controller = graph.target(data["m_Controller"], animator[0], {"AnimatorController"})
    if avatar is None or controller is None or root in bones:
        raise ValueError("M02 controller, Avatar or root identity changed")
    tos = {}
    for value, path in graph.data(avatar)["m_TOS"]:
        tos.setdefault(value & 0xffffffff, set()).add(path)
    refs = graph.data(controller)["m_AnimationClips"]
    if len(refs) != 3:
        raise ValueError("M02 controller clip count changed")
    clips = [graph.target(ref, controller[0], {"AnimationClip"}) for ref in refs]
    if None in clips:
        raise ValueError("M02 source clip unresolved")
    bound_paths = [
        {b["path"] & 0xffffffff for b in graph.data(clip)["m_ClipBindingConstant"]["genericBindings"]}
        for clip in clips
    ]
    if any(paths != bound_paths[0] for paths in bound_paths) or len(bound_paths[0]) != 9:
        raise ValueError("M02 bound path sets changed across clips")
    relevant = set(bones)
    for bone in bones:
        for node in graph.ancestry(bone):
            relevant.add(node)
            if node == root:
                break
    path_nodes = {}
    for node in relevant:
        path = graph.relative_path(node, root)
        if path is None:
            raise ValueError("M02 bone outside Animator root")
        value = zlib.crc32(path.encode("utf-8"))
        if value not in bound_paths[0]:
            continue
        if value in path_nodes or (path and tos.get(value) != {path}):
            raise ValueError("M02 path hash fails exact Avatar verification")
        path_nodes[value] = node
    if path_nodes.keys() != bound_paths[0] or not set(bones) <= set(path_nodes.values()):
        raise ValueError("M02 bound paths must map to the original bone ancestry")
    mesh = graph.types[entry["owner"]][entry["mesh_pid"]]
    mesh_data = graph.data((entry["owner"], entry["mesh_pid"]))
    count = mesh_data["m_VertexData"]["m_VertexCount"]
    handler = direct_mesh_handler(mesh)
    positions = positions_from_parsed_mesh(handler, count)
    weights = decoded_handler_skin(handler, count, len(bones))
    bindposes = [source_matrix4(p) for p in mesh_data["m_BindPose"]]

    def parent(key, transform):
        ref = transform["m_Father"]
        if ptr(ref) == (0, 0):
            return None
        target = graph.target(ref, key[0], TRANSFORM)
        if target is None:
            raise ValueError("M02 source parent unresolved")
        return target

    cases = []
    for index, clip in enumerate(clips):
        curves, constants, bindings, start, stop = clip_channels(graph, clip, path_nodes)
        maximum = 0.0
        changed = 0
        baseline = None
        for step in range(5):
            time = start + (stop - start) * step / 4
            values = [value_at(curve, time) for curve in curves] + constants
            overrides = snapshot(graph, bindings, values)

            def lookup(key):
                return overrides[key] if key in overrides else graph.data(key)

            world = [source_world_matrix(key, lookup, parent) for key in bones]
            current = skin_positions_cpu(positions, weights, world, bindposes)
            if baseline is None:
                baseline = current
            else:
                delta = max(abs(a - b) for point, original in zip(current, baseline, strict=True)
                            for a, b in zip(point, original, strict=True))
                changed += delta > 1e-6
                maximum = max(maximum, delta)
        cases.append({"clip_index": index, "sampled_poses": 5,
                      "streamed_components": len(curves), "constant_components": len(constants),
                      "positions_compared_per_pose": count, "poses_changed_from_first": changed,
                      "max_position_component_change_from_first": maximum})
    return cases


def run(stage):
    cases = None

    def inspect(entry, graph, renderer, bones, animators):
        nonlocal cases
        if entry["id"] == "M02":
            cases = sample_m02(entry, graph, renderer, bones, animators)

    audit(stage, inspect)
    if cases is None:
        raise ValueError("M02 case not reached")
    return {"experiment": "GFX111", "source_sha": ZIP2_SHA, "cases": cases,
            "unity_runtime_pose_verified": False, "adreno_animated_pose_verified": False,
            "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2", "stage", "safe"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    report = run(stage_originals(args.zip2, args.stage))
    args.safe.write_text(json.dumps(report, indent=2) + "\n")
