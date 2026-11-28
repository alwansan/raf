import unittest
from tools.gt_top_resource_closure import selected_forward_context as f
class ForwardContextTests(unittest.TestCase):
    def test_tag_exact_and_only_case_rewritten(self):
        passes=[dict(subshader=0,**{"pass":0},original_state={"m_Tags":{"tags":[["LIGHTMODE","FORWARDBASE"],["Other","yes"]]}})]
        tag=f.exact_forward_tag(passes)
        raw=b'Shader "Test" {\nTags { "LIGHTMODE" = "FORWARDBASE" "Other" = "yes" }\n}'
        self.assertEqual(f.rename_and_normalize(raw,"Test","Hidden/Test",tag),
                         b'Shader "Hidden/Test" {\nTags { "LightMode" = "ForwardBase" "Other" = "yes" }\n}')
        with self.assertRaises(ValueError):f.rename_and_normalize(raw+raw,"Test","Hidden/Test",tag)
        passes[0]["original_state"]["m_Tags"]["tags"][0][1]="DEFERRED"
        with self.assertRaises(ValueError):f.exact_forward_tag(passes)
    def test_no_guess_for_absent_tag(self):
        with self.assertRaises(ValueError):f.exact_forward_tag([dict(subshader=0,**{"pass":0},original_state={"m_Tags":{"tags":[]}})])
if __name__=="__main__":unittest.main()
