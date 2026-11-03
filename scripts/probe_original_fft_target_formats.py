"""Source-pinned FFT temporary target formats; not actual GPU format equivalence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from scripts.instrument_android_runtime_operations import body_bounds
SHA='2f866cbe58836da8260461fe6406793f35d868eba94e816e593209544b4ba704'

def analyze(source,expected=SHA):
    if len(source)>100000 or hashlib.sha256(source.encode()).hexdigest()!=expected:
        raise ValueError('Original FFT target source fingerprint mismatch')
    a,b=body_bounds(source,'private void RetrieveRenderTexturesSet()')
    code=re.sub(r'\s+','',source[a:b])
    required=['if(_TwoChannels){format=(_HighPrecision?RenderTextureFormat.ARGBFloat:RenderTextureFormat.ARGBHalf);}',
              'else{format=(_HighPrecision?RenderTextureFormat.RGFloat:RenderTextureFormat.RGHalf);}',
              '_RenderTexturesSet=RenderTexturesCache.GetCache(_Resolution<<1,_Resolution<<1,0,format,linear:true,_UsesUav);']
    if any(code.count(x)!=1 for x in required):raise ValueError('Original FFT format/size contract changed')
    return {'source_sha256':expected,'temporary_cache_width_multiplier':2,'temporary_cache_height_multiplier':2,
            'linear':True,'random_write_forwarded_from_original_constructor':True,
            'formats':[{'two_channels':two,'high_precision':high,'render_texture_format':fmt}
              for two,high,fmt in [(False,False,'RGHalf'),(False,True,'RGFloat'),(True,False,'ARGBHalf'),(True,True,'ARGBFloat')]],
            'actual_created_image_format_verified':False,'spirv_rgba32f_equivalence_verified':False,'unity_or_gpu_executed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);a=p.parse_args()
    paths=list(a.source.rglob('GpuFFT.cs'))
    if len(paths)!=1 or paths[0].is_symlink():raise ValueError('Original FFT source unavailable/ambiguous')
    print('RAFT_ORIGINAL_FFT_TARGET_FORMATS '+json.dumps(analyze(paths[0].read_text(encoding='utf-8-sig').replace('\r\n','\n')),sort_keys=True))
