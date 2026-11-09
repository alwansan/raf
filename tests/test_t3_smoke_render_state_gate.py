import unittest
from t3_smoke_render_state_gate import audit

class SmokeStateTests(unittest.TestCase):
    def sample(self):
        side = dict(identity_role='smoke_linked_34_use_shader48', smoke_named_renderer_count=17,
                    material_slot_count=34, source_sha256='a'*64, blend_enabled=True,
                    alpha_test=False, alpha_blend=True, program_present=True)
        return {'schema':'t3-smoke-render-state-v1','original':side.copy(),'exported':side.copy()}
    def test_match(self):
        self.assertEqual(audit(self.sample())['status'], 'SCOPED_STATE_MATCH')
    def test_mismatch(self):
        d=self.sample();d['exported']['alpha_blend']=False
        self.assertEqual(audit(d)['mismatches'], ['alpha_blend'])
    def test_unknown_fails(self):
        d=self.sample();d['exported']['blend_enabled']=None
        with self.assertRaisesRegex(ValueError,'unknown_render_state'):audit(d)
    def test_other_shader_fails(self):
        d=self.sample();d['original']['identity_role']='fire_108_use_shader'
        with self.assertRaisesRegex(ValueError,'wrong_shader_identity'):audit(d)
    def test_wrong_source_fails(self):
        d=self.sample();d['exported']['source_sha256']='b'*64
        with self.assertRaisesRegex(ValueError,'different_original_source'):audit(d)
    def test_wrong_graph_fails(self):
        d=self.sample();d['original']['material_slot_count']=108
        with self.assertRaisesRegex(ValueError,'graph_count_not_verified'):audit(d)
    def test_nonhex_source_fails(self):
        d=self.sample();d['original']['source_sha256']='z'*64
        with self.assertRaisesRegex(ValueError,'missing_source_fingerprint'):audit(d)
    def test_boolean_graph_count_fails(self):
        d=self.sample();d['original']['smoke_named_renderer_count']=True
        with self.assertRaisesRegex(ValueError,'graph_count_not_verified'):audit(d)
if __name__=='__main__':unittest.main()
