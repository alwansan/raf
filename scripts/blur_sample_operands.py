"""Bounded original SAMPLE resource/sampler operand linkage, no shader emission."""
from scripts.blur_cb_instruction import operand
def sample(words, textures):
 if not words or words[0]&2047!=69 or words[0]>>31 or (words[0]>>24)&127!=len(words):
  raise ValueError('sample instruction')
 at=1;items=[]
 for _ in range(4):
  item,at=operand(words,at);items.append(item)
 if at!=len(words):raise ValueError('sample trailing words')
 if items[0]['type'] not in (0,2) or items[2]['type']!=7 or items[3]['type']!=6:
  raise ValueError('sample operand roles')
 def slot(item):
  if len(item['indices'])!=1 or item['indices'][0]['relative'] is not None or item['modifier']:
   raise ValueError('sample dynamic or modified binding')
  return item['indices'][0]['immediate']
 texture,sampler=slot(items[2]),slot(items[3])
 matches=[p for p in textures if p['m_Index']==texture and p['m_SamplerIndex']==sampler]
 return {'original_texture_sampler_pair_matches':len(matches),
         'unique_original_pair':len(matches)==1,'runtime_or_sampling_values_verified':False}
