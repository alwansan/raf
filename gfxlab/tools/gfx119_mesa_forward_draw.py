"""Render the private GFX117 texture views with Mesa GLES.

Use EGL_PLATFORM=surfaceless and LIBGL_ALWAYS_SOFTWARE=1. The numbered
constants below are the GLES/EGL API enums. Captures are private source
images; publish only the safe summary.
"""
import ctypes as c
import hashlib
import json
import re
import struct

import numpy as np
from pathlib import Path
from PIL import Image
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--private", type=Path, required=True)
parser.add_argument("--textures", type=Path, required=True)
parser.add_argument("--safe", type=Path, required=True)
args = parser.parse_args()
root = args.private
E = c.CDLL('libEGL.so.1')
P = c.c_void_p
I = c.c_int
U = c.c_uint
F = c.c_float
Z = c.c_ssize_t
S = c.c_char_p
B = c.c_ubyte

def egl(name, ret, *args):
    f = getattr(E, name)
    f.restype = ret
    f.argtypes = args
    return f
proc = egl('eglGetProcAddress', P, S)

def gl(name, ret, *args):
    address = proc(('gl' + name).encode())
    assert address, name
    return c.CFUNCTYPE(ret, *args)(address)

def call(name, *args):
    return gl(name, None, *[U] * len(args))(*args)
d = egl('eglGetDisplay', P, P)(None)
assert egl('eglInitialize', U, P, P, P)(d, None, None)
assert egl('eglBindAPI', U, U)(12448)
cfg = P()
count = I()
assert egl('eglChooseConfig', U, P, P, P, I, P)(d, (I * 7)(12339, 1, 12352, 64, 12324, 8, 12344), c.byref(cfg), 1, c.byref(count)) and count.value
ctx = egl('eglCreateContext', P, P, P, P, P)(d, cfg, None, (I * 3)(12440, 3, 12344))
surf = egl('eglCreatePbufferSurface', P, P, P, P)(d, cfg, (I * 5)(12375, 8, 12374, 8, 12344))
assert egl('eglMakeCurrent', U, P, P, P, P)(d, surf, surf, ctx)
renderer = gl('GetString', S, U)(7937).decode()
def shader(name, kind):
    src = (root / name).read_bytes()
    sh = gl('CreateShader', U, U)(kind)
    gl('ShaderSource', None, U, I, P, P)(sh, 1, (S * 1)(src), None)
    call('CompileShader', sh)
    status = I()
    gl('GetShaderiv', None, U, U, P)(sh, 35713, c.byref(status))
    if not status.value:
        log = c.create_string_buffer(4096)
        gl('GetShaderInfoLog', None, U, I, P, P)(sh, 4096, None, log)
        raise RuntimeError(log.value)
    return sh
p = gl('CreateProgram', U)()
for name, kind in [('probe.vert', 35633), ('probe.frag', 35632)]:
    call('AttachShader', p, shader(name, kind))
call('LinkProgram', p)
status = I()
gl('GetProgramiv', None, U, U, P)(p, 35714, c.byref(status))
assert status.value
call('UseProgram', p)
def gen(name):
    out = U()
    gl('Gen' + name, None, I, P)(1, c.byref(out))
    return out.value
fbo = gen('Framebuffers')
color = gen('Textures')
depth = gen('Renderbuffers')
call('BindTexture', 3553, color)
call('TexStorage2D', 3553, 1, 32856, 256, 256)
call('BindFramebuffer', 36160, fbo)
call('FramebufferTexture2D', 36160, 36064, 3553, color, 0)
call('BindRenderbuffer', 36161, depth)
call('RenderbufferStorage', 36161, 33190, 256, 256)
call('FramebufferRenderbuffer', 36160, 36096, 36161, depth)
assert gl('CheckFramebufferStatus', U, U)(36160) == 36053
call('Viewport', 0, 0, 256, 256)
for flag in [3024, 3042, 2884]:
    call('Disable', flag)
call('DepthFunc', 513)
gl('DepthMask', None, B)(1)
gl('ClearDepthf', None, F)(1)
def buffer(target, data):
    identifier = gen("Buffers")
    call("BindBuffer", target, identifier)
    gl("BufferData", None, U, Z, P, U)(target, len(data), data, 35044)
    return identifier


def check(stage):
    error = gl("GetError", U)()
    if error:
        raise RuntimeError(f"{stage}: GL error 0x{error:04x}")

# The fixture renders source bind geometry with an identity object transform.
# Camera, directional light, disabled probe volume and black reflection cubes
# are explicitly authored test inputs. They are not a capture of Unity's scene.
mesh = (root / "mesh.bin").read_bytes()
vertices = np.frombuffer(mesh, dtype="<f4").reshape(-1, 12)
if vertices.shape != (1666, 12) or not np.isfinite(vertices).all():
    raise ValueError("Unexpected M02 source vertex layout")
minimum, maximum = vertices[:, :3].min(axis=0), vertices[:, :3].max(axis=0)
center = (minimum + maximum) / 2
span = float(max(maximum - minimum))
scale = 1.6 / span
projection = np.eye(4, dtype=np.float32)
projection[0, 0] = projection[1, 1] = scale
projection[2, 2] = -scale
projection[:3, 3] = -projection.diagonal()[:3] * center
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
contracts = {stage: json.loads((root / (stage + ".json")).read_text())
             for stage in ("vertex", "fragment")}


def bind_constant_buffers(light_on):
    count = source_bytes = 0
    for stage, extension in (("vertex", "vert"), ("fragment", "frag")):
        contract = contracts[stage]
        stage_source = (root / ("probe." + extension)).read_text()
        blocks = re.findall(r"layout\(binding = (\d+), std140\) uniform (\w+)"
                            r"\s*\{\s*(?:highp )?vec4 _m0\[(\d+)\];\s*\}\s*(\w+);", stage_source)
        groups = {g["name"]: g for g in contract["groups"]}
        slots = {b["index"]: b["name"] for b in contract["bindings"] if b["type"] == 1}
        if {int(slot) for slot, _, _, _ in blocks} != set(slots):
            raise ValueError("GLSL constant buffer declarations changed")
        for slot, name, vectors, instance in blocks:
            slot = int(slot)
            source = (root / f"{stage}-{slot}.bin").read_bytes()
            mask = (root / f"{stage}-{slot}.mask").read_bytes()
            data = bytearray(source)
            covered = bytearray(mask)
            size = int(vectors) * 16
            if len(data) != size or size != contract["sizes"][str(slot)] * 16:
                raise ValueError("Constant buffer size changed")
            for field in groups[slots[slot]]["parameters"].values():
                start = field["index"]
                width = field["rows"] * field["columns"]
                end = start + width * 4
                if end > size:
                    raise ValueError("Named runtime value exceeds actual shader buffer")
                if all(covered[start:end]):
                    continue
                values = engine[field["name"]]
                if field["name"] == "_LightColor0" and not light_on:
                    values = (0, 0, 0, 1)
                if len(values) != width or any(covered[start:end]):
                    raise ValueError("Unproven runtime binding shape")
                data[start:end] = struct.pack(f"<{width}f", *values)
                covered[start:end] = bytes([1]) * (end - start)
            active = re.findall(r"\b" + re.escape(instance) + r"\._m0\[([^\]]+)\]", stage_source)
            for vector in active:
                if not re.fullmatch(r"\d+u?", vector):
                    raise ValueError("Unexpected dynamic uniform access")
                start = int(vector.rstrip("u")) * 16
                if not any(covered[start:start + 16]):
                    raise ValueError("Uniform vector lacks semantic input")
            if any(mask[i] and data[i] != source[i] for i in range(size)):
                raise ValueError("Original material payload overwritten")
            index = gl("GetUniformBlockIndex", U, U, S)(p, name.encode())
            if index == 0xffffffff:
                raise ValueError("Driver discarded an expected uniform block")
            driver_size = I()
            gl("GetActiveUniformBlockiv", None, U, U, U, P)(p,index,0x8a40,c.byref(driver_size))
            if driver_size.value != size:
                raise ValueError("Driver uniform block size differs from original")
            call("UniformBlockBinding",p,index,count)
            call("BindBufferBase",0x8a11,count,buffer(0x8a11,bytes(data)))
            source_bytes += sum(mask)
            count += 1
    return count, source_bytes


def upload_texture(unit, kind, role, constant=None):
    target = {"sampler2D":0x0de1,"sampler3D":0x806f,"samplerCube":0x8513}[kind]
    call("ActiveTexture",0x84c0 + unit)
    call("BindTexture",target,gen("Textures"))
    for key in (0x2802,0x2803):
        call("TexParameteri",target,key,0x2901 if role else 0x812f)
    call("TexParameteri",target,0x2800,0x2601)
    call("TexParameteri",target,0x2801,0x2701 if role else 0x2601)
    call("TexParameteri",target,0x813d,10 if role and constant is None else 0)
    upload2d = gl("TexImage2D",None,U,I,I,I,I,I,U,U,P)
    if constant is not None:
        upload2d(target,0,0x8058 if role=="normal" else 0x8c43,1,1,0,0x1908,0x1401,bytes(constant))
    elif role:
        raw = (args.textures/(role+".rgba")).read_bytes()
        offset = 0
        for mip in range(11):
            width = 1024 >> mip
            size = width*width*4
            upload2d(target,mip,0x8058 if role=="normal" else 0x8c43,
                     width,width,0,0x1908,0x1401,raw[offset:offset+size])
            offset += size
        if offset != len(raw):
            raise ValueError("Unexpected source texture mip chain")
    elif kind == "sampler2D":
        upload2d(target,0,0x8058,1,1,0,0x1908,0x1401,bytes([255]*4))
    elif kind == "samplerCube":
        for face in range(6):
            upload2d(0x8515+face,0,0x8058,1,1,0,0x1908,0x1401,b"\0\0\0\xff")
    else:
        gl("TexImage3D",None,U,I,I,I,I,I,I,U,U,P)(
            target,0,0x8058,1,1,1,0,0x1908,0x1401,b"\0\0\0\xff")


def bind_samplers(replacements=None):
    replacements = replacements or {}
    shader = (root/"probe.frag").read_text()
    samplers = re.findall(r"uniform highp (sampler\w+) (\w+Combinedt(\d+)s(\d+));",shader)
    bindings = {b["index"]:b for b in contracts["fragment"]["bindings"] if b["type"] == 0}
    roles = {"_MainTex":"basecolor","_BumpMap":"normal","_MetallicGlossMap":"metallic"}
    defaults = {"_OcclusionMap","unity_SpecCube0","unity_SpecCube1","unity_ProbeVolumeSH"}
    if {int(slot) for _,_,slot,_ in samplers} != set(bindings) or len(samplers) != 7:
        raise ValueError("Exact source texture slot contract changed")
    for unit,(kind,name,slot,sampler) in enumerate(samplers):
        binding = bindings[int(slot)]
        if binding["extra"] >= 0 and binding["extra"] != int(sampler):
            raise ValueError("Combined sampler conflicts with source")
        if binding["name"] not in roles.keys() | defaults:
            raise ValueError("Texture lacks source or explicit fixture input")
        role = roles.get(binding["name"])
        upload_texture(unit,kind,role,replacements.get(role))
        location = gl("GetUniformLocation",I,U,S)(p,name.encode())
        if location < 0:
            raise ValueError("Translated sampler missing from driver program")
        gl("Uniform1i",None,I,I)(location,unit)
    return len(samplers)


call("BindVertexArray",gen("VertexArrays"))
buffer(0x8892,mesh)
attributes = {("POSITION",0):(3,0),("NORMAL",0):(3,12),
              ("TEXCOORD",0):(2,40),("TANGENT",0):(4,24)}
for semantic,semantic_index,system,_,register,mask,_ in contracts["vertex"]["inputs"]:
    key = semantic,semantic_index
    if system:
        raise ValueError("Unexpected source system vertex attribute")
    if key == ("TEXCOORD",1):
        # This mesh has no UV1. Its original _UVSec selects UV0.
        gl("VertexAttrib2f",None,U,F,F)(register,0,0)
        continue
    components, offset = attributes[key]
    if mask.bit_count() != components and key != ("POSITION",0):
        raise ValueError("Source vertex signature and attributes disagree")
    gl("VertexAttribPointer",None,U,I,U,B,I,P)(register,components,0x1406,0,48,offset)
    call("EnableVertexAttribArray",register)
indices = (root/"indices.bin").read_bytes()
buffer(0x8893,indices)
bound_samplers = bind_samplers()
check("resource setup")


def draw(light_on):
    blocks, material_bytes = bind_constant_buffers(light_on)
    call("Enable",0x0b71)
    gl("ClearColor",None,F,F,F,F)(0,0,0,0)
    call("Clear",0x4100)
    gl("DrawElements",None,U,I,U,P)(4,len(indices)//2,0x1403,None)
    pixels = c.create_string_buffer(256*256*4)
    gl("ReadPixels",None,I,I,I,I,U,U,P)(0,0,256,256,0x1908,0x1401,pixels)
    check("indexed Forward draw")
    return np.frombuffer(pixels.raw,dtype=np.uint8).reshape(256,256,4),blocks,material_bytes


lit, blocks, material_bytes = draw(True)
unlit, _, _ = draw(False)
bind_samplers({"normal": (255, 128, 255, 128)})
flat, _, _ = draw(True)
bind_samplers({"metallic": (0, 0, 0, 255)})
nonmetal, _, _ = draw(True)
bind_samplers()
repeated, _, _ = draw(True)
if not np.array_equal(lit,repeated):
    raise ValueError("Restoring source bindings changed the baseline")
normal_changed = int(np.count_nonzero(np.any(lit[:,:,:3] != flat[:,:,:3],axis=2)))
metallic_changed = int(np.count_nonzero(np.any(lit[:,:,:3] != nonmetal[:,:,:3],axis=2)))
if min(normal_changed,metallic_changed) < 100:
    raise ValueError("Source normal or metallic control did not affect the draw")
alpha = lit[:,:,3] != 0
coverage = int(alpha.sum())
changed = int(np.count_nonzero(np.any(lit[:,:,:3] != unlit[:,:,:3],axis=2)))
if not np.array_equal(lit[:,:,3],unlit[:,:,3]) or coverage < 100 or changed < 100:
    raise ValueError("Directional light control did not produce a credible source draw")
Image.fromarray(lit[::-1]).save(root/"lit.png")
report = dict(experiment="GFX119", renderer=renderer, triangles=len(indices)//6,
              covered_pixels=coverage, directional_light_changed_pixels=changed,
              normal_control_changed_pixels=normal_changed, metallic_control_changed_pixels=metallic_changed,
              baseline_repeat_exact=True,
              dark_control_nonblack_pixels=int(np.any(unlit[:,:,:3]!=0,axis=2).sum()),
              driver_verified_cb_blocks=blocks, original_material_bytes_preserved=material_bytes,
              bound_combined_samplers=bound_samplers, rgba_sha256=hashlib.sha256(lit.tobytes()).hexdigest(),
              controlled_fixture=True, original_translated_forward_draw_completed=True,
              original_game_pixel_parity=False, android_device_verified=False, phase_closed=False)
args.safe.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
