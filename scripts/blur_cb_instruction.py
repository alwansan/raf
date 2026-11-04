"""Bounded arithmetic instruction operands, SM4/5 subset; never scan tokens."""
from scripts.blur_cb_operand import decode
# D3D10_SB_OPCODE ADD, DP2/3/4, MAD, MIN/MAX, MOV/MOVC, MUL.
ARITY={0:3,15:3,16:3,17:3,50:4,51:3,52:3,54:2,55:4,56:3}
def read(words):
 if not words or any(type(x) is not int or not 0<=x<=0xffffffff for x in words):raise ValueError('words')
 header=words[0];opcode=header&2047
 if opcode not in ARITY or header>>31 or (header>>24)&127!=len(words):raise ValueError('instruction')
 at=1;reads=[]
 for ordinal in range(ARITY[opcode]):
  if at>=len(words):raise ValueError('truncated operand')
  start=at;t=words[at];at+=1
  modifier=0
  if t>>31:
   if at>=len(words):raise ValueError('truncated extension')
   ext=words[at];at+=1
   modifier=(ext>>6)&255
   if (ext&63)!=1 or modifier>3 or ext&~(63|(255<<6)):raise ValueError('unsupported extension')
   if ordinal==0:raise ValueError('destination modifier')
  typ=(t>>12)&255;dim=(t>>20)&3
  for index in range(dim):
   if (t>>(22+3*index))&7:raise ValueError('relative operand')
   at+=1
  if typ==4:
   if dim or t&3 not in (1,2):raise ValueError('immediate shape')
   at+=1 if t&3==1 else 4
  elif typ not in (0,1,2,8):raise ValueError('operand type')
  if at>len(words):raise ValueError('truncated payload')
  if typ==8:
   if ordinal==0:raise ValueError('CB destination')
   item=decode([t&0x7fffffff]+list(words[at-2:at]))
   item['source_modifier']=modifier
   reads.append(item)
 if at!=len(words):raise ValueError('trailing words')
 return reads
