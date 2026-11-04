"""Fail-closed ShaderLab per-pass structural coverage; never authenticity proof.

Only numeric counts and booleans are returned. No shader source or names leak.
An executable program requires a matching CGPROGRAM/ENDCG or
HLSLPROGRAM/ENDHLSL pair *within the same authored Pass*.
"""
import re

LEXICAL = re.compile(r'//[^\r\n]*|/\*[\s\S]*?(?:\*/|$)|"(?:\\.|[^"\\])*"')
PASS_OPEN = re.compile(r'\bPass\s*\{')
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
    """Count complete per-pass programs, not a shader-global program marker."""
    masked = mask_quoted_strings(source)
    count = 0
    authored = 0
    balanced = True
    last_end = -1
    for match in PASS_OPEN.finditer(masked):
        if match.start() < last_end:
            continue  # A nested Pass-like token is not another ShaderLab pass.
        count += 1
        cursor = match.end()
        depth = 1
        while cursor < len(masked) and depth:
            if masked[cursor] == '{':
                depth += 1
            elif masked[cursor] == '}':
                depth -= 1
            cursor += 1
        if depth:
            balanced = False
            continue
        body = masked[match.end():cursor - 1]
        starts = list(PROGRAM_START.finditer(body))
        ends = list(PROGRAM_END.finditer(body))
        valid = False
        if len(starts) == len(ends) == 1:
            start, end = starts[0], ends[0]
            correct = ((start.group() == 'CGPROGRAM' and end.group() == 'ENDCG')
                       or (start.group() == 'HLSLPROGRAM' and end.group() == 'ENDHLSL'))
            valid = correct and start.end() < end.start() and bool(
                body[start.end():end.start()].strip())
        authored += bool(valid)
        last_end = cursor
    return {
        'pass_count': count,
        'passes_with_complete_program': authored,
        'all_passes_programmed': balanced and count > 0 and authored == count,
        'pass_braces_balanced': balanced,
    }
