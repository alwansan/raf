"""Private named source binding plan; returned names MUST NOT be logged/uploaded."""
import hashlib
import json

def build(common, name_indices):
    names={}
    for name,index in name_indices:
        if type(index) is not int or index in names or not isinstance(name,str) or not name or "\0" in name:
            raise ValueError("ambiguous source name table")
        names[index]=name
    def resolve(index):
        if type(index) is not int or index not in names:raise ValueError("missing source name")
        return names[index]
    slots={}
    for b in common['m_ConstantBufferBindings']:
        index,slot=b['m_NameIndex'],b['m_Index']
        if type(slot) is not int or slot<0 or index in slots or slot in slots.values():
            raise ValueError("ambiguous source slot")
        slots[index]=slot
    buffers=[]
    for b in common['m_ConstantBuffers']:
        if b['m_NameIndex'] not in slots:raise ValueError("unbound source buffer")
        members=[]
        for field,kind,dimension in (('m_MatrixParams','matrix','m_RowCount'),('m_VectorParams','vector','m_Dim')):
            for m in b[field]:
                members.append(dict(name=resolve(m['m_NameIndex']),kind=kind,
                    serialized_index=m['m_Index'],serialized_dimension=m[dimension],
                    serialized_type=m['m_Type'],serialized_array_size=m['m_ArraySize']))
        if b['m_StructParams']:raise ValueError("struct source recovery required")
        if len({m['name'] for m in members})!=len(members):raise ValueError("duplicate source member")
        buffers.append(dict(name=resolve(b['m_NameIndex']),slot=slots[b['m_NameIndex']],
                            allocation_bytes=b['m_Size'],partial=b.get('m_IsPartialCB'),members=members))
    if len(buffers)!=len(slots):raise ValueError("missing source buffer")
    textures=[dict(name=resolve(t['m_NameIndex']),texture_slot=t['m_Index'],
                   sampler_slot=t['m_SamplerIndex'],serialized_dimension=t['m_Dim'])
              for t in common['m_TextureParams']]
    return dict(buffers=buffers,textures=textures,sampler_state_semantics_verified=False,
                upload_layout_or_gpu_verified=False)

def public_summary(plan):
    raw=json.dumps(plan,sort_keys=True,separators=(',',':')).encode()
    return dict(private_named_plan_sha256=hashlib.sha256(raw).hexdigest(),
                named_buffers=len(plan['buffers']),
                named_members=sum(len(b['members']) for b in plan['buffers']),
                named_textures=len(plan['textures']),private_names_published=False,
                upload_layout_or_gpu_verified=False)
