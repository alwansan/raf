"""Recover pinned BSD volumetric shaders and Raft's half-resolution composition pass.

Passes 0-11 are authenticated upstream programs, not reconstructed PC bytecode.
Raft's extra pass 12 composes upstream pass 5 and BlitAdd's transmittance blend.
Never replace a pass with an unlit placeholder or silently clamp a caller's index.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.request
from scripts.restore_tmp_shaders import DECL, restore

REPO = 'SlightlyMad/VolumetricLights'
COMMIT = 'd20b6f9a47ae857e1d313b147db2df3ef44b9196'
EXPECTED = {
    'Assets/Shaders/BilateralBlur.shader': ('Hidden/BilateralBlur', 12),
    'Assets/Shaders/BlitAdd.shader': ('Hidden/BlitAdd', 1),
    'Assets/Shaders/VolumetricLight.shader': ('Sandbox/VolumetricLight', 5),
}
ROOT = 'Assets/RaftAndroid/VolumetricShaders/'
NOTICE = 'Assets/StreamingAssets/RaftAndroidNotices/volumetric-lights-BSD-3-Clause.txt'
PASS12 = '''
        // Android port compatibility: Raft's half-resolution combined pass 12.
        // Derived from upstream bilateral pass 5 and Hidden/BlitAdd pass 0.
        // Keep transmittance (alpha) multiplication before scattering addition.
        Pass
        {
            Blend One Zero
            CGPROGRAM
            #pragma vertex vertUpsampleCombined
            #pragma fragment fragCombined
            #pragma target 4.0
            sampler2D _Source;
            float4 _Source_TexelSize;
            v2fUpsample vertUpsampleCombined(appdata v)
            {
                return vertUpsample(v, _HalfResDepthBuffer_TexelSize);
            }
            float4 fragCombined(v2fUpsample input) : SV_Target
            {
                float4 main = BilateralUpsample(input, _CameraDepthTexture,
                    _HalfResDepthBuffer, _HalfResColor,
                    sampler_HalfResColor, sampler_HalfResDepthBuffer);
                float2 uv = input.uv;
                #if UNITY_UV_STARTS_AT_TOP
                if (_Source_TexelSize.y < 0) uv.y = 1 - uv.y;
                #endif
                float4 source = tex2D(_Source, uv);
                source *= main.w;
                source.xyz += main.xyz;
                return source;
            }
            ENDCG
        }
'''


def pass_count(text):
    return len(re.findall(r'\bPass\s*\{', text))


def combined_half_pass(bilateral, blit):
    if pass_count(bilateral) != 12 or pass_count(blit) != 1:
        raise ValueError('Upstream volumetric pass order changed')
    for token in ('v2fUpsample', 'BilateralUpsample', 'sampler_HalfResColor', 'sampler_HalfResDepthBuffer'):
        if token not in bilateral:
            raise ValueError('Missing bilateral composition dependency')
    if 'source *= main.w;' not in blit or 'source.xyz += main.xyz;' not in blit:
        raise ValueError('Upstream transmittance composition changed')
    # Insert only after upstream's last pass, before SubShader/Shader closing braces.
    match = re.search(r'\n\s*}\s*}\s*$', bilateral)
    if not match:
        raise ValueError('Unexpected bilateral shader structure')
    result = bilateral[:match.start()] + '\n' + PASS12 + bilateral[match.start():]
    if pass_count(result) != 13:
        raise ValueError('Missing half-resolution composition pass')
    return result


def sources(manifest, read):
    if manifest['repository'] != REPO or manifest['commit'] != COMMIT:
        raise ValueError('Unexpected volumetric source identity')
    rows = manifest['files']
    if len(rows) != 4 or {r['path'] for r in rows} != set(EXPECTED) | {'LICENSE'}:
        raise ValueError('Incomplete or unsafe volumetric source paths')
    for row in rows:
        if not 0 < row['bytes'] <= 64 * 1024 or not re.fullmatch('[a-f0-9]{40}', row['git_blob']):
            raise ValueError('Invalid volumetric source bounds')

    def verified(row):
        raw = read(row['path'])
        digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if len(raw) != row['bytes'] or digest != row['git_blob']:
            raise ValueError('Volumetric vendor source fingerprint mismatch')
        return row['path'], raw

    with ThreadPoolExecutor(max_workers=4) as pool:
        raw = dict(pool.map(verified, rows))
    shaders = {}
    for path, (name, count) in EXPECTED.items():
        text = raw[path].decode('utf-8-sig')
        match = DECL.search(text)
        if not match or match[1] != name or pass_count(text) != count:
            raise ValueError('Volumetric shader identity/pass contract changed')
        shaders[name] = text
    shaders['Hidden/BilateralBlur'] = combined_half_pass(shaders['Hidden/BilateralBlur'], shaders['Hidden/BlitAdd'])
    print('RAFT_VOLUMETRIC_SOURCES authenticatedShaders=3 originalPasses=12,1,5 combinedHalfPass=12 outputBilateralPasses=13 deviceExecution=false')
    return shaders, raw['LICENSE']


def download(path):
    url = 'https://raw.githubusercontent.com/' + REPO + '/' + COMMIT + '/' + path
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                raw = response.read(64 * 1024 + 1)
            if len(raw) > 64 * 1024:
                raise ValueError('Over-limit volumetric vendor source')
            return raw
        except OSError:
            if attempt == 2:
                raise
            time.sleep(1)


def restore_project(project, backup, shaders, license):
    # This legally required notice is a dependency of the restored volumetric
    # effects and must be committed and rolled back WITH their Shader files.
    # A separate post-restoration write could fail after the shaders changed,
    # or follow a redirected StreamingAssets parent outside the Unity export.
    return restore(project, backup, shaders, {}, license,
        shader_prefix=tuple(EXPECTED[p][0] for p in EXPECTED), include_root=ROOT,
        label='VOLUMETRIC', vendor_version=COMMIT + '+raft-half-compose-v1',
        extra_additions={NOTICE: license})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path)
    p.add_argument('--backup', type=Path)
    p.add_argument('--verify-only', action='store_true')
    p.add_argument('--manifest', type=Path, default=Path('config/volumetric-shader-sources.json'))
    args = p.parse_args()
    shaders, license = sources(json.loads(args.manifest.read_text()), download)
    if args.verify_only:
        return
    if not args.project or not args.backup:
        raise ValueError('Project and external backup required')
    restore_project(args.project, args.backup, shaders, license)


if __name__ == '__main__':
    main()
