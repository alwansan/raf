"""Independent SPIR-V decoration fixtures for W1's real graphics binding bridge."""
import ast
from pathlib import Path
import re
import struct
import unittest

namespace={'re':re,'struct':struct}
tree=ast.parse(Path('scripts/w1_depth_raster_numeric.py').read_text())
function=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='normalize_bindings')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<actual-W1-binding-function>','exec'),namespace)
normalize=namespace['normalize_bindings']

def op(code,*args):
    return [((len(args)+1)<<16)|code,*args]
def named(ident,name):
    raw=(name+'\0').encode();raw+=b'\0'*((-len(raw))%4)
    return op(5,ident,*struct.unpack('<%dI'%(len(raw)//4),raw))
def fixture(texture='t0',sampler='s0'):
    words=[0x07230203,0x00010000,0,30,0]
    words+=named(17,texture)+named(23,sampler)
    # Descriptor order intentionally differs from original t/s register order.
    words+=op(71,17,33,9)+op(71,17,34,7)+op(71,23,33,4)+op(71,23,34,3)
    return struct.pack('<%dI'%len(words),*words)
def metadata():
    return {'m_CommonParameters':{'m_TextureParams':[{'m_Index':0,'m_SamplerIndex':0,'m_NameIndex':41}]}}
def reflected(texture='t0',sampler='s0'):
    return {'separate_images':[{'name':texture,'set':7,'binding':9}],'separate_samplers':[{'name':sampler,'set':3,'binding':4}]}

class BindingBridge(unittest.TestCase):
    def test_register_identity_beats_descriptor_order(self):
        result,count=normalize(fixture(),reflected(),metadata(),[('_SyntheticTex',41)],False)
        words=list(struct.unpack('<%dI'%(len(result)//4),result))
        self.assertEqual(count,1)
        self.assertEqual(words[-16:],[*op(71,17,33,0),*op(71,17,34,0),*op(71,23,33,2),*op(71,23,34,0)])
    def test_rebound_property_names_map_same_bindings(self):
        result,_=normalize(fixture('_SyntheticTex','sampler_SyntheticTex'),reflected('_SyntheticTex','sampler_SyntheticTex'),metadata(),[('_SyntheticTex',41)],True)
        words=struct.unpack('<%dI'%(len(result)//4),result)
        self.assertEqual(words[-13],0)
        self.assertEqual(words[-5],2)
    def test_wrong_register_missing_decoration_and_malformed_binary_fail(self):
        with self.assertRaises(ValueError):
            normalize(fixture('t1'),reflected('t1'),metadata(),[('_SyntheticTex',41)],False)
        raw=fixture()[:-16]
        with self.assertRaises(ValueError):
            normalize(raw,reflected(),metadata(),[('_SyntheticTex',41)],False)
        with self.assertRaises(ValueError):
            normalize(fixture()+struct.pack('<I',0),reflected(),metadata(),[('_SyntheticTex',41)],False)

if __name__=='__main__': unittest.main()

