"""Render private original Forward fixtures with Mesa GLES.

Use EGL_PLATFORM=surfaceless and LIBGL_ALWAYS_SOFTWARE=1. The numbered
constants below are the GLES/EGL API enums. Captures are private source
images; publish only the safe summary.
"""
import ctypes as c
import hashlib
import json
import re
import struct
import shutil

import numpy as np
from pathlib import Path
from PIL import Image
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--private", type=Path, required=True)
parser.add_argument("--textures", type=Path, required=True)
parser.add_argument("--safe", type=Path, required=True)
parser.add_argument("--portable", type=Path)
parser.add_argument("--second-slot", type=Path)
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
def link_program():
    program = gl('CreateProgram', U)()
    for name, kind in [('probe.vert', 35633), ('probe.frag', 35632)]:
        stage = shader(name, kind)
        call('AttachShader', program, stage)
        call('DeleteShader', stage)
    call('LinkProgram', program)
    status = I()
    gl('GetProgramiv', None, U, U, P)(program, 35714, c.byref(status))
    if not status.value:
        raise ValueError("Mesa could not link the selected Forward pair")
    call('UseProgram', program)
    return program


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
from gfxlab.tools.gfx121_forward_fixture_values import engine_values, pack_buffer

portable_buffers = {}


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
            size = int(vectors) * 16
            if len(source) != size or size != contract["sizes"][str(slot)] * 16:
                raise ValueError("Constant buffer size changed")
            data, covered = pack_buffer(source,mask,groups[slots[slot]],engine,light_on)
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
            portable_buffers.setdefault(light_on, {})[name] = bytes(data)
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
    layout = texture_layout.get(role, {"width": 1024, "height": 1024, "levels": 11,
                                       "source_color_space": 0 if role == "normal" else 1})
    internal = {0: 0x8058, 1: 0x8c43}[layout["source_color_space"]]
    call("TexParameteri",target,0x813d,layout["levels"] - 1 if role and constant is None else 0)
    upload2d = gl("TexImage2D",None,U,I,I,I,I,I,U,U,P)
    if constant is not None:
        upload2d(target,0,internal,1,1,0,0x1908,0x1401,bytes(constant))
    elif role:
        raw = (texture_path/(role+".rgba")).read_bytes()
        offset = 0
        for mip in range(layout["levels"]):
            width = max(1, layout["width"] >> mip)
            height = max(1, layout["height"] >> mip)
            size = width * height * 4
            upload2d(target,mip,internal,
                     width,height,0,0x1908,0x1401,raw[offset:offset+size])
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
    return [(kind,name,roles.get(bindings[int(slot)]["name"])) for kind,name,slot,_ in samplers]


def select_slot(folder, textures):
    global root, texture_path, texture_layout, p, engine, contracts, indices
    root, texture_path = folder, textures
    layout_path = textures / "textures.json"
    texture_layout = json.loads(layout_path.read_text()) if layout_path.exists() else {}
    mesh = (root / "mesh.bin").read_bytes()
    engine = engine_values(mesh)
    contracts = {stage: json.loads((root / (stage + ".json")).read_text())
                 for stage in ("vertex", "fragment")}
    p = link_program()
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
    check("geometry setup")
    return bind_samplers()


sampler_bindings = select_slot(args.private, args.textures)
bound_samplers = len(sampler_bindings)
check("resource setup")


def draw(light_on, *, clear=True):
    blocks, material_bytes = bind_constant_buffers(light_on)
    call("Enable",0x0b71)
    gl("ClearColor",None,F,F,F,F)(0,0,0,0)
    if clear:
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
if args.portable:
    args.portable.mkdir(mode=0o700, parents=True, exist_ok=False)
    for name in ("probe.vert", "probe.frag", "mesh.bin", "indices.bin"):
        shutil.copyfile(root/name, args.portable/name)
    for role in ("basecolor", "normal", "metallic"):
        shutil.copyfile(args.textures/(role+".rgba"),args.portable/(role+".rgba"))
    block_rows = []
    for index,(name,data) in enumerate(portable_buffers[True].items()):
        lit_name, unlit_name = f"light-{index}.bin", f"dark-{index}.bin"
        (args.portable/lit_name).write_bytes(data)
        (args.portable/unlit_name).write_bytes(portable_buffers[False][name])
        block_rows.append(dict(name=name,light=lit_name,dark=unlit_name,bytes=len(data)))
    scene = dict(blocks=block_rows,
                 samplers=[dict(kind=kind, name=name, role=role or "") for kind,name,role in sampler_bindings])
    if texture_layout:
        scene["textures"] = {role: {key: row[key] for key in ("width", "height", "levels", "source_color_space")}
                             for role, row in texture_layout.items()}
    (args.portable/"scene.json").write_text(json.dumps(scene))
    for name, pixels in (("light",lit),("dark",unlit),("flat",flat),("nonmetal",nonmetal)):
        (args.portable/(name+".rgba")).write_bytes(pixels.tobytes())
if args.second_slot:
    if (args.private / "mesh.bin").read_bytes() != (args.second_slot / "mesh.bin").read_bytes():
        raise ValueError("Material slots must refer to the same source mesh")
    select_slot(args.second_slot, args.second_slot)
    second, _, _ = draw(True)
    select_slot(args.private, args.textures)
    draw(True)
    select_slot(args.second_slot, args.second_slot)
    combined, _, _ = draw(True, clear=False)
    first_mask, second_mask, both = (image[:, :, 3] != 0 for image in (lit, second, combined))
    if not np.array_equal(both, first_mask | second_mask):
        raise ValueError("Combined coverage disagrees with the two source slots")
    contributions = []
    for source, source_mask, other_mask in ((lit, first_mask, second_mask),
                                            (second, second_mask, first_mask)):
        exclusive = source_mask & ~other_mask
        if not exclusive.any() or not np.array_equal(source[exclusive], combined[exclusive]):
            raise ValueError("A source material slot did not survive composition")
        contributions.append(int(exclusive.sum()))
    if not np.all(np.all(combined == lit, axis=2) | np.all(combined == second, axis=2)):
        raise ValueError("Unexpected pixels in the combined opaque material draw")
    report["two_slots_shared_depth_draw"] = {
        "second_slot_triangles": len(indices)//6,
        "second_slot_coverage": int(second_mask.sum()),
        "combined_coverage": int(both.sum()),
        "overlap_pixels": int((first_mask & second_mask).sum()),
        "exclusive_pixels_by_slot": contributions,
        "rgba_sha256": hashlib.sha256(combined.tobytes()).hexdigest(),
    }
    Image.fromarray(combined[::-1]).save(args.private / "combined.png")
    if args.portable:
        (args.portable / "combined.rgba").write_bytes(combined.tobytes())

args.safe.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
