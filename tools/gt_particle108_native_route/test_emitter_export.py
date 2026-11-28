import unittest
from tools.gt_particle108_native_route.emitter_export import stream_bytes,read_doc,compare_settings,reciprocal,ordered_materials,Reject
class SameExportTests(unittest.TestCase):
    def test_stream_exact(self):
        self.assertEqual(stream_bytes([0,1,15]),stream_bytes("00010f"))
    def test_invalid_byte(self):
        with self.assertRaises(Reject):stream_bytes([256])
    def test_numeric_hex_preserved(self):
        self.assertEqual(read_doc("ParticleSystemRenderer:\n  m_VertexStreams: 000102\n")["ParticleSystemRenderer"]["m_VertexStreams"],"000102")
    def test_stream_mismatch(self):
        a={"m_RenderMode":0,"m_VertexStreams":[0,1,2]}
        b={"m_RenderMode":0,"m_VertexStreams":"000201"}
        self.assertEqual(compare_settings(a,b,{}, {})["vertex_stream_bytes_matched"],0)
    def test_module_flag_mismatch(self):
        a={"m_RenderMode":0,"m_VertexStreams":[]}
        self.assertEqual(compare_settings(a,a,{"ShapeModule":{"enabled":True}},{"ShapeModule":{"enabled":0}})["module_flags_mismatched"],1)
    def test_material_order(self):
        g="a"*32;mp={(21,("s",1)):(10,g,2),(21,("s",2)):(11,g,2)}
        a=[{"fileID":10,"guid":g,"type":2},{"fileID":11,"guid":g,"type":2}]
        self.assertTrue(ordered_materials([("s",1),("s",2)],a,mp))
        self.assertFalse(ordered_materials([("s",1),("s",2)],a[::-1],mp))
    def test_reciprocal(self):
        g="a"*32;go={"m_Component":[{"component":{"fileID":2}},{"component":{"fileID":3}}]}
        r=ps={"m_GameObject":{"fileID":1}}
        self.assertTrue(reciprocal(go,r,ps,(1,g,3),(2,g,3),(3,g,3)))
        self.assertFalse(reciprocal(go,{"m_GameObject":{"fileID":9}},ps,(1,g,3),(2,g,3),(3,g,3)))
if __name__=="__main__":unittest.main()
