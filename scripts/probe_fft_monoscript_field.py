"""Resolve original water MonoScript class via its SHA256 within private CSharp9.

Authenticated source class identity comes from serialized globalgamemanagers
MonoScript, not a guessed type name. No original class names or source emitted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ORIGINAL_MONOSCRIPT_NAME_SHA256 = "cb4d4c048bb81a9c6260539769f50e73b91b44ae5d6ccc048038d342154ed687"
NAMESPACE = re.compile(r"(?m)^\s*namespace\s+([A-Za-z_][\w.]*)\s*(?:\{|;)")
COMPUTE_FIELD = re.compile(
    r"\b(?:public|private|protected|internal)\s+"
    r"(?:(?:static|readonly|volatile|new|protected|internal)\s+)*"
    r"(?:UnityEngine\.)?ComputeShader\s+([A-Za-z_]\w*)\s*(?:[;=,])"
)
MAX_SOURCE = 800_000

COMPUTE_ARRAY_FIELD = re.compile(
    r"\b(?:public|private|protected|internal)\s+"
    r"(?:(?:static|readonly|new|volatile)\s+)*"
    r"(?:UnityEngine\.)?ComputeShader\s*\[\s*\]\s+"
    r"([A-Za-z_]\w*)\s*(?:[;=,])"
)

CLASS_DECLARATION_TEMPLATE = r"\bclass\s+%s\b(?:\s*<[^>{}]{1,120}>)?\s*(?::\s*([^{\r\n]+))?\s*\{"
TYPE_IDENTIFIER = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$")


def inherited_compute_sources(root, path, original_source):
    """Bounded type-base exploration, never return a class or field name."""
    ancestors = []
    visited = set()
    current_path, current_source = path, original_source
    for depth in range(3):
        declaration = re.search(
            CLASS_DECLARATION_TEMPLATE % re.escape(current_path.stem),
            current_source)
        if declaration is None or not declaration.group(1):
            break
        parent = declaration.group(1).split(",", 1)[0].strip().split("<", 1)[0].strip()
        if not TYPE_IDENTIFIER.fullmatch(parent):
            break
        parent_stem = parent.rsplit(".", 1)[-1]
        if parent_stem in {"MonoBehaviour", "ScriptableObject", "Object", "Behaviour"}:
            break
        matches = [x for x in root.rglob(parent_stem + ".cs")
                   if x.is_file() and not x.is_symlink() and x.stat().st_size <= MAX_SOURCE]
        if len(matches) != 1 or matches[0] in visited:
            break
        visited.add(matches[0])
        parent_source = matches[0].read_text(encoding="utf-8-sig")
        ancestors.append({
            "inheritance_depth": depth + 1,
            "original_parent_source_sha256":
                hashlib.sha256(parent_source.encode("utf8")).hexdigest(),
            "compute_shader_type_occurrences":
                len(re.findall(r"\bComputeShader\b", parent_source)),
            "direct_field_candidates": len(COMPUTE_FIELD.findall(parent_source)),
            "token_contexts": classify_compute_shader_occurrences(parent_source),
            "original_type_name_or_csharp_published": False,
        })
        current_path, current_source = matches[0], parent_source
    return ancestors


USAGE = re.compile(r"\b(?:UnityEngine\.)?ComputeShader\b")
IDENT_AFTER_TYPE = re.compile(r"\s+([A-Za-z_]\w*)\s*([;=({,)])")
ARRAY_AFTER_TYPE = re.compile(r"\s*\[\s*\]\s+([A-Za-z_]\w*)\s*([;=,({])")
MEMBER_ACCESS = re.compile(r"^(?:\s*(?:\[[^\]]+\]\s*)*)(?:(?:public|private|protected|internal|static|readonly|new|volatile)\s+)+")


def classify_compute_shader_occurrences(raw):
    """Summarize exact token contexts, never returning private symbol text."""
    result = []
    for match in USAGE.finditer(raw):
        # Boundary is a statement/member separator, never a whole source snippet.
        prefix = raw[max(0, match.start() - 220):match.start()].split(";")[-1].split("{")[-1].split("}")[-1]
        suffix = raw[match.end():match.end() + 160]
        candidate = IDENT_AFTER_TYPE.match(suffix)
        name_sha = None
        category = "expression_or_unresolved"
        if re.search(r"\btypeof\s*\(\s*(?:UnityEngine\.)?$", prefix):
            category = "typeof_expression"
        elif candidate:
            name_sha = hashlib.sha256(candidate.group(1).encode()).hexdigest()
            end = candidate.group(2)
            # Handles [SerializeField] private ComputeShader field, and plain
            # ComputeShader field within a syntactically recognized declaration.
            prior = re.sub(r"\bUnityEngine\.$", "", prefix)
            has_member_access = bool(re.search(
                r"\b(?:public|private|protected|internal)\s+(?:(?:static|readonly|new|volatile)\s+)*$", prior))
            if end in (";", "=", ",") and has_member_access:
                category = "declared_field_candidate"
            elif end == "{" and has_member_access:
                category = "property_candidate"
            elif end == "(":
                category = "method_declaration_or_call"
            elif end == ")":
                category = "typed_parameter_candidate"
            else:
                category = "type_use_without_confirmed_field"
        elif suffix.lstrip().startswith("["):
            item = ARRAY_AFTER_TYPE.match(suffix)
            if item is not None:
                name_sha = hashlib.sha256(item.group(1).encode()).hexdigest()
                prior = re.sub(r"\bUnityEngine\.$", "", prefix)
                has_member_access = bool(re.search(
                    r"\b(?:public|private|protected|internal)\s+(?:(?:static|readonly|new|volatile)\s+)*$", prior))
                category = ("declared_compute_array_candidate"
                            if has_member_access and item.group(2) in (";", "=", ",")
                            else "array_type_usage_unresolved")
            else:
                category = "array_or_indexer_usage_unresolved"
        elif suffix.lstrip().startswith("<"):
            category = "generic_type_use"
        elif suffix.lstrip().startswith("."):
            category = "static_member_access"
        result.append({"kind": category, "following_identifier_sha256": name_sha})
    return result



def inspect(root: Path, expected_sha=ORIGINAL_MONOSCRIPT_NAME_SHA256):
    if not root.is_dir():
        raise ValueError("Private original CSharp9 decompilation missing")
    files = list(root.rglob("*.cs"))
    if len(files) > 10_000:
        raise ValueError("Unbounded original CSharp source file count")
    matches = []
    for file in files:
        if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_SOURCE:
            continue
        raw = file.read_text(encoding="utf-8-sig")
        namespaces = NAMESPACE.findall(raw)
        namespace = namespaces[0] if namespaces else ""
        # Original MonoScript asset SHA was computed on namespace + "." + class.
        identity = namespace + "." + file.stem
        if hashlib.sha256(identity.encode("utf8")).hexdigest() != expected_sha:
            continue
        compute_fields = COMPUTE_FIELD.findall(raw)
        array_fields = COMPUTE_ARRAY_FIELD.findall(raw)
        usage = classify_compute_shader_occurrences(raw)
        parents = inherited_compute_sources(root, file, raw)
        matches.append({
            "original_monoscript_identity_sha256": expected_sha,
            "original_class_csharp_source_sha256": hashlib.sha256(raw.encode("utf8")).hexdigest(),
            "original_field_type_compute_shader_declarations": len(compute_fields),
            "original_direct_compute_shader_array_declarations": len(array_fields),
            "original_direct_compute_shader_array_field_sha256": [
                hashlib.sha256(name.encode("utf8")).hexdigest() for name in array_fields
            ],
            "compute_shader_field_name_sha256": [
                hashlib.sha256(name.encode("utf8")).hexdigest() for name in compute_fields
            ],
            "compute_shader_mentions": len(re.findall(r"\bComputeShader\b", raw)),
            "compute_shader_contexts": usage,
            "bounded_original_base_type_analysis": parents,
            "waves_renderer_fft_mentions": len(re.findall(r"\bWavesRendererFFT\b", raw)),
            "dx11_fft_mentions": len(re.findall(r"\bDx11FFT\b", raw)),
            "original_type_name_or_csharp_published": False,
        })
    if len(matches) > 1:
        raise ValueError("Ambiguous original class SHA256 identity")
    return {
        "original_monoscript_identity_sha256": expected_sha,
        "original_managed_type_matched": len(matches) == 1,
        "matches": matches,
        "serialized_compute_field_offset_verified": False,
        "android_water_shader_compiled": False,
        "original_sources_modified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    a = p.parse_args()
    print("RAFT_FFT_MONOSCRIPT_CSHARP_FIELD_LINK " + json.dumps(inspect(a.source), sort_keys=True))


if __name__ == "__main__":
    main()
