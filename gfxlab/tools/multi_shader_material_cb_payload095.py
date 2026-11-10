"""Private original saved Material float/color -> authenticated CB byte writes.

Produces partial known-byte masks. Unknown engine globals stay UNKNOWN and
must never be uploaded as fabricated zero values or treated as complete CBs.
Names, values, registers and byte payloads must remain private.
"""
import struct,math
from collections import Counter
from gfxlab.tools.multi_shader_parameter_blob093 import linked_parameters_private,merged_parameters_private
from gfxlab.tools.multi_shader_one_pass_spirv import code_from_ref
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_material_texture_semantics import named_entries

def saved_values_private(material):
    saved=material['m_SavedProperties'];out={}
    for name,value in named_entries(saved.get('m_Floats',[])):
        if type(value) not in (float,int) or not math.isfinite(value):raise ValueError('GFX095_BAD_SAVED_FLOAT')
        out[name]=('float',(float(value),))
    for name,value in named_entries(saved.get('m_Colors',[])):
        if name in out:raise ValueError('GFX095_DUPLICATE_SAVED_PROPERTY')
        if not isinstance(value,dict) or not all(k in value for k in ('r','g','b','a')):raise ValueError('GFX095_BAD_SAVED_COLOR')
        vals=tuple(value[k] for k in ('r','g','b','a'))
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in vals):raise ValueError('GFX095_BAD_COLOR_VALUE')
        out[name]=('color',vals)
    return out

def partial_payload_private(merged,source_sizes,saved,declared_props):
    bindings={b['name']:b['index'] for b in merged['bindings'] if b['type']==1}
    if len(bindings)!=sum(b['type']==1 for b in merged['bindings']):raise ValueError('GFX095_DUPLICATE_BINDING')
    buffers={};stats=Counter()
    for group in merged['groups']:
        slot=bindings.get(group['name'])
        if slot not in source_sizes:continue
        size=source_sizes[slot]*16
        if size<=0 or size>1024*1024:raise ValueError('GFX095_CB_SIZE')
        if slot not in buffers:buffers[slot]=(bytearray(size),bytearray(size))
        payload,known=buffers[slot]
        for member in group['parameters'].values():
            name=member['name']
            if name not in saved:
                stats['member_without_direct_saved_material_value']+=1;continue
            kind,vals=saved[name];prop_type=declared_props.get(name)
            if prop_type is None:raise ValueError('GFX095_SAVED_MEMBER_NOT_SHADER_PROPERTY')
            if ((kind=='float' and prop_type not in (2,3)) or
                (kind=='color' and prop_type not in (0,1))):raise ValueError('GFX095_PROPERTY_TYPE_MISMATCH')
            if member['type']!=0 or member['matrix'] or member['array'] not in (0,1):
                stats['saved_member_type_or_array_not_supported']+=1;continue
            n=member['columns']
            if not 1<=n<=4 or len(vals)<n or (kind=='float' and n!=1):raise ValueError('GFX095_VECTOR_DIMENSION_MISMATCH')
            offset=member['index'];raw=struct.pack('<%df'%n,*vals[:n])
            if offset<0 or offset%4 or offset+len(raw)>size:raise ValueError('GFX095_WRITE_OUTSIDE_SOURCE_CB')
            for i,b in enumerate(raw,offset):
                if known[i] and payload[i]!=b:raise ValueError('GFX095_CONFLICTING_BYTE_WRITES')
                known[i]=1;payload[i]=b
            if payload[offset:offset+len(raw)]!=raw:raise ValueError('GFX095_WRITE_READBACK')
            stats['saved_float_member_writes' if kind=='float' else 'saved_color_member_writes']+=1
            stats['written_members_bitwise_float32_readback_equal']+=1
    stats['source_CB_blocks_with_partial_material_bytes']=sum(any(known) for _,known in buffers.values())
    stats['known_material_byte_count']=sum(sum(mask) for _,mask in buffers.values())
    stats['unknown_runtime_byte_count']=sum(len(mask)-sum(mask) for _,mask in buffers.values())
    return buffers,stats

def original_materials_private(stage):
    from gfxlab.tools.multi_source_select import selected_five
    from gfxlab.tools.shears_texture_readiness import select_exact_renderer
    from gfxlab.tools.shears_provenance_probe import resolve_pptr
    private,_=selected_five(stage)
    envs,types,owner,renderer=select_exact_renderer(stage)
    keys=[resolve_pptr(renderer['m_Materials'][0],owner,[e.path for e in envs[owner].file.externals])[1]]
    keys += [(m['owner'],m['material_pid']) for e in private['selected'] for m in e['materials']]
    if len(keys)!=7 or len(set(keys))!=6:raise ValueError('GFX095_MATERIAL_GRAPH')
    return [types[o][pid].read_typetree(check_read=False) for o,pid in keys]

def safe_material_payload_census(stage,tree,buffer,programs):
    materials=original_materials_private(stage)
    props={p['m_Name']:p['m_Type'] for p in tree['m_ParsedForm']['m_PropInfo']['m_Props']}
    saved=[saved_values_private(m) for m in materials];total=Counter()
    linked,_=linked_parameters_private(tree,buffer)
    for pp,st,row,ref,param in linked:
        dx=code_from_ref(row,programs,'Vertex' if st=='progVertex' else 'Pixel')
        _,sizes=private_source_slots(source_shader_chunk(dx));merged=merged_parameters_private(pp,st,param)
        for values in saved:
            _,counts=partial_payload_private(merged,sizes,values,props);total.update(counts)
    return dict(experiment='GFX-MULTI-095',source_material_slots=7,unique_source_materials=6,
         source_stage_parameter_rows=len(linked),safe_counts=dict(total),
         uploaded_original_material_bytes_to_GPU=False,complete_runtime_CB_payloads=False,
         source_Shader48_GPU_pixel_parity=False,originalShaderRestored=False,phase_closed=False)

def main():
    import argparse,json
    from pathlib import Path
    from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
    from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
    p=argparse.ArgumentParser();p.add_argument('--zip2',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();stage=stage_originals(a.zip2,a.stage);tree,buffer,programs=load_original_shader_private(stage)
    d=safe_material_payload_census(stage,tree,buffer,programs);d['source_sha']=ZIP2_SHA
    a.out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
