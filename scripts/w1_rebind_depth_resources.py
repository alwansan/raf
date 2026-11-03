"""Restore original shader texture/sampler names and vertex-input semantics.

Only supports explicit translator register names and original serialized metadata;
never guesses a resource from descriptor order or a vertex attribute from position.
All input/output HLSL remains private to the caller.
"""
import re
import struct

IDENT = re.compile(r'[A-Za-z_]\w*\Z')
RESOURCE = re.compile(r'\b(Texture\w*(?:\s*<[^;{}>]+>)?|SamplerState|SamplerComparisonState)\s+([A-Za-z_]\w*)\s*:\s*register\(\s*([ts])(\d+)\s*\)\s*;')


def signature_inputs(dxbc):
    """Read original SM4/5 ISGN register -> authored semantic mapping."""
    if dxbc[:4] != b'DXBC' or len(dxbc) < 36:
        raise ValueError('Invalid original graphics container')
    count = struct.unpack_from('<I', dxbc, 28)[0]
    if count > 128 or 32 + count * 4 > len(dxbc):
        raise ValueError('Invalid original signature chunk table')
    matches = []
    for i in range(count):
        start = struct.unpack_from('<I', dxbc, 32 + i * 4)[0]
        if start + 8 > len(dxbc):
            raise ValueError('Truncated original signature chunk')
        size = struct.unpack_from('<I', dxbc, start + 4)[0]
        if start + 8 + size > len(dxbc):
            raise ValueError('Truncated original signature payload')
        if dxbc[start:start + 4] == b'ISGN':
            matches.append(dxbc[start + 8:start + 8 + size])
    if len(matches) != 1:
        raise ValueError('Exactly one original ISGN signature required')
    data = matches[0]
    if len(data) < 8:
        raise ValueError('Truncated signature header')
    n = struct.unpack_from('<I', data)[0]
    if n > 32 or 8 + n * 24 > len(data):
        raise ValueError('Invalid original input signature count')
    result = {}
    for i in range(n):
        offset, index, system, component, register = struct.unpack_from('<5I', data, 8 + i * 24)
        end = data.find(b'\0', offset)
        if offset < 8 + n * 24 or end < offset or end - offset > 64:
            raise ValueError('Invalid original semantic string')
        name = data[offset:end].decode('ascii')
        if not IDENT.fullmatch(name) or index > 31 or register in result:
            raise ValueError('Ambiguous original vertex semantic')
        result[register] = name + str(index)
    return result


def rebind(source, program, name_indices, *, original_inputs=None):
    common = program.get('m_CommonParameters', {})
    unsupported = ('m_BufferParams', 'm_ConstantBufferBindings', 'm_ConstantBuffers',
                   'm_MatrixParams', 'm_UAVParams', 'm_VectorParams', 'm_Samplers')
    if any(common.get(key) for key in unsupported):
        raise ValueError('Depth resource rebinder does not support non-texture metadata')
    names = {}
    for name, index in name_indices:
        if type(index) is not int or not isinstance(name, str) or index in names:
            raise ValueError('Invalid original property-name table')
        names[index] = name
    textures, samplers = {}, {}
    for row in common.get('m_TextureParams', []):
        index, name_index, sampler_index = row.get('m_Index'), row.get('m_NameIndex'), row.get('m_SamplerIndex')
        if type(index) is not int or index < 0 or name_index not in names or index in textures:
            raise ValueError('Invalid original texture-register metadata')
        name = names[name_index]
        if not IDENT.fullmatch(name):
            raise ValueError('Original texture property is not an HLSL identifier')
        textures[index] = name
        if type(sampler_index) is int and 0 <= sampler_index < 65535:
            if sampler_index in samplers and samplers[sampler_index] != 'sampler' + name:
                raise ValueError('Shared original sampler needs explicit binding recovery')
            samplers[sampler_index] = 'sampler' + name
    mapping, used = {}, {'t': set(), 's': set()}
    for match in RESOURCE.finditer(source):
        kind, variable, register_class = match[1], match[2], match[3]
        # vkd3d records original DXBC registers in its symbolic names, whereas
        # SPIRV-Cross HLSL register numbers may be renumbered descriptor bindings.
        original = re.search(r'(?:^|_)' + register_class + r'([0-9]+)$', variable)
        if original is None:
            raise ValueError('Translator original-register symbol unavailable')
        index = int(original[1])
        table = textures if register_class == 't' else samplers
        if index not in table or index in used[register_class]:
            raise ValueError('Original resource-register mapping is missing or duplicated')
        mapping[variable] = table[index]
        used[register_class].add(index)
    if used['t'] != set(textures) or used['s'] != set(samplers):
        raise ValueError('Serialized texture/sampler metadata not fully resolved')
    if mapping:
        token = re.compile(r'\b(?:' + '|'.join(re.escape(k) for k in mapping) + r')\b')
        source = token.sub(lambda m: mapping[m[0]], source)
    semantics = 0
    if original_inputs is not None:
        input_struct = re.search(r'\bstruct\s+SPIRV_Cross_Input\s*\{([^{}]*)\}', source)
        if input_struct is None:
            raise ValueError('Translator vertex input struct unavailable')
        seen = set()
        def replace(match):
            index = int(match[1])
            if index not in original_inputs or index in seen:
                raise ValueError('Original vertex input register unresolved')
            seen.add(index)
            return ': ' + original_inputs[index]
        body = re.sub(r':\s*TEXCOORD([0-9]+)\b', replace, input_struct[1])
        if seen != set(original_inputs):
            raise ValueError('Original vertex signature not fully restored')
        source = source[:input_struct.start(1)] + body + source[input_struct.end(1):]
        semantics = len(seen)
    return source, {'textures_rebound': len(used['t']), 'samplers_rebound': len(used['s']),
                    'vertex_semantics_restored': semantics, 'binding_names_disclosed': False}
