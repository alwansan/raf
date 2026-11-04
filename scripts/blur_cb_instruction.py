"""Bounded SM4/5 arithmetic operands; relative indices retained symbolically."""
from scripts.blur_cb_operand import decode
ARITY={0:3,15:3,16:3,17:3,50:4,51:3,52:3,54:2,55:4,56:3}
def operand(words,at,depth=0):
 if depth>8 or at>=len(words):raise ValueError('operand bound')
 t=words[at];at+=1;modifier=0
 if t>>31:
  if at>=len(words):raise ValueError('extension bound')
  ext=words[at];at+=1;modifier=(ext>>6)&255
  if ext&63!=1 or modifier>3 or ext&~(63|(255<<6)):raise ValueError('unsupported extension')
 typ=(t>>12)&255;dim=(t>>20)&3;indices=[]
 if typ not in (0,1,2,4,8,9):raise ValueError('operand_type_'+str(typ))
 for i in range(dim):
  kind=(t>>(22+3*i))&7
  if kind not in (0,2,3):raise ValueError('unsupported index')
  base=None;relative=None
  if kind in (0,3):
   if at>=len(words):raise ValueError('index bound')
   base=words[at];at+=1
  if kind in (2,3):
   relative,at=operand(words,at,depth+1)
   if relative['type'] not in (0,1) or relative['token']&3!=2 or (relative['token']>>2)&3!=2:
    raise ValueError('relative index source')
  indices.append({'immediate':base,'relative':relative})
 if typ==4:
  if dim or t&3 not in (1,2):raise ValueError('immediate shape')
  at+=1 if t&3==1 else 4
 if at>len(words):raise ValueError('truncated payload')
 return {'token':t,'type':typ,'indices':indices,'modifier':modifier},at
def read(words):
 if not words or any(type(x) is not int or not 0<=x<=0xffffffff for x in words):raise ValueError('words')
 h=words[0];op=h&2047
 if op not in ARITY or h>>31 or (h>>24)&127!=len(words):raise ValueError('instruction')
 at=1;reads=[]
 for ordinal in range(ARITY[op]):
  item,at=operand(words,at)
  if ordinal==0 and item['modifier']:raise ValueError('destination modifier')
  if item['type']==8:
   if ordinal==0 or len(item['indices'])!=2:raise ValueError('CB shape')
   dynamic=any(x['relative'] is not None for x in item['indices'])
   if dynamic:
    reads.append({'source_modifier':item['modifier'],'dynamic_index':True,
                  'index_expression':item['indices'],'byte_offsets':[]})
   else:
    t=item['token']&0x7fffffff
    out=decode([t]+[x['immediate'] for x in item['indices']])
    out['source_modifier']=item['modifier'];out['dynamic_index']=False;reads.append(out)
 if at!=len(words):raise ValueError('trailing words')
 return reads
