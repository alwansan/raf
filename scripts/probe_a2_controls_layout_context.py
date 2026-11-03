"""Source-locked private ControlsSettingsBox sizeDelta context probe (CPU only).

Reports structural counts, hashes and line numbers, never decompiled method names,
expression bodies or original source. This is *not* a Unity or on-phone test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_android_display_paths import mask_csharp_noncode
from scripts.probe_a2_settings_layout import source_sites

ORIGINAL_SHA256 = 'b64ba19e2d55fe503045e523c3c8658adb4ca3ededaccfecf6521bad1600ef92'
EXPECTED_LINE = 110
MAX_SOURCE_BYTES = 3 * 1024 * 1024
MAX_SCOPE_FILES = 6
SIZE_DELTA = re.compile(r'\.\s*sizeDelta\s*=(?!=|>)')
# A method signature with an explicit return type. No identifier or source text is emitted.
METHOD = re.compile(
    r'(?<![.\w])(?:(?:public|private|protected|internal|static|override|virtual|sealed|'
    r'async|new|extern|unsafe|partial)\s+)*'
    r'(?P<returns>[A-Za-z_][\w.<>,?\[\]]*)\s+'
    r'(?P<name>[A-Za-z_]\w*)\s*\([^;{}]{0,600}\)\s*\{'
)
NOT_METHOD = {'if', 'for', 'while', 'foreach', 'switch', 'catch', 'using',
              'lock', 'return', 'new', 'throw', 'typeof', 'sizeof', 'fixed'}


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def line_at(code, offset):
    return code.count('\n', 0, offset) + 1


def closed_brace(code, opening):
    if code[opening] != '{':
        raise ValueError('Expected code brace')
    depth = 0
    for offset in range(opening, len(code)):
        if code[offset] == '{':
            depth += 1
        elif code[offset] == '}':
            depth -= 1
            if depth == 0:
                return offset
    return None


def inspect_text(source, strict_line=True):
    code = mask_csharp_noncode(source)
    matches = list(SIZE_DELTA.finditer(code))
    if len(matches) != 1:
        raise ValueError('Expected exactly one executable original sizeDelta assignment')
    match = matches[0]
    line = line_at(code, match.start())
    if strict_line and line != EXPECTED_LINE:
        raise ValueError('Original ControlsSettingsBox sizeDelta location changed')
    candidates = []
    for method in METHOD.finditer(code):
        if method.group('returns') in NOT_METHOD or method.group('name') in NOT_METHOD:
            continue
        opening = method.end() - 1
        end = closed_brace(code, opening)
        if end is not None and method.start() < match.start() < end:
            candidates.append((method, end))
    if not candidates:
        raise ValueError('Original sizeDelta assignment lacks recognizable enclosing method')
    method, end = max(candidates, key=lambda value: value[0].start())
    body = code[method.end():end]
    before = code[method.end():match.start()]
    after = code[match.end():end]
    # Only a simple terminal identifier is classified as a direct variable target.
    # A method chain is deliberately recorded as unknown; no guesses.
    target_match = re.search(r'(?P<name>\b[A-Za-z_]\w*)\s*$', code[max(0, match.start()-160):match.start()])
    target = target_match.group('name') if target_match else None
    prior_ident = code[max(0, match.start()-160):match.start()]
    form = ('unknown' if not target else
            'member_or_chain' if re.search(r'\b[A-Za-z_]\w*\s*\([^)]*\)\s*\.\s*' + re.escape(target) + r'\s*$', prior_ident)
            else 'direct_identifier')
    # Search only within this original method body for a typed declaration of the
    # exact target identifier; merely seeing RectTransform elsewhere is not linkage.
    typed = bool(target and re.search(r'\bRectTransform\s+' + re.escape(target) + r'\b', body))
    component = bool(target and re.search(
        r'\b' + re.escape(target) + r'\s*=\s*[^;]{0,300}\bGetComponent\s*<\s*RectTransform\s*>', before))
    # Bound to the statement; report syntax categories only, never RHS source.
    semicolon = code.find(';', match.end(), min(match.end() + 1000, end))
    if semicolon < 0:
        raise ValueError('Unbounded sizeDelta assignment statement')
    rhs = code[match.end():semicolon]
    if not rhs.strip():
        raise ValueError('Empty sizeDelta right-hand side')
    # CSharp9 includes assignments such as new Vector2(..), no variable text emitted.
    method_signature = code[method.start():method.end()].strip()
    parameters = method_signature.split('(', 1)[1].rsplit(')', 1)[0]
    # Bound to syntactically typed signature parameters. Never print parameter names.
    rect_parameters = set(re.findall(r'\b(?:UnityEngine\s*\.\s*)?RectTransform\s+([A-Za-z_]\w*)\b', parameters))
    vector_parameters = set(re.findall(r'\b(?:UnityEngine\s*\.\s*)?Vector2\s+([A-Za-z_]\w*)\b', parameters))
    transform_parameters = set(re.findall(r'\b(?:UnityEngine\s*\.\s*)?Transform\s+([A-Za-z_]\w*)\b', parameters))
    rhs_ident = rhs.strip() if re.fullmatch(r'\s*[A-Za-z_]\w*\s*', rhs) else None
    outside_method = code[:method.start()] + code[end+1:]
    call_refs = [x for x in re.finditer(r'\b' + re.escape(method.group('name')) + r'\s*\(', code)
                 if x.start() != method.start() and not method.start() <= x.start() < method.end()]
    return {
        'original_sha256': digest(source.replace('\r\n', '\n')),
        'size_delta_assignment_count': len(matches),
        'size_delta_line': line,
        'target_form': form,
        'target_identifier_sha256': digest(target) if target else None,
        'target_has_local_recttransform_declaration': typed,
        'target_is_recttransform_parameter': bool(target and target in rect_parameters),
        'target_is_transform_parameter': bool(target and target in transform_parameters),
        'rhs_is_simple_identifier': rhs_ident is not None,
        'rhs_is_vector2_parameter': bool(rhs_ident and rhs_ident in vector_parameters),
        'owner_declares_target_as_recttransform_outside_method': bool(target and re.search(
            r'\bRectTransform\s+' + re.escape(target) + r'\b', outside_method)),
        'target_initialized_via_getcomponent_recttransform': component,
        'method_signature_sha256': digest(method_signature),
        'method_start_line': line_at(code, method.start()),
        'method_end_line': line_at(code, end),
        'method_is_settings_lifecycle': method.group('name') in {'SettingStart', 'Start', 'OnEnable', 'Awake', 'Update'},
        'method_explicit_local_invocations': len(call_refs),
        'method_screen_resolution_mutations': len(re.findall(r'\bScreen\s*\.\s*SetResolution\s*\(', body)),
        'method_canvas_scaler_writes': sum(len(re.findall(r'\.\s*' + name + r'\s*=(?!=|>)', body))
                                            for name in ('referenceResolution','matchWidthOrHeight','uiScaleMode','screenMatchMode')),
        'rhs_uses_new_vector2': bool(re.search(r'\bnew\s+(?:UnityEngine\s*\.\s*)?Vector2\s*\(', rhs)),
        'rhs_uses_screen_dimension': bool(re.search(r'\bScreen\s*\.\s*(?:width|height|resolutions?)\b', rhs)),
        'rhs_uses_recttransform': bool(re.search(r'\bRectTransform\b|\.\s*(?:rect|sizeDelta)\b', rhs)),
        'source_mutated': False,
        'settings_stretch_cause_proven': False,
        'unity_or_device_executed': False,
    }


def inspect_root(root, verify=True):
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Unsafe original source root')
    paths = sorted(root.rglob('ControlsSettingsBox.cs'))
    if len(paths) != 1 or len(paths) > MAX_SCOPE_FILES:
        raise ValueError('Original ControlsSettingsBox source missing or duplicated')
    file = paths[0]
    if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError('Unsafe original ControlsSettingsBox source')
    source = file.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    if verify and digest(source) != ORIGINAL_SHA256:
        raise ValueError('Unknown original ControlsSettingsBox SHA256')
    result = inspect_text(source, strict_line=verify)
    result['verified_original_source'] = verify
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    args = p.parse_args()
    print('RAFT_A2_CONTROLS_LAYOUT_CONTEXT ' + json.dumps(inspect_root(args.source), sort_keys=True))


if __name__ == '__main__':
    main()
