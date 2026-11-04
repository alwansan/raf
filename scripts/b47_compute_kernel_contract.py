"""Source-only validation of Unity ComputeShader kernel pragma/entrypoint shape.

No compiled-kernel identity, Unity import or device execution is implied. Names,
HLSL bodies and source bytes must never appear in aggregate diagnostics.
"""
import re

LEXICAL = re.compile(r'//[^\r\n]*|/\*[\s\S]*?(?:\*/|$)|"(?:\\.|[^"\\])*"')
PRAGMA = re.compile(r'(?m)^[ \t]*#[ \t]*pragma[ \t]+kernel[ \t]+([A-Za-z_][A-Za-z_0-9]*)\b')
ENTRY = re.compile(
    r'(?m)^[ \t]*\[[ \t]*numthreads[ \t]*\([ \t]*([0-9]+)[ \t]*,[ \t]*'
    r'([0-9]+)[ \t]*,[ \t]*([0-9]+)[ \t]*\)[ \t]*\][ \t\r\n]*'
    r'(?:inline[ \t]+)?void[ \t]+([A-Za-z_][A-Za-z_0-9]*)[ \t]*'
    r'\([^;{}]*\)[ \t\r\n]*(?:\:[ \t]*[A-Za-z_][A-Za-z_0-9]*[ \t]*)?\{'
)


def mask_comments_and_strings(source: str) -> str:
    return LEXICAL.sub(
        lambda m: ''.join(c if c in '\r\n' else ' ' for c in m.group()), source
    )


def matching_close_brace(source: str, open_index: int) -> bool:
    depth = 0
    for char in source[open_index:]:
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return True
    return False


def kernel_entrypoint_profile(source: str) -> dict:
    """Aggregate only: match each declared kernel to a bounded authored body.

    Macro-generated thread dimensions or entrypoints require independent proof.
    This intentionally conservative structural gate cannot verify compiled
    Unity kernels or the original serialized ComputeShader identity.
    """
    clean = mask_comments_and_strings(source)
    kernels = [match.group(1) for match in PRAGMA.finditer(clean)]
    declarations = {}
    for match in ENTRY.finditer(clean):
        dimensions = tuple(int(match.group(i)) for i in (1, 2, 3))
        if not all(1 <= dimension <= 1024 for dimension in dimensions):
            continue
        if dimensions[0] * dimensions[1] * dimensions[2] > 1024:
            continue
        name = match.group(4)
        if matching_close_brace(clean, match.end() - 1):
            declarations[name] = declarations.get(name, 0) + 1
    valid = sum(declarations.get(name) == 1 for name in kernels)
    unique = len(kernels) == len(set(kernels))
    return {
        "kernel_count": len(kernels),
        "kernels_with_structural_entrypoints": valid,
        "unique_kernel_names": unique,
        "all_kernel_entrypoints_structural": bool(kernels) and unique and valid == len(kernels),
    }
