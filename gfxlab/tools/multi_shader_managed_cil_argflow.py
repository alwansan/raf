#!/usr/bin/env python3
"""GFX-MULTI-045: private, fail-closed, bounded ECMA-335 CIL argument flow.

Only a straight-line, fully supported symbolic stack trace can prove that an
authentic Shader48 property literal (or a validated Shader.PropertyToID result)
reaches the FIRST argument of an authentic UnityEngine Material/MPB Set* call.
This is source *script* evidence, NOT a DXBC register mapping or GPU proof.
No original literal, IL, token, method name, binary or source is emitted.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import ZIP2_SHA, read_manifest, stage_originals
from gfxlab.tools.multi_shader_managed_literal_sidecar import (
    ASSEMBLIES, bound_source_names, sha256_file, validate_manifest,
)
from gfxlab.tools.multi_shader_managed_cil_calls import (
    MAX_METHODS, MAX_METHOD_INSTRUCTIONS, MAX_TOTAL_IL_INSTRUCTIONS,
    UNITY_NS,
)

MAX_STACK = 128
MAX_CANDIDATE_METHOD_INSTRUCTIONS = 4096
MAX_SIGNATURE_BYTES = 2048
TARGET_METHODS = frozenset(("SetTexture", "SetFloat", "SetColor", "SetVector", "SetMatrix"))
TARGET_OWNERS = frozenset(("Material", "MaterialPropertyBlock"))
BRANCH_PREFIXES = ("br", "beq", "bne", "bge", "bgt", "ble", "blt", "leave")
BRANCH_OPS = frozenset(("switch", "throw", "rethrow", "endfinally", "endfilter", "jmp"))
UNKNOWN = (None, None)


def compressed_uint(blob, pos):
    if pos >= len(blob):
        raise ValueError("GFX045_SIGNATURE_TRUNCATED")
    a = blob[pos]
    if a < 128:
        return a, pos + 1
    if a < 192:
        if pos + 2 > len(blob):
            raise ValueError("GFX045_SIGNATURE_TRUNCATED")
        return ((a & 63) << 8) | blob[pos + 1], pos + 2
    if a < 224:
        if pos + 4 > len(blob):
            raise ValueError("GFX045_SIGNATURE_TRUNCATED")
        return ((a & 31) << 24) | (blob[pos + 1] << 16) | (blob[pos + 2] << 8) | blob[pos + 3], pos + 4
    raise ValueError("GFX045_SIGNATURE_COMPRESSED_INT_INVALID")


def _sig_type(blob, pos, depth=0):
    """Subset of ECMA-335 II.23.2.12 types; unknown forms fail closed."""
    if depth > 8 or pos >= len(blob):
        raise ValueError("GFX045_SIGNATURE_TYPE_INVALID")
    t = blob[pos]
    pos += 1
    simple = {1: "void", 2: "bool", 3: "char", 4: "i1", 5: "u1",
              6: "i2", 7: "u2", 8: "i4", 9: "u4", 10: "i8",
              11: "u8", 12: "r4", 13: "r8", 14: "string",
              22: "typedref", 24: "nativeint", 25: "nativeuint",
              28: "object"}
    if t in simple:
        return simple[t], pos
    if t in (15, 16, 29, 69):  # PTR, BYREF, SZARRAY, PINNED
        _, pos = _sig_type(blob, pos, depth + 1)
        return "compound", pos
    if t in (17, 18, 19, 30):  # VALUETYPE, CLASS, VAR, MVAR + compressed token
        _, pos = compressed_uint(blob, pos)
        return "compound", pos
    if t in (31, 32):  # CMOD_REQD/OPT: token followed by actual type
        _, pos = compressed_uint(blob, pos)
        return _sig_type(blob, pos, depth + 1)
    if t == 21:  # GENERICINST: class/valuetype, token, arity, args
        if pos >= len(blob) or blob[pos] not in (17, 18):
            raise ValueError("GFX045_GENERIC_SIGNATURE_INVALID")
        pos += 1
        _, pos = compressed_uint(blob, pos)
        n, pos = compressed_uint(blob, pos)
        if n > 32:
            raise ValueError("GFX045_GENERIC_ARITY_UNBOUNDED")
        for _ in range(n):
            _, pos = _sig_type(blob, pos, depth + 1)
        return "compound", pos
    raise ValueError("GFX045_UNSUPPORTED_SIGNATURE_TYPE")


def parse_member_signature(blob):
    """Return strict (argc, has_this, first_arg_type, return_type), else None."""
    if not isinstance(blob, (bytes, bytearray)) or not 2 <= len(blob) <= MAX_SIGNATURE_BYTES:
        return None
    try:
        flags = blob[0]
        if flags & 0x0F not in (0, 5) or flags & 0x10:
            return None  # generics, vararg/field/property: not analyzed
        argc, pos = compressed_uint(blob, 1)
        if argc > 24:
            return None
        ret, pos = _sig_type(blob, pos)
        params = []
        for _ in range(argc):
            typ, pos = _sig_type(blob, pos)
            params.append(typ)
        if pos != len(blob):
            return None
        return (argc, bool(flags & 0x20), params[0] if params else None, ret)
    except ValueError:
        return None


def _local_key(name, operand):
    for prefix in ("ldloc.", "stloc."):
        if name.startswith(prefix) and name[len(prefix):] in ("0", "1", "2", "3"):
            return int(name[len(prefix):])
    if name in ("ldloc", "stloc", "ldloc.s", "stloc.s"):
        value = getattr(operand, "index", None)
        if type(value) is int and 0 <= value <= 4096:
            return value
    return None


def _unsupported_control_flow(name):
    return name.startswith(BRANCH_PREFIXES) or name in BRANCH_OPS or name.startswith("endfinally")


def _interpret(normalized, valid_names, bound_names):
    """Pure synthetic-testable interpreter; one branch/unknown opcode poisons proof.

    Each normalized instruction is (mnemonic, payload). Call payload (when
    available) is a validated (owner, method, argc, has_this, first_type, ret).
    A property marker is never invented from a call's NAME or mere adjacency.
    """
    if not isinstance(normalized, list) or len(normalized) > MAX_CANDIDATE_METHOD_INSTRUCTIONS:
        raise ValueError("GFX045_METHOD_UNBOUNDED")
    if any(_unsupported_control_flow(n) for n, _ in normalized):
        return {"eligible": False, "reason": "control_flow", "direct": set(), "id": set(),
                "bound": set(), "verified_calls": 0}
    stack, locals_map = [], {}
    direct, through_id, bound = set(), set(), set()
    verified_calls = 0
    def pop():
        if not stack:
            raise ValueError("GFX045_CIL_STACK_UNDERFLOW")
        return stack.pop()
    try:
        for name, value in normalized:
            if name == "nop":
                pass
            elif name == "ldstr":
                stack.append(("string", value) if value in valid_names else UNKNOWN)
            elif name.startswith(("ldarg.", "ldarg ", "ldarga")) or name in ("ldarg", "ldarg.s", "ldnull", "ldftn", "ldvirtftn") or name.startswith("ldc."):
                stack.append(UNKNOWN)
            elif name.startswith("ldloc"):
                key = _local_key(name, value)
                if key is None:
                    raise ValueError("GFX045_UNSUPPORTED_LOCAL")
                stack.append(locals_map.get(key, UNKNOWN))
            elif name.startswith("stloc"):
                key = _local_key(name, value)
                if key is None:
                    raise ValueError("GFX045_UNSUPPORTED_LOCAL")
                locals_map[key] = pop()
            elif name == "dup":
                stack.append(stack[-1] if stack else pop())
            elif name == "pop":
                pop()
            elif name in ("ldfld", "ldflda"):
                pop()
                stack.append(UNKNOWN)
            elif name in ("ldsfld", "ldsflda"):
                stack.append(UNKNOWN)
            elif name in ("stfld",):
                pop(); pop()
            elif name in ("stsfld",):
                pop()
            elif name in ("castclass", "isinst", "box", "unbox.any"):
                pop(); stack.append(UNKNOWN)
            elif name in ("call", "callvirt"):
                if value is None:
                    raise ValueError("GFX045_CALL_SIGNATURE_UNRESOLVED")
                owner, method, argc, has_this, first_type, ret = value
                if not 0 <= argc <= 24 or (name == "callvirt" and not has_this):
                    raise ValueError("GFX045_INVALID_CALL_ARITY")
                args = [pop() for _ in range(argc)]
                args.reverse()
                if has_this:
                    pop()  # actual method receiver must be present
                if (owner == "Shader" and method == "PropertyToID"
                    and argc == 1 and first_type == "string" and ret == "i4"
                    and not has_this and args[0][0] == "string"):
                    stack.append(("propertyid", args[0][1]))
                else:
                    if (owner in TARGET_OWNERS and method in TARGET_METHODS
                        and first_type in ("string", "i4") and args):
                        marker, prop = args[0]
                        if ((first_type == "string" and marker == "string")
                            or (first_type == "i4" and marker == "propertyid")):
                            (direct if marker == "string" else through_id).add(prop)
                            if prop in bound_names:
                                bound.add(prop)
                            verified_calls += 1
                    if ret != "void":
                        stack.append(UNKNOWN)
            elif name == "ret":
                # A return after a property call does not create another proof.
                break
            else:
                raise ValueError("GFX045_UNSUPPORTED_IL_INSTRUCTION")
            if len(stack) > MAX_STACK:
                raise ValueError("GFX045_STACK_UNBOUNDED")
    except (ValueError, IndexError):
        # Entire method excluded, including any earlier candidate: fail-closed.
        return {"eligible": False, "reason": "unsupported_or_underflow", "direct": set(),
                "id": set(), "bound": set(), "verified_calls": 0}
    return {"eligible": True, "reason": None, "direct": direct, "id": through_id,
            "bound": bound, "verified_calls": verified_calls}


def _call_ref(instr, refs):
    from dncil.clr.token import Token
    op = instr.operand
    if not isinstance(op, Token) or op.table != 10 or refs is None or not 1 <= op.rid <= len(refs.rows):
        return None
    mr = refs.rows[op.rid - 1]
    parent = getattr(getattr(mr, "Class", None), "row", None)
    ns = str(getattr(parent, "TypeNamespace", ""))
    owner = str(getattr(parent, "TypeName", "")) if ns == UNITY_NS else "Other"
    method = str(mr.Name)
    sig_value = getattr(getattr(mr, "Signature", None), "value", None)
    sig = parse_member_signature(sig_value)
    if sig is None:
        return None
    argc, has_this, first_type, ret = sig
    return (owner, method, argc, has_this, first_type, ret)


def inspect_assembly(path, names, bound_names):
    import dnfile
    from dncil.cil.body import CilMethodBody
    from dncil.cil.error import MethodBodyFormatError
    from dncil.cil.body.reader import CilMethodBodyReaderBase
    from dncil.clr.token import StringToken

    pe = dnfile.dnPE(str(path))
    if not pe.net or not pe.net.metadata or not pe.net.mdtables:
        raise ValueError("GFX045_AUTHENTIC_MANAGED_METADATA_ABSENT")
    defs, refs = pe.net.mdtables.MethodDef, pe.net.mdtables.MemberRef
    if defs is None or len(defs.rows) > MAX_METHODS:
        raise ValueError("GFX045_METHOD_COUNT_UNBOUNDED")
    class Reader(CilMethodBodyReaderBase):
        def __init__(self, row):
            self.pe = pe
            self.offset = pe.get_offset_from_rva(row.Rva)
        def read(self, n):
            if type(n) is not int or not 0 <= n <= 10 * 1024 * 1024:
                raise ValueError("GFX045_READ_SIZE")
            data = self.pe.get_data(self.pe.get_rva_from_offset(self.offset), n)
            if len(data) != n:
                raise ValueError("GFX045_TRUNCATED_METHOD")
            self.offset += n
            return data
        def tell(self):
            return self.offset
        def seek(self, off):
            self.offset = off
            return off

    count = Counter({
        "eligible_method_definitions": 0, "parsed_methods": 0,
        "parse_failures": 0, "total_il_instructions": 0,
        "source_methods_with_exact_shader_property_string": 0,
        "candidate_methods_rejected_by_fail_closed_interpreter": 0,
        "eligible_candidate_straight_line_methods": 0,
        "proven_CIL_Set_argument_calls": 0,
        "source_property_literals_passed_directly": 0,
        "source_property_literals_passed_via_PropertyToID": 0,
        "source_bound_texture_properties_with_proven_CIL_Set_arguments": 0
    })
    direct, id_props, bound = set(), set(), set()
    for row in defs.rows:
        if row.Rva == 0 or not row.ImplFlags.miIL or row.Flags.mdAbstract or row.Flags.mdPinvokeImpl:
            continue
        count["eligible_method_definitions"] += 1
        try:
            body = CilMethodBody(Reader(row))
        except (MethodBodyFormatError, ValueError, IndexError, EOFError):
            count["parse_failures"] += 1
            continue
        instructions = body.instructions
        count["parsed_methods"] += 1
        count["total_il_instructions"] += len(instructions)
        if len(instructions) > MAX_METHOD_INSTRUCTIONS or count["total_il_instructions"] > MAX_TOTAL_IL_INSTRUCTIONS:
            raise ValueError("GFX045_IL_LIMIT_EXCEEDED")
        normalized, has_original_literal = [], False
        for ins in instructions:
            name, op = ins.mnemonic, ins.operand
            if name == "ldstr" and isinstance(op, StringToken):
                if pe.net.user_strings is None:
                    raise ValueError("GFX045_US_HEAP_MISSING")
                item = pe.net.user_strings.get(op.rid)
                if item is None or not isinstance(item.value, str):
                    raise ValueError("GFX045_LDSTR_UNRESOLVED")
                op = item.value
                has_original_literal |= op in names
            elif name in ("call", "callvirt"):
                op = _call_ref(ins, refs)
            normalized.append((name, op))
        if not has_original_literal:
            continue
        count["source_methods_with_exact_shader_property_string"] += 1
        if len(normalized) > MAX_CANDIDATE_METHOD_INSTRUCTIONS:
            count["candidate_methods_rejected_by_fail_closed_interpreter"] += 1
            continue
        result = _interpret(normalized, names, bound_names)
        if not result["eligible"]:
            count["candidate_methods_rejected_by_fail_closed_interpreter"] += 1
            continue
        count["eligible_candidate_straight_line_methods"] += 1
        count["proven_CIL_Set_argument_calls"] += result["verified_calls"]
        direct.update(result["direct"])
        id_props.update(result["id"])
        bound.update(result["bound"])
    count["source_property_literals_passed_directly"] = len(direct)
    count["source_property_literals_passed_via_PropertyToID"] = len(id_props)
    count["source_bound_texture_properties_with_proven_CIL_Set_arguments"] = len(bound)
    return dict(count)


def audit(root, stage):
    validate_manifest(read_manifest(root))
    source_names, _, _, bound_names, _ = bound_source_names(stage)
    orig = ASSEMBLIES["Assembly-CSharp"]
    path = root / "Raft" / orig["path"]
    if (not path.is_file() or path.is_symlink()
        or path.stat().st_size != orig["bytes"] or sha256_file(path) != orig["sha"]):
        raise ValueError("GFX045_ORIGINAL_ASSEMBLY_SHA_MISMATCH")
    counts = inspect_assembly(path, source_names, bound_names)
    return {
        "experiment": "GFX-MULTI-045",
        "evidence_level": "ORIGINAL_SOURCE_SCRIPT_ARGUMENT_ONLY",
        "original_zip2_sha": ZIP2_SHA,
        "authentic_original_Shader48_property_count": len(source_names),
        "authentic_original_bound_texture_property_count": len(bound_names),
        "CIL_argument_flow_safe_counts": counts,
        "original_Material_property_to_DX11_register_mapping_verified": False,
        "original_constant_buffer_byte_offsets_verified": False,
        "Shader48_original_Android_runtime_verified": False,
        "originalShaderRestored": False,
        "pc_to_adreno_original_pixel_parity": False,
        "original_names_IL_tokens_binaries_or_shader_bytes_exported": False,
        "phase_closed": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip2", required=True, type=Path)
    ap.add_argument("--stage", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    result = audit(args.zip2, stage_originals(args.zip2, args.stage))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("GFX_MULTI045_SAFE_ORIGINAL_CIL_ARGUMENT_FLOW_COUNTS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
