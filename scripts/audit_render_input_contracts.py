"""Bounded aggregate diagnostics of exported shader and input contracts; no payload output."""
import argparse
from collections import Counter
from pathlib import Path
import re

def audit(project):
    shaders = list((project / 'Assets').rglob('*.shader'))
    computes = list((project / 'Assets').rglob('*.compute'))
    passes = Counter()
    targeted = []
    for path in shaders:
        text = path.read_text(errors='replace')
        count = len(re.findall(r'\bPass\s*\{', text))
        passes[count] += 1
        name = re.search(r'\bShader\s+"([^"\n]+)"', text)
        if name and any(token in name[1] for token in ('Bloom','Bilateral','Water Spectrum','VolumetricLight','Foam/Global')):
            targeted.append({'shader': name[1], 'source_passes': count,
                             'has_program_block': bool(re.search(r'CGPROGRAM|HLSLPROGRAM', text))})
    kernels = Counter()
    for path in computes:
        text = path.read_text(errors='replace')
        kernels[len(re.findall(r'^\s*#pragma\s+kernel\s+', text, re.M))] += 1
    print('RAFT_EXPORTED_RENDER_CONTRACT shaders=' + str(len(shaders)) +
          ' source_pass_histogram=' + str(dict(sorted(passes.items()))) +
          ' computes=' + str(len(computes)) + ' source_kernel_histogram=' + str(dict(sorted(kernels.items()))) +
          ' targeted=' + str(targeted[:16]) + ' runtimeShaderSupportVerified=false')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    audit(p.parse_args().project)
