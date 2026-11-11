"""Shared controlled Forward fixture values and source-preserving CB packing."""
import struct
import numpy as np


def engine_values(mesh, *, direct3d=False):
    vertices = np.frombuffer(mesh, dtype="<f4").reshape(-1, 12)
    if not len(vertices) or not np.isfinite(vertices).all():
        raise ValueError("Unexpected source vertex layout")
    minimum, maximum = vertices[:, :3].min(axis=0), vertices[:, :3].max(axis=0)
    center = (minimum + maximum) / 2
    span = float(max(maximum - minimum))
    if span <= 0:
        raise ValueError("Source mesh has no spatial extent")
    scale = 1.6 / span
    projection = np.eye(4, dtype=np.float32)
    projection[0, 0] = projection[1, 1] = scale
    projection[2, 2] = -scale
    projection[:3, 3] = -projection.diagonal()[:3] * center
    if direct3d:
        # D3D clips z to [0,w]; preserve the GLES window depth after projection.
        projection[2, :] = 0.5 * (projection[2, :] + projection[3, :])
    identity = tuple(np.eye(4).flatten())
    camera = (float(center[0]), float(center[1]), float(center[2]) + 3 * span)
    direction = np.array([0.3, 0.6, 1.0])
    direction /= np.linalg.norm(direction)
    engine = {
        "_WorldSpaceCameraPos": camera,
        "unity_MatrixVP": tuple(projection.T.flatten()),
        "unity_ObjectToWorld": identity,
        "unity_WorldToObject": identity,
        "unity_WorldTransformParams": (0, 0, 0, 1),
        "_LightColor0": (0.85, 0.85, 0.85, 1),
        "_WorldSpaceLightPos0": (*direction, 0),
        "unity_OcclusionMaskSelector": (1, 0, 0, 0),
        "unity_SpecCube0_BoxMin": (0, 0, 0, 1),
        "unity_SpecCube1_BoxMin": (0, 0, 0, 1),
        "unity_SpecCube0_BoxMax": (0, 0, 0, 0),
        "unity_SpecCube1_BoxMax": (0, 0, 0, 0),
        "unity_SpecCube0_ProbePosition": (0, 0, 0, 0),
        "unity_SpecCube1_ProbePosition": (0, 0, 0, 0),
        "unity_SpecCube0_HDR": (1, 1, 0, 0),
        "unity_SpecCube1_HDR": (1, 1, 0, 0),
        "unity_ProbeVolumeParams": (0, 0, 0, 0),
        "unity_ProbeVolumeSizeInv": (1, 1, 1),
        "unity_ProbeVolumeMin": (0, 0, 0),
        "unity_ProbeVolumeWorldToObject": identity,
    }
    return engine

def pack_buffer(source, mask, group, engine, light_on):
    if len(source) != len(mask):
        raise ValueError("Material payload/mask size disagreement")
    data = bytearray(source)
    covered = bytearray(mask)
    for field in group["parameters"].values():
        start = field["index"]
        width = field["rows"] * field["columns"]
        end = start + width * 4
        if not 0 <= start < end <= len(data):
            raise ValueError("Named runtime value exceeds actual shader buffer")
        if all(covered[start:end]):
            continue
        values = engine[field["name"]]
        if field["name"] == "_LightColor0" and not light_on:
            values = (0,0,0,1)
        if len(values) != width or any(covered[start:end]):
            raise ValueError("Unproven runtime binding shape")
        data[start:end] = struct.pack(f"<{width}f", *values)
        covered[start:end] = bytes([1]) * (end-start)
    return data, covered
