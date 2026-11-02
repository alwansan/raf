"""Trace where SHA-pinned original Dx11FFT computes its two-pass kernel index.

Original CSharp source stays only in temporary CI. Reports immutable SHA,
integer constants and expression shapes; does not execute or publish game code.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256
from scripts.probe_original_fft_caller_graph import source_declarations
from scripts.probe_original_fft_kernel_callsites import (
    CALL, SIMPLE_ID, parse_original_args, sha
)

MAX_ASSIGNMENTS = 24
MAX_SOURCE = 700_000



def anonymized_operator_shape(expression):
    """Preserve only numeric/operator syntax, replacing all private names."""
    if len(expression) > 600:
        raise ValueError("Original kernel index formula unbounded")
    masked_string = re.sub(r'"(?:\\.|[^"\\])*"', '"S"', expression)
    masked_identifiers = re.sub(r"\b[A-Za-z_]\w*\b", "V", masked_string)
    compact = re.sub(r"\s+", "", masked_identifiers)
    return re.sub(r"[^V0-9()\[\]{}<>!+=*/%&|^?.,:\-]", "?", compact)[:180]


def immediate_boolean_guard(text, offset):
    """Recognize only direct if(identifier) or if(!identifier) guard."""
    prefix = text[max(0, offset-250):offset]
    found = re.search(r"\bif\s*\(\s*(!?)\s*([A-Za-z_]\w*)\s*\)\s*\{?\s*$", prefix)
    if not found:
        return {"simple_condition_verified": False}
    return {"simple_condition_verified": True,
            "guard_identifier_sha256": sha(found.group(2)),
            "guard_negated": found.group(1) == "!",
            "private_guard_identifier_published": False}


def classify_index_rhs(expression):
    """No expression text in report, and definitely no evaluation."""
    result = {
        "original_expression_sha256": sha(re.sub(r"\s+", "", expression)),
        "anonymized_operator_shape": anonymized_operator_shape(expression),
        "integer_constants": [int(x) for x in re.findall(
            r"(?<![A-Za-z_.])\d{1,6}(?![A-Za-z_])", expression)][:12],
        "mathf_log2_call": bool(re.search(r"\bMathf\s*\.\s*Log\s*\(", expression)),
        "mathf_pow_call": bool(re.search(r"\bMathf\s*\.\s*Pow\s*\(", expression)),
        "has_conditional_operator": "?" in expression and ":" in expression,
        "has_addition": "+" in expression,
        "has_subtraction": "-" in expression,
        "has_multiplication": "*" in expression,
        "has_shift": "<<" in expression or ">>" in expression,
        "has_array_lookup": "[" in expression and "]" in expression,
        "original_expression_published": False,
    }
    return result


def index_source_links(original, expected):
    if not isinstance(original, str) or len(original) > MAX_SOURCE or sha(original) != expected:
        raise ValueError("Original Dx11FFT managed source hash changed or too large")
    kernel_args = []
    for match in CALL.finditer(original):
        if match.group(1) not in ("Dispatch", "SetTexture"):
            continue
        args, _ = parse_original_args(original, match.end()-1)
        if len(args) >= 3:
            kernel_args.append(args[0].strip())
    base = next((v for v in kernel_args if SIMPLE_ID.fullmatch(v)), None)
    if base is None:
        raise ValueError("Original first-pass FFT index variable not identifiable")
    ref_regex = re.compile(r"\b(?:int\s+|var\s+)?(?:this\s*\.\s*)?" +
                           re.escape(base) + r"\s*(=|\+=|-=)\s*([^;]{1,600})\s*;")
    assignments = []
    for m in ref_regex.finditer(original):
        if len(assignments) >= MAX_ASSIGNMENTS:
            raise ValueError("Too many original FFT index assignments")
        assignments.append({
            "source_line": original.count("\n", 0, m.start()) + 1,
            "operator": m.group(1),
            "right_hand_side": classify_index_rhs(m.group(2)),
            "preceding_immediate_guard": immediate_boolean_guard(original, m.start()),
        })
    constructors = [m for m in source_declarations(original) if m["name"] == "Dx11FFT"]
    formula = {"constructor_signature_matched": False,
               "first_assignment_matches_constructor_int_parameter": False,
               "bank_stride_guard_matches_fourth_bool_parameter": False,
               "proven_formula_shape": None,
               "verified_runtime_kernel_lookup_index": False}
    if len(constructors) == 1 and len(constructors[0]["params"]) == 4:
        args = constructors[0]["params"]
        integer = re.fullmatch(r"\s*int\s+([A-Za-z_]\w*)\s*", args[1])
        fourth = re.fullmatch(r"\s*bool\s+([A-Za-z_]\w*)\s*", args[3])
        formula["constructor_signature_matched"] = bool(integer and fourth)
        if integer and fourth and len(assignments) == 2:
            rhs_shape = assignments[0]["right_hand_side"]["anonymized_operator_shape"]
            literal_formula = re.fullmatch(
                r"\s*([A-Za-z_]\w*)\s*-\s*5\s*<<\s*1\s*",
                original[re.search(r"\b" + re.escape(base) +
                    r"\s*=\s*[^;]{1,600}\s*;", original).start():].split("=", 1)[1].split(";", 1)[0]
            ) if rhs_shape == "V-5<<1" else None
            formula["first_assignment_matches_constructor_int_parameter"] = (
                bool(literal_formula and literal_formula.group(1) == integer.group(1)))
            formula["bank_stride_guard_matches_fourth_bool_parameter"] = (
                assignments[1]["operator"] == "+="
                and assignments[1]["right_hand_side"]["anonymized_operator_shape"] == "10"
                and assignments[1]["preceding_immediate_guard"].get("guard_identifier_sha256")
                == sha(fourth.group(1)))
            if (formula["first_assignment_matches_constructor_int_parameter"]
                    and formula["bank_stride_guard_matches_fourth_bool_parameter"]):
                formula["proven_formula_shape"] = "(n-5)<<1, then conditional +10"
    # Trace the formula seed separately: it is NOT assumed to be the int
    # constructor parameter. Only SHA hashes and masked operator shapes leave CI.
    seed = {"first_formula_seed_identified": False,
            "first_formula_seed_identifier_sha256": None,
            "seed_assignment_count": 0,
            "seed_assignments": [],
            "seed_alias_of_constructor_int_proven": False}
    initial_formula = re.search(
        r"\b" + re.escape(base) +
        r"\s*=\s*([A-Za-z_]\w*)\s*-\s*5\s*<<\s*1\s*;", original)
    if initial_formula:
        variable = initial_formula.group(1)
        seed["first_formula_seed_identified"] = True
        seed["first_formula_seed_identifier_sha256"] = sha(variable)
        pattern = re.compile(r"\b(?:int\s+|var\s+)?(?:this\s*\.\s*)?" +
                             re.escape(variable) + r"\s*=\s*([^;]{1,600})\s*;")
        lineage = []
        for m in pattern.finditer(original):
            if len(lineage) >= 20:
                raise ValueError("Too many original FFT index seed assignments")
            lineage.append({
                "source_line": original.count("\n", 0, m.start())+1,
                "rhs": classify_index_rhs(m.group(1)),
            })
        seed["seed_assignments"] = lineage
        seed["seed_assignment_count"] = len(lineage)
        if len(constructors) == 1 and len(constructors[0]["params"]) == 4:
            ctor_int = re.fullmatch(
                r"\s*int\s+([A-Za-z_]\w*)\s*", constructors[0]["params"][1])
            if ctor_int:
                seed["seed_alias_of_constructor_int_proven"] = variable == ctor_int.group(1)
    param_declaration = bool(re.search(r"\bint\s+" + re.escape(base) + r"\s*[,)]", original))
    # Detect references without reporting proprietary field identifiers.
    occurrences = len(re.findall(r"\b" + re.escape(base) + r"\b", original))
    return {
        "original_dx11fft_source_sha256_verified": True,
        "first_pass_index_identifier_sha256": sha(base),
        "first_pass_index_source_occurrences": occurrences,
        "first_pass_index_int_parameter_declaration_detected": param_declaration,
        "index_assignment_count": len(assignments),
        "index_assignments": assignments,
        "source_proven_original_constructor_kernel_bank_formula": formula,
        "source_proven_original_kernel_index_formula_seed_lineage": seed,
        "first_and_second_pass_index_runtime_values_verified": False,
        "original_game_expressions_or_identifiers_published": False,
        "android_gpu_execution_proven": False,
    }


def inspect(root):
    paths = list(root.rglob("Dx11FFT.cs"))
    if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
        raise ValueError("Original Dx11FFT caller source missing")
    original = paths[0].read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    return index_source_links(original, ORIGINAL_SOURCE_SHA256["Dx11FFT"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    a = p.parse_args()
    print("RAFT_ORIGINAL_DX11FFT_INDEX_DERIVATION " +
          json.dumps(inspect(a.source), sort_keys=True))


if __name__ == "__main__":
    main()
