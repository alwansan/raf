import unittest
from tools.gt_top_original_renderer.probe import keywords, select_route, check_links, trace_map

class TopRouteTests(unittest.TestCase):
    def test_keywords_string_and_list(self):
        self.assertEqual(keywords({"m_ShaderKeywords":"A B"}),keywords({"m_ValidKeywords":["B"],"m_InvalidKeywords":["A"]}))
        with self.assertRaises(ValueError):
            keywords({"m_ShaderKeywords":"A A"})
    def test_exact_route_and_no_fallback(self):
        p=[{"subshader":0,"pass":0,"keyword_universe":[{"name":"A"},{"name":"DIRECTIONAL"}],
            "routes":[{"enabled":["A","DIRECTIONAL"],"vs":1,"fs":2},{"enabled":["DIRECTIONAL"],"vs":3,"fs":4}]}]
        self.assertEqual(select_route(p,{"A"})["vs"],1)
        self.assertEqual(select_route(p,set())["vs"],3)
        p[0]["routes"].pop(0)
        with self.assertRaises(ValueError):
            select_route(p,{"A"})
    def test_duplicate_route_rejected(self):
        row={"enabled":[],"vs":1,"fs":2}
        with self.assertRaises(ValueError):
            select_route([{"subshader":0,"pass":0,"keyword_universe":[],"routes":[row,row]}],set())
    def test_actual_exact_edges_and_wrong_mesh(self):
        g="a"*32
        m="b"*32
        s="c"*32
        x="d"*32
        def ptr(g,f,t="2"):
            return {"fileID":str(f),"guid":g,"type":t}
        renderer={"m_GameObject":{"fileID":"9"},"m_Materials":[ptr(m,21)]}
        filt={"m_GameObject":{"fileID":"9"},"m_Mesh":ptr(x,43)}
        mat={"m_Shader":ptr(s,4800000,"3")}
        check_links(renderer,filt,mat,g,g,(m,21),(s,4800000),(x,43))
        with self.assertRaises(ValueError):
            check_links(renderer,filt,mat,g,g,(m,21),(s,4800000),(x,44))
        filt["m_GameObject"]={"fileID":"10"}
        with self.assertRaises(ValueError):
            check_links(renderer,filt,mat,g,g,(m,21),(s,4800000),(x,43))
    def test_wrong_material_and_shader(self):
        g="a"*32
        mat={"m_Shader":{"fileID":"4800000","guid":"b"*32,"type":"3"}}
        renderer={"m_GameObject":{"fileID":"1"},"m_Materials":[{"fileID":"2"}]}
        filt={"m_GameObject":{"fileID":"1"},"m_Mesh":{"fileID":"3"}}
        with self.assertRaises(ValueError):
            check_links(renderer,filt,mat,g,g,(g,4),("b"*32,4800000),(g,3))
        with self.assertRaises(ValueError):
            check_links(renderer,filt,mat,g,g,(g,2),("c"*32,4800000),(g,3))
    def test_duplicate_source_trace_rejected(self):
        row={"class_id":23,"source":{"owner":"level0","path_id":1},"export":{"file_id":2,"guid":"a"*32,"type":2}}
        with self.assertRaises(ValueError):
            trace_map({"objects":[row,row]},{23})

if __name__=="__main__":
    unittest.main()
