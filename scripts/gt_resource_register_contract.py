"""Bounded scanner for translated scalar texture/sampler declarations.

Original DXBC slots come from symbolic names, not renumbered HLSL bindings.
Only the default register space is supported. This module does not infer
resource names, array layouts, UAV semantics, or original asset permissions.
"""
import re

IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')
_TYPE = r'(?:Texture\w*(?:\s*<[^;{}>]+>)?|SamplerState|SamplerComparisonState)'
# Keep the four numbered groups used by existing callers of RESOURCE.
RESOURCE = re.compile(r'\b(' + _TYPE + r')\s+([A-Za-z_]\w*)\s*:\s*register\s*\(\s*([ts])(\d+)\s*(?:,\s*space0\s*)?\)\s*;')
_START = re.compile(r'\b(' + _TYPE + r')\s+([A-Za-z_]\w*)\s*(?=[:;\[])')
_UNREGISTERED = re.compile(r'\b(' + _TYPE + r')\s+([A-Za-z_]\w*)\s*;')
_COMMENT_OR_STRING = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\\r\n])*"')


def mask_noncode(source):
    """Preserve offsets and line endings while masking comments/strings."""
    if not isinstance(source, str):
        raise ValueError('resource_source_not_text')
    return _COMMENT_OR_STRING.sub(lambda m: re.sub(r'[^\r\n]', ' ', m[0]), source)


def registered_resources(source, *, allow_unregistered=False):
    """Return offset-preserving matches; reject unsupported declarations.

    The input domain is translated HLSL, not an arbitrary macro-expanded
    shader. Comments/strings are masked only for scanning. Texture arrays
    such as Texture2DArray are types; descriptor arrays (name[N]) are not
    supported here. Nonzero spaces must never disappear from the census.
    """
    masked = mask_noncode(source)
    matches, symbols, translated = [], set(), set()
    for start in _START.finditer(masked):
        match = RESOURCE.match(masked, start.start())
        if match is None:
            if allow_unregistered and _UNREGISTERED.match(masked, start.start()):
                if start[2] in symbols:
                    raise ValueError('duplicate_translated_resource_symbol')
                symbols.add(start[2])
                continue
            raise ValueError('unsupported_texture_sampler_declaration_or_register_space')
        expected = 't' if match[1].startswith('Texture') else 's'
        if match[3] != expected:
            raise ValueError('resource_register_class_mismatch')
        key = (match[3], int(match[4]))
        if match[2] in symbols or key in translated:
            raise ValueError('duplicate_translated_resource_symbol_or_slot')
        symbols.add(match[2])
        translated.add(key)
        matches.append(match)
    return matches


def strip_registered_resources(source):
    """Erase only validated t/s annotations for Unity name-based binding."""
    for match in reversed(registered_resources(source, allow_unregistered=True)):
        source = source[:match.end(2)] + ';' + source[match.end():]
    return source


def texture_sampler_bindings(source, common, names, resources):
    """Resolve authored common/variant metadata, with explicit override lanes.

    Variant resource records override the same common slot, as in the existing
    stage decoder. Duplicates *within* either lane and ambiguous samplers fail.
    Unused metadata is not an error: the translator may optimize it away.
    """
    def insert(lane, slot, name, sampler):
        if (type(slot) is not int or slot < 0 or slot in lane
                or type(name) is not str or not IDENT.fullmatch(name)
                or type(sampler) is not int):
            raise ValueError('invalid_or_duplicate_original_texture_slot')
        lane[slot] = (name, sampler)

    textures, overrides = {}, {}
    for item in common['m_TextureParams']:
        key = item['m_NameIndex']
        if type(key) is not int or key not in names:
            raise ValueError('original_texture_name_index_missing')
        insert(textures, item['m_Index'], names[key], item['m_SamplerIndex'])
    for item in resources:
        if item['kind'] == 0:
            insert(overrides, item['index'], item['name'], item['extra_value'])
    textures.update(overrides)
    bindings, used, target_names = [], set(), set()
    for match in registered_resources(source):
        symbol, kind = match[2], match[3]
        slot_match = re.fullmatch(kind + r'(\d+)', symbol)
        if slot_match is None:
            raise ValueError('original_texture_or_sampler_slot_missing')
        slot = int(slot_match[1])
        candidates = ([textures[slot][0]] if slot in textures else []) if kind == 't' else [
            name for name, sampler in textures.values() if sampler == slot]
        if len(candidates) != 1 or (kind, slot) in used:
            raise ValueError('original_texture_or_sampler_binding_ambiguous')
        name = candidates[0]
        target = name if kind == 't' else 'sampler' + name
        if target in target_names:
            raise ValueError('original_resource_symbol_collision')
        used.add((kind, slot))
        target_names.add(target)
        bindings.append({'kind': kind, 'slot': slot, 'source_texture_name': name})
    return bindings
