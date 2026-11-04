"""Fail-closed ShaderLab per-pass structural coverage; never authenticity proof.

Only numeric counts and booleans are returned. No shader source or names leak.
An executable program requires a matching CGPROGRAM/ENDCG or
HLSLPROGRAM/ENDHLSL pair *within the same authored Pass*.
"""
import re

LEXICAL = re.compile(r'//[^\r\n]*|/\*[\s\S]*?(?:\*/|$)|"(?:\\.|[^"\\])*"')
SHADER_OPEN = re.compile(r'\bShader\s+"(?:\\.|[^"\\])*"\s*\{')
TAG_OPEN = re.compile(r'\b(SubShader|Pass)\s*\{')
PROGRAM_START = re.compile(r'\b(?:CGPROGRAM|HLSLPROGRAM)\b')
PROGRAM_END = re.compile(r'\b(?:ENDCG|ENDHLSL)\b')


def _blank(token):
    return ''.join(c if c in '\r\n' else ' ' for c in token)


def remove_comments(source):
    """Keep quoted ShaderLab names and all source offsets; blank comments."""
    return LEXICAL.sub(lambda m: m.group() if m.group().startswith('"')
                       else _blank(m.group()), source)


def mask_quoted_strings(source):
    """Erase comments and string literals, preserving source length/newlines."""
    return LEXICAL.sub(lambda m: _blank(m.group()), source)


def pass_coverage(source):
    """Count authored Pass programs only inside Shader -> SubShader scopes.

    Earlier global Pass matching could count a fake Pass under Properties or
    outside a Shader root and report misleading structural readiness. Mask
    quoted literals/comments before parsing braces. A true Pass must be an
    immediate child of a SubShader which is an immediate child of a Shader.
    Structural validity still does not authenticate original bytecode/pixels.
    """
    clean = remove_comments(source)
    masked = mask_quoted_strings(source)
    open_kinds = {}
    for match in SHADER_OPEN.finditer(clean):
        open_kinds[match.end() - 1] = "shader"
    for match in TAG_OPEN.finditer(masked):
        open_kinds[match.end() - 1] = match.group(1).lower()

    stack = []
    bodies = []
    subshader_bodies = []
    balanced = True
    for index, char in enumerate(masked):
        if char == "{":
            kind = open_kinds.get(index, "other")
            parent = stack[-1][0] if stack else None
            if (kind == "shader" and parent is not None or
                    kind == "subshader" and parent != "shader" or
                    kind == "pass" and parent != "subshader"):
                kind = "other"
            stack.append([kind, index + 1, []])
        elif char == "}":
            if not stack:
                balanced = False
                continue
            kind, start, contained = stack.pop()
            if kind == "pass":
                body = masked[start:index]
                bodies.append(body)
                # A runtime-selected SubShader owns its passes. Summing the
                # passes of alternate SubShaders is NOT a valid passCount.
                if stack and stack[-1][0] == "subshader":
                    stack[-1][2].append(body)
            elif kind == "subshader":
                subshader_bodies.append(contained)
    if stack:
        balanced = False

    def programmed(body):
        starts = list(PROGRAM_START.finditer(body))
        ends = list(PROGRAM_END.finditer(body))
        if len(starts) != len(ends) or len(starts) != 1:
            return False
        start, end = starts[0], ends[0]
        correct = ((start.group() == "CGPROGRAM" and end.group() == "ENDCG")
                   or (start.group() == "HLSLPROGRAM" and end.group() == "ENDHLSL"))
        return bool(correct and start.end() < end.start()
                    and body[start.end():end.start()].strip())

    count = len(bodies)
    authored = sum(programmed(body) for body in bodies)
    per_subshader_count = [len(group) for group in subshader_bodies]
    per_subshader_programmed = [
        sum(programmed(body) for body in group) for group in subshader_bodies
    ]
    return {
        "pass_count": count,  # diagnostic aggregate only; not Shader.passCount
        "passes_with_complete_program": authored,
        "all_passes_programmed": balanced and count > 0 and authored == count,
        "pass_braces_balanced": balanced,
        "subshader_pass_counts": per_subshader_count,
        "subshader_programmed_pass_counts": per_subshader_programmed,
        "all_subshaders_programmed": (
            balanced and bool(per_subshader_count)
            and all(count > 0 and count == ready for count, ready in
                    zip(per_subshader_count, per_subshader_programmed))
        ),
        "active_subshader_runtime_verified": False,
    }
