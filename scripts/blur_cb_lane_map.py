"""Sparse CB address model for private original rebinding; no ShaderLab emission.

Consumes observed numeric records, preserving full allocations and all holes.
No claim that serialized indices or matrix orientation match GPU execution.
"""
def build(buffer):
    size = buffer['allocation_bytes']
    if type(size) is not int or size <= 0 or size % 4:
        raise ValueError('allocation')
    lanes = [None] * (size // 4)
    for ordinal, member in enumerate(buffer['members']):
        offset = member['serialized_index']
        dim = member['serialized_dimension']
        if type(offset) is not int or offset < 0 or offset % 4:
            raise ValueError('offset')
        if type(dim) is not int or not 1 <= dim <= 4:
            raise ValueError('dimension')
        if member['serialized_array_size'] != 0 or member['serialized_type'] != 0:
            raise ValueError('unverified array or type')
        kind = member['kind']
        if kind not in ('matrix', 'vector'):
            raise ValueError('kind')
        count = dim * (4 if kind == 'matrix' else 1)
        if offset // 4 + count > len(lanes):
            raise ValueError('outside allocation')
        for component in range(count):
            at = offset // 4 + component
            if lanes[at] is not None:
                raise ValueError('overlapping members')
            lanes[at] = (ordinal, component)
    return {'allocation_bytes': size, 'lanes': lanes,
            'unmapped_bytes': 4 * lanes.count(None),
            'gpu_semantics_verified': False}

def lookup(model, register, component):
    if type(register) is not int or register < 0 or type(component) is not int or not 0 <= component < 4:
        raise ValueError('address')
    index = register * 4 + component
    if index >= len(model['lanes']):
        raise ValueError('outside allocation')
    return model['lanes'][index]
