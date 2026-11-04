"""Decode one already-delimited SM4/5 immediate CB source operand.

Not an instruction scanner: caller must establish the operand boundary. Reject
relative, extended and unsupported encodings rather than guess bytecode words.
Reference: microsoft/DirectX-Headers D3D12TokenizedProgramFormat.hpp.
"""
def decode(words):
    if len(words) != 3 or any(type(x) is not int or not 0 <= x <= 0xffffffff for x in words):
        raise ValueError('bounded operand')
    token,slot,register=words
    if token >> 31 or ((token>>12)&255)!=8 or ((token>>20)&3)!=2 or (token>>22)&511:
        raise ValueError('unsupported CB indexing')
    if slot>255 or register>131071 or token&3!=2:
        raise ValueError('unsupported CB shape')
    mode=(token>>2)&3
    if mode==1:
        components=[(token>>(4+2*i))&3 for i in range(4)]
    elif mode==2:
        components=[(token>>4)&3]
    else:
        raise ValueError('source selection mode')
    return {'slot':slot,'register':register,'components':components,
            'byte_offsets':[16*register+4*c for c in components]}
