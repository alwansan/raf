"""Bounded aggregate diagnostics of exported shader and input contracts; no payload output.

The counts are lexical source evidence only, NOT Unity/GPU pass or kernel validation.
"""
import argparse
from collections import Counter
from pathlib import Path
import re

# Reuse the same audited ShaderLab header/comment scanner as strict restoration.
# Do not invent a second proprietary identity matcher for the diagnostic.
from scripts.restore_builtin_shaders import COMMENT_OR_STRING, exported_shader_identity


PASS = re.compile(r'\bPass\s*\{')
PROGRAM = re.compile(r'\b(?:CGPROGRAM|HLSLPROGRAM)\b')
KERNEL = re.compile(r'(?m)^[ \t]*#[ \t]*pragma[ \t]+kernel[ \t]+[A-Za-z_][A-Za-z_0-9]*\b')
TARGET_TOKENS = ('Bloom', 'Bilateral', 'Water Spectrum', 'VolumetricLight', 'Foam/Global')


def executable_lexical_view(source):
    """Mask comments and quoted strings without changing source offsets/lines.

    This prevents quoted/commented ShaderLab tokens from being counted as live
    passes or programs. It does not prove actual shader compilation or execute
    preprocessor conditions.
    """
    def blank(match):
        return ''.join(c if c in '\r\n' else ' ' for c in match.group())

    return COMMENT_OR_STRING.sub(blank, source)


def audit(project):
    assets = project / 'Assets'
    shaders = list(assets.rglob('*.shader'))
    computes = list(assets.rglob('*.compute'))
    passes = Counter()
    targeted = []
    for path in shaders:
        source = path.read_text(errors='replace')
        live = executable_lexical_view(source)
        count = len(PASS.findall(live))
        passes[count] += 1
        # Comment-aware and exactly-one-header policy used for restoration.
        name = exported_shader_identity(source)
        if name and any(token in name for token in TARGET_TOKENS):
            targeted.append({'shader': name, 'source_passes': count,
                             'has_program_block': bool(PROGRAM.search(live))})
    kernels = Counter()
    for path in computes:
        source = path.read_text(errors='replace')
        live = executable_lexical_view(source)
        kernels[len(KERNEL.findall(live))] += 1
    print('RAFT_EXPORTED_RENDER_CONTRACT shaders=' + str(len(shaders)) +
          ' source_pass_histogram=' + str(dict(sorted(passes.items()))) +
          ' computes=' + str(len(computes)) + ' source_kernel_histogram=' + str(dict(sorted(kernels.items()))) +
          ' targeted=' + str(targeted[:16]) + ' runtimeShaderSupportVerified=false')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    audit(p.parse_args().project)
