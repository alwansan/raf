"""SHA-pinned, redacted lexical trace of original FFT constructor size.
No original identifiers/code or shader bytes leave CI; not runtime type/dataflow proof.
"""
import argparse
import json
from pathlib import Path
import re
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.probe_original_fft_kernel_callsites import parse_original_args, sha, SIMPLE_ID
from scripts.probe_original_android_display_paths import mask_csharp_noncode

def classify_rhs(rhs):
    compact = re.sub(r"\s+", "", rhs)
    if len(compact) > 1000:
        raise ValueError("Unbounded FFT size expression")
    if re.fullmatch(r"\d{1,9}", compact):
        kind, literal = "integer_literal", int(compact)
    elif SIMPLE_ID.fullmatch(compact):
        kind, literal = "identifier_or_member", None
    elif re.search(r"\b[A-Za-z_]\w*\s*\(", compact):
        kind, literal = "call_or_cast_expression", None
    elif re.search(r"[+*/%<>-]", compact):
        kind, literal = "arithmetic_expression", None
    else:
        kind, literal = "other_expression", None
    return {"rhs_kind": kind, "integer_literal": literal,
            "rhs_compact_sha256": sha(compact), "private_expression_disclosed": False}

def analyze(caller, expected_sha):
    if not isinstance(caller, str) or len(caller) > 700000 or sha(caller) != expected_sha:
        raise ValueError("Original FFT caller source fingerprint mismatch")
    masked = mask_csharp_noncode(caller)
    constructors = list(re.finditer(r"\bnew\s+Dx11FFT\s*\(", masked))
    if len(constructors) != 1:
        raise ValueError("Original FFT constructor call count changed")
    args, _ = parse_original_args(caller, constructors[0].end()-1)
    if len(args) != 4:
        raise ValueError("Original FFT constructor arity changed")
    second = re.sub(r"\s+", "", args[1])
    if not SIMPLE_ID.fullmatch(second):
        raise ValueError("Original FFT size argument is no longer a simple reference")
    name = second.split(".")[-1]
    decl = re.compile(r"\b(int|uint|long|float|double|var)\s+" + re.escape(name) + r"\b")
    writes = re.compile(r"(?<![\w])(?:this\s*\.\s*)?" + re.escape(name)
                        + r"\s*(\+=|-=|\*=|/=|=(?!=))\s*([^;]{1,1000});")
    declarations = [{"line": masked.count("\n", 0, m.start())+1,
                     "declared_type_kind": m.group(1)} for m in decl.finditer(masked)]
    if len(declarations) > 32:
        raise ValueError("Unbounded FFT size declarations")
    changes = []
    alias_candidates = []
    for m in writes.finditer(masked):
        if len(changes) >= 32:
            raise ValueError("Unbounded FFT size writes")
        rhs = caller[m.start(2):m.end(2)].strip()
        if m.group(1) == "=" and SIMPLE_ID.fullmatch(rhs):
            alias_candidates.append(rhs)
        changes.append({"line": masked.count("\n", 0, m.start())+1,
                        "assignment_operator": m.group(1),
                        **classify_rhs(caller[m.start(2):m.end(2)])})
    if len(set(alias_candidates)) > 8:
        raise ValueError("Unbounded FFT size alias candidates")
    alias_reports = []
    for alias in sorted(set(alias_candidates)):
        alias_name = alias.split(".")[-1]
        if alias_name == name:
            continue
        alias_declarations = list(re.finditer(
            r"\b(int|uint|long|float|double|var)\s+" + re.escape(alias_name) + r"\b", masked))
        alias_writes = list(re.finditer(
            r"(?<![\w])(?:this\s*\.\s*)?" + re.escape(alias_name)
            + r"\s*(\+=|-=|\*=|/=|=(?!=))\s*([^;]{1,1000});", masked))
        if len(alias_declarations) > 32 or len(alias_writes) > 32:
            raise ValueError("Unbounded FFT size alias provenance")
        alias_reports.append({
            "alias_identifier_sha256": sha(alias),
            "declarations": [{"line": masked.count("\n", 0, m.start())+1,
                              "type_kind": m.group(1)} for m in alias_declarations],
            "lexical_writes": [{"line": masked.count("\n", 0, m.start())+1,
                                "assignment_operator": m.group(1),
                                **classify_rhs(caller[m.start(2):m.end(2)])} for m in alias_writes],
            "type_resolved": False,
        })
    return {
        "original_waves_renderer_sha256": expected_sha,
        "constructor_call_count": len(constructors),
        "constructor_line": masked.count("\n", 0, constructors[0].start())+1,
        "size_argument_identifier_sha256": sha(second),
        "size_argument_has_member_access": "." in second,
        "size_argument_declarations": declarations,
        "size_argument_lexical_writes": changes,
        "size_argument_one_hop_aliases": alias_reports,
        "source_level_size_value_proven": False,
        "runtime_resolution_or_unity_kernel_mapping_verified": False,
        "original_identifiers_or_expressions_published": False,
        "unity_or_device_execution": False,
    }

WIND_WAVES_SHA256 = 'fd145a6bc3344a0089e608d365df534bb3e4ad0b499d372c963d302620644f2f'


def analyze_resolution_owner(caller, owner, caller_sha, owner_sha):
    """Resolve one pinned property/backing-field/minimum chain, not runtime values."""
    from scripts.instrument_android_runtime_operations import body_bounds
    if len(caller) > 700000 or len(owner) > 700000 or sha(caller) != caller_sha or sha(owner) != owner_sha:
        raise ValueError('Original FFT resolution owner fingerprint mismatch')
    start, end = body_bounds(caller, 'private GpuFFT ChooseBestFFTAlgorithm(bool twoChannels)')
    body = caller[start:end]
    code = mask_csharp_noncode(body)
    calls = list(re.finditer(r'\bnew\s+Dx11FFT\s*\(', code))
    if len(calls) != 1:
        raise ValueError('Original selected FFT constructor count changed')
    args, _ = parse_original_args(body, calls[0].end()-1)
    if len(args) != 4 or not re.fullmatch(r'[A-Za-z_]\w*', args[1].strip()):
        raise ValueError('Original selected FFT size local changed')
    variable = args[1].strip()
    bindings = list(re.finditer(r'\bint\s+' + re.escape(variable) +
        r'\s*=\s*([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)\s*;', code[:calls[0].start()]))
    if len(bindings) != 1:
        raise ValueError('Original FFT size property binding changed')
    if len(re.findall(r'\b' + re.escape(variable) + r'\s*(?:\+\+|--|[+*/%\-]?=(?!=))', code)) != 1:
        raise ValueError('Original FFT size local has additional writes')
    receiver, member = bindings[0].groups()
    caller_code = mask_csharp_noncode(caller)
    if len(re.findall(r'\bprivate\s+(?:readonly\s+)?WindWaves\s+' + re.escape(receiver) + r'\s*;', caller_code)) != 1:
        raise ValueError('Original FFT property receiver type changed')
    owner_code = mask_csharp_noncode(owner)
    props = list(re.finditer(r'\bpublic\s+int\s+' + re.escape(member) +
                            r'\s*=>\s*([A-Za-z_]\w*)\s*;', owner_code))
    if len(props) != 1:
        raise ValueError('Original FFT resolution property getter changed')
    backing = props[0][1]
    if len(re.findall(r'\bprivate\s+int\s+' + re.escape(backing) + r'\s*;', owner_code)) != 1:
        raise ValueError('Original FFT resolution backing type changed')
    writes = list(re.finditer(r'\b' + re.escape(backing) + r'\s*=(?!=)\s*([A-Za-z_]\w*)\s*;', owner_code))
    if len(writes) != 1 or len(re.findall(r'\b' + re.escape(backing) + r'\s*(?:\+\+|--|[+*/%\-]?=(?!=))', owner_code)) != 1:
        raise ValueError('Original FFT resolution backing write changed')
    value = writes[0][1]
    a, b = body_bounds(owner, 'internal void ResolveFinalSettings(WaterQualityLevel quality)')
    if not a <= writes[0].start() < b:
        raise ValueError('Original FFT resolution assignment owner changed')
    minimum = list(re.finditer(r'\bint\s+' + re.escape(value) + r'\s*=\s*Mathf\s*\.\s*Min\s*\(', owner_code[a:b]))
    if len(minimum) != 1 or len(re.findall(r'\b' + re.escape(value) + r'\s*(?:\+\+|--|[+*/%\-]?=(?!=))', owner_code[a:b])) != 1:
        raise ValueError('Original FFT resolution minimum changed')
    inputs, _ = parse_original_args(owner, a + minimum[0].end()-1)
    compact = [re.sub(r'\s+', '', x) for x in inputs]
    if len(compact) != 3 or not all(SIMPLE_ID.fullmatch(x) for x in compact) or compact[2] != 'SystemInfo.maxTextureSize':
        raise ValueError('Original FFT resolution minimum inputs changed')
    return {
        'original_wind_waves_sha256': owner_sha,
        'constructor_size_property_receiver_type': 'WindWaves',
        'property_return_type': 'int',
        'property_is_direct_backing_field_getter': True,
        'backing_field_type': 'int',
        'backing_field_lexical_write_count': len(writes),
        'backing_field_write_uses_settings_minimum_local': True,
        'settings_minimum_arity': 3,
        'settings_minimum_input_hashes': [sha(x) for x in compact],
        'third_minimum_input_is_device_max_texture_size': True,
        'requested_and_quality_values_proven': False,
        'power_of_two_or_lower_bound_proven': False,
        'runtime_resolution_or_unity_kernel_mapping_verified': False,
        'original_identifiers_or_expressions_published': False,
        'unity_or_device_execution': False,
    }


def inspect(root):
    paths = list(root.rglob("WavesRendererFFT.cs"))
    if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
        raise ValueError("Original WavesRendererFFT source missing or ambiguous")
    source = paths[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    owners = list(root.rglob("WindWaves.cs"))
    if len(owners) != 1 or owners[0].is_symlink() or not owners[0].is_file():
        raise ValueError("Original WindWaves source missing or ambiguous")
    owner = owners[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    result = analyze(source, ORIGINAL_SOURCE_SHA256["WavesRendererFFT"])
    result["size_property_owner_provenance"] = analyze_resolution_owner(
        source, owner, ORIGINAL_SOURCE_SHA256["WavesRendererFFT"], WIND_WAVES_SHA256)
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    print("RAFT_ORIGINAL_FFT_SIZE_ARGUMENT " + json.dumps(inspect(p.parse_args().source), sort_keys=True))
