import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_original_draw as d

class SelectedOriginalDrawTests(unittest.TestCase):
    def test_pixel_controls_do_not_accept_blank_or_identical_reference(self):
        clear=np.zeros((3,3,4),dtype=np.float32)
        dummy=np.ones_like(clear)
        fixed=clear.copy();fixed[1,1]=.5
        rows=dict(clear=clear,dummy=dummy,type3=clear,type2=fixed,type2_repeat=fixed,wrong_guid=clear,wrong_fileid=clear)
        result=d.pixel_summary(rows)
        self.assertEqual(result["dummy_vs_clear"],9)
        self.assertEqual(result["type2_vs_clear"],1)
        self.assertEqual(result["type2_vs_wrong_guid"],1)
        self.assertEqual(result["type2_repeat_difference"],0)
        self.assertEqual(d.pixel_summary(dict(rows,wrong_guid=fixed))["type2_vs_wrong_guid"],0)
        self.assertEqual(d.pixel_summary(dict(rows,type2=clear))["type2_vs_clear"],0)
        with self.assertRaises(ValueError):d.pixel_summary(dict(rows,type2=np.full_like(clear,np.nan)))
    def test_source_material_controls_retain_original_shader(self):
        g="1"*32;s="2"*32;w="3"*32
        body=("\nMaterial:\n  m_Shader: {fileID: 4800000, guid: "+s+", type: 3}\n  m_SavedProperties:\n    m_TexEnvs:\n    - _Array:\n        m_Texture: {fileID: 18700000, guid: "+g+", type: 3}\n        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n")
        rows=d.variants(body,"_Array",g,18700000,3,w)
        self.assertEqual(rows["type3"],body)
        self.assertEqual(sum(x!=y for x,y in zip(rows["type2"],body)),1)
        self.assertIn("guid: "+s+", type: 3",rows["wrong_guid"])
        self.assertIn("guid: "+w+", type: 2",rows["wrong_guid"])
        self.assertIn("fileID: 18700001",rows["wrong_fileid"])

if __name__=="__main__":unittest.main()
