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


# Only literal #if 0 / #if 1 conditions are resolved. #ifdef, #ifndef,
# symbolic expressions and macros are intentionally *unknown*; both sides are
# masked unless separately authenticated with the actual Unity defines.
# This must never be confused with a compiled-kernel/identity verifier.
CONDITIONAL = re.compile(r'^[ \t]*#[ \t]*(if|ifdef|ifndef|elif|else|endif)\b([^\r\n]*)')
# A reachable #error makes the source impossible to compile, even if its
# pragma/entrypoint text otherwise looks structurally complete.
ERROR_DIRECTIVE = re.compile(r'^[ \t]*#[ \t]*error\b')


def mask_inactive_preprocessor(clean: str) -> str:
    """Retain definitely enabled conditional branches; mask ambiguous ones.

    Source diagnostics must not count #pragma/kernel entrypoints that the HLSL
    preprocessor cannot compile. Preserve newlines for anchored regexes.
    Unknown conditions fail closed rather than guessing Android defines.
    Potentially reachable #error directives reject compile-blocked candidates.
    """
    stack = []
    active = True
    possible = True  # Could Unity enter this branch with unknown defines?
    kept = []
    for line in clean.splitlines(keepends=True):
        match = CONDITIONAL.match(line)
        if match:
            directive, tail = match.groups()
            operand = tail.strip()
            if directive in ("if", "ifdef", "ifndef"):
                if not operand:
                    raise ValueError("Missing compute conditional expression")
                value = operand == "1" if directive == "if" and operand in ("0", "1") else None
                frame = {"parent": active, "seen": value is True,
                         "unknown": value is None, "else": False,
                         "possible_parent": possible,
                         "possible_following": possible and value is not True}
                stack.append(frame)
                active = active and value is True
                possible = possible and value is not False
            elif directive == "elif":
                if not stack or stack[-1]["else"] or not operand:
                    raise ValueError("Malformed compute #elif")
                frame = stack[-1]
                value = operand == "1" if operand in ("0", "1") else None
                if value is None:
                    frame["unknown"] = True
                active = frame["parent"] and not frame["seen"] and not frame["unknown"] and value is True
                if value is True:
                    frame["seen"] = True
                possible = frame["possible_following"] and value is not False
                frame["possible_following"] = frame["possible_following"] and value is not True
            elif directive == "else":
                if not stack or stack[-1]["else"] or operand:
                    raise ValueError("Malformed compute #else")
                frame = stack[-1]
                frame["else"] = True
                active = frame["parent"] and not frame["seen"] and not frame["unknown"]
                possible = frame["possible_following"]
            else:
                if not stack or operand:
                    raise ValueError("Malformed compute #endif")
                frame = stack.pop()
                active = frame["parent"]
                possible = frame["possible_parent"]
            kept.append("".join(c if c in "\r\n" else " " for c in line))
        else:
            if possible and ERROR_DIRECTIVE.match(line):
                # Do not disclose a possibly private compiler error message.
                raise ValueError("Potentially active compute #error directive")
            kept.append(line if active else "".join(c if c in "\r\n" else " " for c in line))
    if stack:
        raise ValueError("Unclosed compute preprocessor conditional")
    return "".join(kept)



def kernel_entrypoint_profile(source: str) -> dict:
    """Aggregate only: match each declared kernel to a bounded authored body.

    Macro-generated thread dimensions or entrypoints require independent proof.
    This intentionally conservative structural gate cannot verify compiled
    Unity kernels or the original serialized ComputeShader identity.
    """
    clean = mask_inactive_preprocessor(mask_comments_and_strings(source))
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
