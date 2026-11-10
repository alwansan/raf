"""Read separate Unity 2021.3 shader ParameterBlob records, not DXBC RDEF.

Format provenance: AssetRipper 41d464112b99132f02df99e5f46e7f4eefa79c60,
ShaderBlob/ShaderSubProgram.cs ReadParameters and ShaderSubProgramEntry.cs.
Private return values contain original identifiers and MUST NOT be published.
The safe census exposes anonymous counts only, never raw names or bytes.
"""
from __future__ import annotations
import struct
from collections import Counter
VERSION=202012090
MAX_BYTES=512*1024*1024
MAX_COUNT=65536
class Reader:
    def __init__(self,data):
        if not isinstance(data,bytes) or not 4<=len(data)<=MAX_BYTES:raise ValueError('GFX093_INPUT_BOUNDS')
        self.data=data;self.pos=0
    def i(self):
        if self.pos+4>len(self.data):raise ValueError('GFX093_TRUNCATED_INT')
        v=struct.unpack_from('<i',self.data,self.pos)[0];self.pos+=4;return v
    def count(self):
        v=self.i()
        if not 0<=v<=MAX_COUNT:raise ValueError('GFX093_COUNT_BOUNDS')
        return v
    def string(self):
        n=self.count()
        if n>4096 or self.pos+n>len(self.data):raise ValueError('GFX093_STRING_BOUNDS')
        s=self.data[self.pos:self.pos+n].decode('utf8','strict');self.pos+=n
        if '\x00' in s:raise ValueError('GFX093_STRING_NUL')
        if n:self.pos=(self.pos+3)&~3
        if self.pos>len(self.data):raise ValueError('GFX093_ALIGNMENT')
        return s

def entries_private(buffer):
    r=Reader(buffer);n=r.count()
    if n==0 or 4+n*12>len(buffer):raise ValueError('GFX093_ENTRY_TABLE_BOUNDS')
    out=[]
    for _ in range(n):
        off,length,segment=r.i(),r.i(),r.i()
        if segment!=0 or off<4+n*12 or length<4 or off>len(buffer)-length:
            raise ValueError('GFX093_ENTRY_RANGE_OR_SEGMENT')
        out.append((off,length,segment))
    # Shared equal records are allowed; partially overlapping records are not.
    ordered=sorted(set((o,o+l) for o,l,_ in out))
    if any(a[1]>b[0] for a,b in zip(ordered,ordered[1:])):raise ValueError('GFX093_ENTRY_OVERLAP')
    return out

def parameter_blob_private(raw):
    r=Reader(raw)
    if r.i()!=VERSION:raise ValueError('GFX093_UNSUPPORTED_VERSION')
    def parameter():
        name=r.string();typ,rows,cols,matrix,array,index=[r.i() for _ in range(6)]
        if (not name or not 0<=typ<=16 or not 1<=rows<=4 or not 1<=cols<=4
            or matrix not in (0,1) or not 0<=array<=MAX_COUNT or index<0 or index>MAX_BYTES):
            raise ValueError('GFX093_PARAMETER_SHAPE')
        return dict(name=name,type=typ,rows=rows,columns=cols,matrix=bool(matrix),array=array,index=index)
    n=r.count()
    if n<1:raise ValueError('GFX093_NO_GLOBAL_GROUP')
    groups=[]
    for _ in range(n):
        name=r.string();used=r.i();count=r.count()
        if not 0<=used<=MAX_BYTES:raise ValueError('GFX093_GROUP_SIZE')
        params=[parameter() for _ in range(count)];structs=[]
        for _ in range(r.count()):
            sname=r.string();index,array,size=r.i(),r.i(),r.i()
            if not sname or min(index,array,size)<0:raise ValueError('GFX093_STRUCT_BOUNDS')
            structs.append(dict(name=sname,index=index,array=array,size=size,
                                parameters=[parameter() for _ in range(r.count())]))
        groups.append(dict(name=name,used=used,parameters=params,structs=structs))
    bindings=[]
    for _ in range(r.count()):
        name=r.string();typ,index,extra=r.i(),r.i(),r.i()
        if typ not in (0,1,2,3,4) or index<0 or index>65535:raise ValueError('GFX093_BINDING_SHAPE')
        texture_flags=r.i() if typ==0 else None
        if typ==0 and (extra < -1 or extra>65535 or texture_flags<0):raise ValueError('GFX093_TEXTURE_SHAPE')
        bindings.append(dict(name=name,type=typ,index=index,extra=extra,texture_flags=texture_flags))
    if r.pos!=len(raw):raise ValueError('GFX093_PARAMETER_BLOB_TRAILING_BYTES')
    return dict(groups=groups,bindings=bindings)

def linked_parameters_private(tree,buffer):
    table=entries_private(buffer);out=[]
    cache={}
    for sub in tree['m_ParsedForm']['m_SubShaders']:
        for pp in sub['m_Passes']:
            for stage in ('progVertex','progFragment'):
                p=pp[stage];buckets=p['m_PlayerSubPrograms'];indices=p['m_ParameterBlobIndices']
                if len(indices)!=len(buckets):raise ValueError('GFX093_BUCKET_COUNT')
                for rows,refs in zip(buckets,indices):
                    if len(rows)!=len(refs):raise ValueError('GFX093_LINK_COUNT')
                    for row,ref in zip(rows,refs):
                        if type(ref)!=int or not 0<=ref<len(table):raise ValueError('GFX093_PARAM_INDEX')
                        code=row['m_BlobIndex']
                        if type(code)!=int or not 0<=code<len(table):raise ValueError('GFX093_CODE_INDEX')
                        if ref not in cache:
                            off,length,_=table[ref];cache[ref]=parameter_blob_private(buffer[off:off+length])
                        out.append((pp,stage,row,ref,cache[ref]))
    return out,cache

def safe_census(tree,buffer):
    linked,cache=linked_parameters_private(tree,buffer);c=Counter()
    props={p['m_Name'] for p in tree['m_ParsedForm']['m_PropInfo']['m_Props']}
    for pp,stage,row,ref,params in linked:
        c['linked_stage_parameter_rows']+=1
        c['vertex_rows' if stage=='progVertex' else 'fragment_rows']+=1
        tex=[b for b in params['bindings'] if b['type']==0]
        cb=[b for b in params['bindings'] if b['type']==1]
        c['texture_bindings']+=len(tex);c['CB_bindings']+=len(cb)
        c['texture_binding_name_matches_declared_property']+=sum(b['name'] in props for b in tex)
        cbmap={b['name']:b['index'] for b in cb}
        if len(cbmap)!=len(cb):raise ValueError('GFX093_DUPLICATE_CB_NAME')
        for group in params['groups'][1:]:
            c['CB_groups']+=1
            if group['name'] in cbmap:
                c['CB_group_name_to_original_b_binding']+=1
                c['property_to_CB_member_byte_candidates']+=sum(p['name'] in props for p in group['parameters'])
            c['struct_groups']+=len(group['structs'])
    return dict(experiment='GFX-MULTI-093',safe_counts=dict(c),unique_parameter_blobs=len(cache),
                originalShaderRestored=False,phase_closed=False,
                GPU_pixels_proven=False,parameter_indices_existed_but_prior_RDEF_gate_did_not_audit_them=True)

def common_parameters_private(pp,stage):
    from gfxlab.tools.multi_shader_material_texenv_bridge import pass_name_table
    names=pass_name_table(pp['m_NameIndices']);c=pp[stage]['m_CommonParameters']
    def name(item):
        ix=item['m_NameIndex']
        if ix not in names:raise ValueError('GFX093_COMMON_NAME_INDEX')
        return names[ix]
    groups=[];bindings=[]
    for cb in c['m_ConstantBuffers']:
        members=[]
        for v in cb['m_VectorParams']:
            members.append(dict(name=name(v),type=v['m_Type'],rows=1,columns=v['m_Dim'],
                        matrix=False,array=v['m_ArraySize'],index=v['m_Index']))
        for v in cb['m_MatrixParams']:
            members.append(dict(name=name(v),type=v['m_Type'],rows=v['m_RowCount'],columns=4,
                        matrix=True,array=v['m_ArraySize'],index=v['m_Index']))
        groups.append(dict(name=name(cb),used=cb['m_Size'],parameters=members,structs=cb['m_StructParams']))
    for b in c['m_ConstantBufferBindings']:
        bindings.append(dict(name=name(b),type=1,index=b['m_Index'],extra=0,texture_flags=None))
    for b in c['m_TextureParams']:
        bindings.append(dict(name=name(b),type=0,index=b['m_Index'],extra=b['m_SamplerIndex'],
                             texture_flags=(b['m_Dim']<<1)|int(b['m_MultiSampled'])))
    return dict(groups=groups,bindings=bindings)

def merged_parameters_private(pp,stage,params):
    common=common_parameters_private(pp,stage)
    bindings={}
    for b in common['bindings']+params['bindings']:
        key=(b['type'],b['name'])
        if key in bindings and bindings[key]!=b:raise ValueError('GFX093_COMMON_VARIANT_BINDING_CONFLICT')
        bindings[key]=b
    groups={}
    for g in common['groups']+params['groups'][1:]:
        if g['name'] not in groups:
            groups[g['name']]=dict(name=g['name'],used=g['used'],parameters={},structs=[],declared_sizes=set())
        dest=groups[g['name']]
        dest['declared_sizes'].add(g['used'])
        dest['used']=max(dest['declared_sizes']) # Envelope only; actual DXBC declaration remains authoritative.
        for p in g['parameters']:
            if p['name'] in dest['parameters'] and dest['parameters'][p['name']]!=p:
                raise ValueError('GFX093_COMMON_CB_MEMBER_CONFLICT')
            dest['parameters'][p['name']]=p
        dest['structs'].extend(g['structs'])
    return dict(groups=list(groups.values()),bindings=list(bindings.values()))

def safe_merged_census(tree,buffer,programs):
    from gfxlab.tools.multi_shader_one_pass_spirv import code_from_ref
    from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
    from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
    linked,cache=linked_parameters_private(tree,buffer);c=Counter()
    props={p['m_Name'] for p in tree['m_ParsedForm']['m_PropInfo']['m_Props']}
    for pp,stage,row,ref,param in linked:
        c['linked_rows']+=1
        merged=merged_parameters_private(pp,stage,param)
        dx=code_from_ref(row,programs,'Vertex' if stage=='progVertex' else 'Pixel')
        source,source_sizes=private_source_slots(source_shader_chunk(dx))
        tex={b['name']:b for b in merged['bindings'] if b['type']==0}
        cb={b['name']:b for b in merged['bindings'] if b['type']==1}
        c['merged_texture_bindings']+=len(tex);c['merged_CB_bindings']+=len(cb)
        # An unused declared texture may be serialized but optimized away; count
        # a source-authenticated edge only if both register declarations exist.
        for name,b in tex.items():
            if b['index'] in source['resource'] and (b['extra']==-1 or b['extra'] in source['sampler']):
                c['texture_binding_declaration_witness']+=1
                if name in props:c['property_to_source_t_sampler_witness']+=1
            else:c['texture_binding_not_in_actual_source_declarations']+=1
        for g in merged['groups']:
            if g['name'] not in cb:continue
            slot=cb[g['name']]['index']
            if slot not in source['constant_buffer']:
                c['CB_binding_not_in_actual_source_declarations']+=1;continue
            c['CB_group_binding_source_b_witness']+=1
            c['CB_common_variant_size_disagreement']+=int(len(g['declared_sizes'])>1)
            for member in g['parameters'].values():
                # Offset is original byte index, not inferred from member order.
                if member['index']<0 or member['index']>=g['used']:
                    raise ValueError('GFX093_MEMBER_BYTE_INDEX_OUT_OF_CB')
                if member['name'] in props:
                    if member['index']<source_sizes[slot]*16:
                        c['property_to_source_b_member_byte_witness']+=1
                    else:c['property_member_outside_actual_declared_CB']+=1
    return dict(experiment='GFX-MULTI-093',source_zip2_sha='15964ea8f246b6e076ce26b60931ee2e1a9a2385',
                safe_counts=dict(c),unique_parameter_blobs=len(cache),
                previous_missing_parameter_claim_superseded=True,
                actual_material_values_uploaded_to_GPU=False,
                originalShaderRestored=False,phase_closed=False)

def load_original_shader_private(stage):
    from gfxlab.tools.multi_model_transport import all_model_entries
    from UnityPy.helpers import CompressionHelper
    from gfxlab.tools.multi_shader_compiled_platform import scalar_first
    from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs
    entries,types,_=all_model_entries(stage)
    ids={(m['shader_owner'],m['shader_pid']) for e in entries for m in e['materials']}
    if len(ids)!=1:raise ValueError('GFX093_SHADER_IDENTITY')
    owner,pid=next(iter(ids));obj=types[owner][pid]
    tree=obj.read_typetree(check_read=False);shader=obj.read()
    if len(shader.platforms)!=1 or any(len(x)!=1 for x in (shader.offsets,shader.compressedLengths,shader.decompressedLengths)):
        raise ValueError('GFX093_PLATFORM_COUNT')
    for rows in (shader.offsets,shader.compressedLengths,shader.decompressedLengths):
        if isinstance(rows[0],list) and len(rows[0])!=1:raise ValueError('GFX093_MULTISEGMENT_UNSUPPORTED')
    off=scalar_first(shader.offsets[0]);n=scalar_first(shader.compressedLengths[0]);size=scalar_first(shader.decompressedLengths[0])
    data=bytes(shader.compressedBlob)
    if not 0<=off<=len(data)-n or not 0<n<=len(data) or not 0<size<=MAX_BYTES:
        raise ValueError('GFX093_COMPRESSED_BOUNDS')
    buffer=CompressionHelper.decompress_lz4(data[off:off+n],size)
    if len(buffer)!=size:raise ValueError('GFX093_DECOMPRESSED_SIZE')
    return tree,buffer,compiled_programs(obj)

def main():
    import argparse,json
    from pathlib import Path
    from gfxlab.tools.original_model_probe import stage_originals
    p=argparse.ArgumentParser();p.add_argument('--zip2',type=Path,required=True)
    p.add_argument('--stage',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();tree,buffer,programs=load_original_shader_private(stage_originals(a.zip2,a.stage))
    result=safe_merged_census(tree,buffer,programs)
    linked,cache=linked_parameters_private(tree,buffer)
    codes={row['m_BlobIndex'] for _,_,row,_,_ in linked};params=set(cache)
    if codes&params or len(codes)!=1275 or len(params)!=381 or len(codes|params)!=1656:
        raise ValueError('GFX093_CODE_PARAMETER_PARTITION')
    result.update(original_code_entries=len(codes),original_parameter_entries=len(params),
        fake_unreferenced_GPU_program_interpretation_superseded=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
