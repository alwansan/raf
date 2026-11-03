"""Bounded original Depth Copy parameter decode and private ShaderLab reconstruction.

Original inputs stay private. Only the authenticated no-override parameter layout
and zero-property Depth Copy shader are supported; unsupported state fails closed.
Binary format provenance: nowl-it/AssetRipperCLI 036098ab, ShaderSubProgram.cs.
"""
import math
import re
import struct


def decode_empty_parameters(data):
    position = 0
    def integer():
        nonlocal position
        if position + 4 > len(data):
            raise ValueError('Truncated original shader parameter record')
        value = struct.unpack_from('<i', data, position)[0]
        position += 4
        return value
    def string():
        nonlocal position
        length = integer()
        if not 0 <= length <= 1024 or position + length > len(data):
            raise ValueError('Invalid original parameter-group string')
        value = data[position:position + length].decode('utf-8')
        position += length
        aligned = (position + 3) & ~3
        if aligned > len(data) or any(data[position:aligned]):
            raise ValueError('Invalid original parameter string padding')
        position = aligned
        return value
    version = integer()
    if version != 202012090:
        raise ValueError('Unsupported original shader parameter version')
    groups = integer()
    if groups not in (0, 1):
        raise ValueError('Nonempty constant-buffer override requires explicit recovery')
    for _ in range(groups):
        string()  # Preserve original group name in input; never log it.
        if integer() != 0 or integer() != 0 or integer() != 0:
            raise ValueError('Nonempty numeric/struct parameter overrides require recovery')
    resources = integer()
    if resources != 0:
        raise ValueError('Nonempty resource overrides require explicit recovery')
    if position != len(data):
        raise ValueError('Original parameter record has unexplained trailing bytes')
    return {'serializer_version': version, 'numeric_groups': groups,
            'constant_buffers': 0, 'numeric_parameters': 0, 'struct_parameters': 0,
            'resource_parameters': 0, 'consumed_bytes': position, 'overrides_empty': True}


def quoted(value):
    if not isinstance(value, str) or any(c in value for c in '\r\n\0'):
        raise ValueError('Invalid serialized ShaderLab string')
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def number(value):
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Invalid original ShaderLab number')
    return format(value, '.9g')


def property_name(record):
    if not isinstance(record, dict):
        raise ValueError('Invalid original render-state value record')
    name = record.get('name')
    # UnityPy's typetree may retain FastPropertyName as {name:string}; it is
    # distinct from a genuinely property-driven state and must not be guessed.
    if isinstance(name, dict) and set(name) == {'name'}:
        name = name['name']
    if name in ('', None):
        return None
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_]\w*', name):
        raise ValueError('Invalid original render-state property identifier')
    return name


def val(record):
    if property_name(record) is not None:
        raise ValueError('Dynamic original render state requires explicit property recovery')
    return record['val']


def enum(record, names):
    name = property_name(record)
    if name is not None:
        return '[' + name + ']'
    value = val(record)
    if value != int(value) or int(value) not in names:
        raise ValueError('Unsupported original render-state enum')
    return names[int(value)]


def tags(value):
    return 'Tags { ' + ' '.join(quoted(k) + ' = ' + quoted(v) for k, v in value.get('tags', [])) + ' }'


COMPARE = {0: 'Off', 1: 'Never', 2: 'Less', 3: 'Equal', 4: 'LEqual', 5: 'Greater', 6: 'NotEqual', 7: 'GEqual', 8: 'Always'}
BLEND = {0: 'Zero', 1: 'One', 2: 'DstColor', 3: 'SrcColor', 4: 'OneMinusDstColor', 5: 'SrcAlpha', 6: 'OneMinusSrcColor', 7: 'DstAlpha', 8: 'OneMinusDstAlpha', 9: 'SrcAlphaSaturate', 10: 'OneMinusSrcAlpha'}
BLENDOP = {0: 'Add', 1: 'Sub', 2: 'RevSub', 3: 'Min', 4: 'Max'}
STENCILOP = {0: 'Keep', 1: 'Zero', 2: 'Replace', 3: 'IncrSat', 4: 'DecrSat', 5: 'Invert', 6: 'IncrWrap', 7: 'DecrWrap'}


def render_state(state):
    lines = []
    if state.get('m_Name'):
        lines.append('Name ' + quoted(state['m_Name']))
    if state.get('m_LOD', 0) != 0:
        raise ValueError('Unexpected pass-local LOD needs explicit recovery')
    lines.append(tags(state['m_Tags']))
    for i in range(8 if state['rtSeparateBlend'] else 1):
        blend = state['rtBlend' + str(i)]
        index = str(i) + ' ' if state['rtSeparateBlend'] else ''
        lines.append('Blend ' + index + enum(blend['srcBlend'], BLEND) + ' ' + enum(blend['destBlend'], BLEND)
                     + ', ' + enum(blend['srcBlendAlpha'], BLEND) + ' ' + enum(blend['destBlendAlpha'], BLEND))
        lines.append('BlendOp ' + index + enum(blend['blendOp'], BLENDOP) + ', ' + enum(blend['blendOpAlpha'], BLENDOP))
        # Only all/none masks occur in the supported depth recovery. Selective
        # masks require separate serialized-vs-runtime bit-order proof.
        mask = enum(blend['colMask'], {0: '0', 15: 'RGBA'})
        lines.append('ColorMask ' + mask + (' ' + str(i) if state['rtSeparateBlend'] else ''))
    lines.append('AlphaToMask ' + enum(state['alphaToMask'], {0: 'Off', 1: 'On'}))
    lines.append('ZClip ' + enum(state['zClip'], {0: 'Off', 1: 'On'}))
    # Serialized None means inherit the default, not an invented Always test.
    if property_name(state['zTest']) is not None or val(state['zTest']) != 0:
        lines.append('ZTest ' + enum(state['zTest'], COMPARE))
    lines.append('ZWrite ' + enum(state['zWrite'], {0: 'Off', 1: 'On'}))
    lines.append('Cull ' + enum(state['culling'], {0: 'Off', 1: 'Front', 2: 'Back'}))
    lines.append('Offset ' + number(val(state['offsetFactor'])) + ', ' + number(val(state['offsetUnits'])))
    if 'conservative' in state and val(state['conservative']) != 0:
        raise ValueError('Conservative raster state requires targeted support proof')
    # Reject nonneutral fixed-function fog rather than silently omitting it.
    if state.get('fogMode', -1) != -1 or any(val(state[k]) != 0 for k in ('fogDensity', 'fogStart', 'fogEnd')):
        raise ValueError('Nonneutral original fog state requires explicit recovery')
    if any(val(state['fogColor'][k]) != 0 for k in ('x', 'y', 'z', 'w')):
        raise ValueError('Nonneutral original fog color requires explicit recovery')
    stencil = []
    for key, label in (('stencilRef', 'Ref'), ('stencilReadMask', 'ReadMask'), ('stencilWriteMask', 'WriteMask')):
        stencil.append(label + ' ' + number(val(state[key])))
    nondefault = False
    for key, suffix in (('stencilOp', ''), ('stencilOpFront', 'Front'), ('stencilOpBack', 'Back')):
        op = state[key]
        if [val(op[k]) for k in ('comp', 'pass', 'fail', 'zFail')] == [8, 0, 0, 0]:
            continue
        nondefault = True
        if val(op['comp']) == 0:
            raise ValueError('Disabled/property-driven stencil comparison unresolved')
        stencil.append('Comp' + suffix + ' ' + enum(op['comp'], COMPARE))
        for k, command in (('pass', 'Pass'), ('fail', 'Fail'), ('zFail', 'ZFail')):
            stencil.append(command + suffix + ' ' + enum(op[k], STENCILOP))
    if nondefault or val(state['stencilRef']) != 0 or val(state['stencilReadMask']) != 255 or val(state['stencilWriteMask']) != 255:
        lines.extend(['Stencil {', *stencil, '}'])
    lines.append('Lighting ' + ('On' if state['lighting'] else 'Off'))
    return '\n'.join(lines)


def stage_body(vertex, fragment):
    return '#if defined(SHADER_STAGE_VERTEX)\n' + vertex + '\n#elif defined(SHADER_STAGE_FRAGMENT)\n' + fragment + '\n#else\n#error Unsupported_stage\n#endif\n'


def wrapper(parsed, stage_sources):
    if parsed.get('m_PropInfo', {}).get('m_Props'):
        raise ValueError('This exact Depth Copy wrapper requires the original empty property block')
    lines = ['Shader ' + quoted(parsed['m_Name']) + ' {', 'Properties {}']
    pass_counts = []
    for si, sub in enumerate(parsed['m_SubShaders']):
        lines.extend(['SubShader {', 'LOD ' + str(sub['m_LOD']), tags(sub['m_Tags'])])
        pass_counts.append(len(sub['m_Passes']))
        for pi, shader_pass in enumerate(sub['m_Passes']):
            if shader_pass['m_Type'] != 0:
                raise ValueError('Unexpected original pass kind')
            vertex, fragment, target = stage_sources[(si, pi)]
            if not re.fullmatch(r'[45]\.[01]', target):
                raise ValueError('Unsupported recovered original shader model')
            lines.extend(['Pass {', render_state(shader_pass['m_State']), 'HLSLPROGRAM',
                          '#pragma target ' + target, '#pragma vertex main', '#pragma fragment main',
                          stage_body(vertex, fragment), 'ENDHLSL', '}'])
        lines.append('}')
    for field, command in (('m_FallbackName', 'Fallback'), ('m_CustomEditorName', 'CustomEditor')):
        if parsed.get(field):
            lines.append(command + ' ' + quoted(parsed[field]))
    lines.append('}')
    if pass_counts != [6, 3]:
        raise ValueError('Original Depth Copy subshader6+3 topology changed')
    return '\n'.join(lines) + '\n'
