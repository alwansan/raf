"""Render the private GFX117 texture views with Mesa GLES.

Use EGL_PLATFORM=surfaceless and LIBGL_ALWAYS_SOFTWARE=1. The numbered
constants below are the GLES/EGL API enums. Captures are private source
images; publish only the safe summary.
"""
import ast
import ctypes as c
import hashlib
import io
import json
import re
import struct
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--assets', type=Path, required=True)
parser.add_argument('--captures', type=Path, required=True)
parser.add_argument('--safe', type=Path, required=True)
parser.add_argument('--shader-java', type=Path, default=Path('gfxlab/android-gles-skin109/src/com/alwansan/gfx109/MainActivity.java'))
args = parser.parse_args()
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
java = args.shader_java.read_text()

def shader(name, kind):
    body = java.split('String ' + name + ' = ', 1)[1].split(';\n\n', 1)[0] if name == 'FRAGMENT' else java.split('String VERTEX = ', 1)[1].split('    private static final String FRAGMENT')[0]
    src = ''.join((ast.literal_eval(q) for q in re.findall('"(?:[^"\\\\]|\\\\.)*"', body))).encode()
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
for name, kind in [('VERTEX', 35633), ('FRAGMENT', 35632)]:
    call('AttachShader', p, shader(name, kind))
gl('TransformFeedbackVaryings', None, U, I, P, U)(p, 1, (S * 1)(b'skinned'), 35980)
call('LinkProgram', p)
status = I()
gl('GetProgramiv', None, U, U, P)(p, 35714, c.byref(status))
assert status.value
call('UseProgram', p)
block = gl('GetUniformBlockIndex', U, U, S)(p, b'Palette')
call('UniformBlockBinding', p, block, 0)

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
root = args.assets
mesh = (root / 'raster115.bin').read_bytes()
cam = (F * 16)(*struct.unpack_from('<16f', mesh))

def uniform(name):
    return gl('GetUniformLocation', I, U, S)(p, name)
gl('UniformMatrix4fv', None, I, I, B, P)(uniform(b'uCamera'), 1, 0, cam)
gl('Uniform1i', None, I, I)(uniform(b'uRaster'), 1)

def buffer(target, data):
    bid = gen('Buffers')
    call('BindBuffer', target, bid)
    gl('BufferData', None, U, Z, P, U)(target, len(data), data, 35044)
    return bid

def capture(depth_test):
    call('Enable' if depth_test else 'Disable', 2929)
    gl('ClearColor', None, F, F, F, F)(0, 0, 0, 0)
    call('Clear', 16640)
    gl('DrawElements', None, U, I, U, P)(4, (len(mesh) - 64) // 2, 5123, None)
    out = c.create_string_buffer(256 * 256 * 4)
    gl('ReadPixels', None, I, I, I, I, U, U, P)(0, 0, 256, 256, 6408, 5121, out)
    assert gl('GetError', U)() == 0
    return Image.frombytes('RGBA', (256, 256), out.raw).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
source_uv = (root / 'uv117.bin').read_bytes()
transforms = struct.unpack_from('<12f', source_uv)
poses = ['C0P0', 'C1P0', 'C1P2', 'C2P0', 'C2P2']
roles = ['basecolor', 'normal', 'metallic']
captures = {}
with ZipFile(args.captures, 'x') as archive:
    for pose in poses:
        data = (root / (pose + '.bin')).read_bytes()
        _, n, b = struct.unpack_from('<4sII', data)
        start = 12 + b * 64
        call('BindVertexArray', gen('VertexArrays'))
        call('BindBufferBase', 35345, 0, buffer(35345, data[12:start].ljust(6400, b'\x00')))
        buffer(34962, data[start:])
        buffer(34963, mesh[64:])
        for i, cnt, offset in [(0, 3, 0), (1, 4, 12)]:
            gl('VertexAttribPointer', None, U, I, U, B, I, P)(i, cnt, 5126, 0, 56, offset)
        gl('VertexAttribIPointer', None, U, I, U, I, P)(2, 4, 5125, 56, 28)
        buffer(34962, source_uv[48:])
        gl('VertexAttribPointer', None, U, I, U, B, I, P)(3, 2, 5126, 0, 8, 0)
        for i in range(4):
            call('EnableVertexAttribArray', i)
        for i, role in enumerate(roles):
            call('BindTexture', 3553, gen('Textures'))
            for pname, value in [(10241, 9985), (10240, 9729), (10242, 10497), (10243, 10497), (33085, 10)]:
                call('TexParameteri', 3553, pname, value)
            raw = (root / (role + '.rgba')).read_bytes()
            offset = 0
            for level in range(11):
                w = 1024 >> level
                length = w * w * 4
                gl('TexImage2D', None, U, I, I, I, I, I, U, U, P)(3553, level, 32856 if i == 1 else 35907, w, w, 0, 6408, 5121, raw[offset:offset + length])
                offset += length
            assert offset == len(raw)
            gl('Uniform1i', None, I, I)(uniform(b'uRole'), i + 1)
            gl('Uniform4f', None, I, F, F, F, F)(uniform(b'uST'), *transforms[i * 4:i * 4 + 4])
            for lod in [0, 4]:
                gl('Uniform1f', None, I, F)(uniform(b'uMip'), lod)
                image = capture(True)
                encoded = io.BytesIO()
                image.save(encoded, format='PNG')
                pixels = image.tobytes()
                alpha = pixels[3::4]
                assert set(alpha) == {0, 255}
                name = f'{pose}-{role}-L{lod}.png'
                archive.writestr(name, encoded.getvalue())
                covered = alpha.count(255)
                colors = len({pixels[k:k + 3] for k in range(0, len(pixels), 4) if pixels[k + 3]})
                assert covered > 100 and colors > 20, (name, covered, colors)
                captures[name] = {'rgba_sha256': hashlib.sha256(pixels).hexdigest(), 'covered_pixels': covered, 'unique_covered_rgb': colors}
assert len(captures) == 30
for pose in poses:
    matches = [v['covered_pixels'] for name, v in captures.items() if name.startswith(pose + '-')]
    assert len(set(matches)) == 1
    for role in roles:
        assert captures[f'{pose}-{role}-L0.png']['rgba_sha256'] != captures[f'{pose}-{role}-L4.png']['rgba_sha256']
args.safe.write_text(json.dumps({'experiment': 'GFX117', 'renderer': renderer, 'captures': captures, 'phase_closed': False}, indent=2) + '\n')
print(renderer, len(captures), min((v['covered_pixels'] for v in captures.values())), max((v['covered_pixels'] for v in captures.values())))
