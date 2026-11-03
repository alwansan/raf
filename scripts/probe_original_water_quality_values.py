"""Decode a SHA-pinned original water-quality object with source-corroborated schema.

This is NOT a recovered Unity TypeTree or proof of the active phone quality.
Only numerical values/hashes are emitted, never names or original binary/source.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

OBJECT_SHA='c8ee04ce0ad9965caa4a2862d4d305501ddae5a1c596ce78bb89be390970b15b'
SOURCE_PINS={
 'WaterQualitySettings.cs':'7d2475ac614043815e41e67537de9eed89954a9b8e0a7c74a7d2cf870594b6c7',
 'WaterQualityLevel.cs':'d26755c7776b620c3a5de52b80c2e7fca2744316d6021cf706ea4f39459dd546',
 'WaterRipplesData.cs':'9c904166866c8603f10eab83dcae6dea911b0cc54e21965937842bfbbb36827f',
 'WaterWavesMode.cs':'e367c4322fec633a05c6ce4e9152de3e387a2d5ce44749caf6d77972f5e88134',
}

class Reader:
    def __init__(self,data):self.data=data;self.pos=0
    def read(self,fmt):
        length=struct.calcsize('<'+fmt)
        if self.pos+length>len(self.data):raise ValueError('Truncated original quality field')
        values=struct.unpack_from('<'+fmt,self.data,self.pos);self.pos+=length
        return values[0] if len(values)==1 else values
    def align(self):
        end=(self.pos+3)&~3
        if end>len(self.data) or any(self.data[self.pos:end]):raise ValueError('Original quality alignment changed')
        self.pos=end
    def boolean(self):
        value=self.read('B')
        if value not in (0,1):raise ValueError('Original quality boolean is invalid')
        self.align();return bool(value)
    def name_hash(self):
        length=self.read('i')
        if not 0<=length<=256 or self.pos+length>len(self.data):raise ValueError('Original quality name length invalid')
        data=self.data[self.pos:self.pos+length];data.decode('utf8');self.pos+=length;self.align()
        return hashlib.sha256(data).hexdigest()
    def finite(self,low,high):
        value=self.read('f')
        if not math.isfinite(value) or not low<=value<=high:raise ValueError('Original quality float is invalid')
        return value


def decode(raw,expected_sha):
    if not isinstance(raw,bytes) or not 80<=len(raw)<=65536 or hashlib.sha256(raw).hexdigest()!=expected_sha:
        raise ValueError('Original quality object fingerprint mismatch')
    r=Reader(raw)
    if r.read('iq')!=(0,0) or not r.boolean() or r.read('iq')!=(1,838):
        raise ValueError('Original quality script/header changed')
    asset_name=r.name_hash()
    # Six serialized fields in authenticated WaterRipplesData: mask, iterations,
    # three texture-format enums and shader-mode enum. It is inline, not a PPtr.
    ripples=r.read('6i')
    if not 0<=ripples[1]<=1024 or ripples[5] not in (0,1):raise ValueError('Original ripple fields invalid')
    count=r.read('i')
    if not 1<=count<=16:raise ValueError('Original quality count invalid')
    levels=[]
    for index in range(count):
        start=r.pos;name=r.name_hash();cap=r.read('i')
        if not 1<=cap<=16384:raise ValueError('Original spectrum limit invalid')
        high_precision=r.boolean();high_normals=r.boolean();tile=r.finite(0,10);waves=r.read('i')
        if waves not in (0,1,2,3):raise ValueError('Original waves enum invalid')
        spray=r.boolean();foam=r.finite(0,1);tess=r.finite(0,1);vertices=r.read('i');tess_vertices=r.read('i');alpha=r.boolean()
        if not 0<=vertices<=10000000 or not 0<=tess_vertices<=10000000:raise ValueError('Original vertex limit invalid')
        levels.append({'index':index,'name_sha256':name,'offset':start,'bytes':r.pos-start,
            'spectrum_limit':cap,'spectrum_limit_is_power_of_two':cap&(cap-1)==0,
            'high_precision':high_precision,'high_quality_normals':high_normals,
            'tile_scale':tile,'waves_mode':waves,'spray':spray,'foam_quality':foam,
            'tessellation_factor':tess,'vertex_limit':vertices,'tessellated_vertex_limit':tess_vertices,'alpha_blending':alpha})
    sync=r.boolean();saved=r.read('i')
    if not 0<=saved<count or r.pos!=len(raw):raise ValueError('Original quality tail/length invalid')
    return {'object_sha256':expected_sha,'bytes_consumed':r.pos,'asset_name_sha256':asset_name,
        'inline_ripple_field_count':6,'ripple_iterations':ripples[1],'ripple_shader_mode':ripples[5],
        'quality_levels':levels,'synchronize_with_unity':sync,'saved_custom_quality_index':saved,
        'source_corroborated_layout_only':True,'original_full_typetree_verified':False,
        'active_phone_quality_or_requested_water_resolution_verified':False,
        'runtime_kernel_mapping_or_gpu_output_verified':False,'original_data_modified':False}


def inspect(raw_path,managed):
    if raw_path.is_symlink() or not raw_path.is_file() or raw_path.stat().st_size!=476:
        raise ValueError('Original quality object missing or unsafe')
    for basename,expected in SOURCE_PINS.items():
        paths=list(managed.rglob(basename))
        if len(paths)!=1 or paths[0].is_symlink() or not paths[0].is_file() or paths[0].stat().st_size>500000:
            raise ValueError('Original quality schema source missing or ambiguous')
        source=paths[0].read_text(encoding='utf-8-sig').replace('\r\n','\n')
        if hashlib.sha256(source.encode()).hexdigest()!=expected:raise ValueError('Original quality schema source fingerprint mismatch')
    result=decode(raw_path.read_bytes(),OBJECT_SHA)
    result['schema_source_sha256']=SOURCE_PINS
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--object',type=Path,required=True);p.add_argument('--managed-source',type=Path,required=True)
    a=p.parse_args();print('RAFT_ORIGINAL_WATER_QUALITY_VALUES '+json.dumps(inspect(a.object,a.managed_source),sort_keys=True))
