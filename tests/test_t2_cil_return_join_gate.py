import unittest
from t2_cil_return_join_gate import classify_join, classify_path, Origin

F = [('ldarg.receiver','this'), ('ldfld','texture'), ('ret','')]
G = [('ldarg.receiver','this'), ('ldfld','other'), ('ret','')]

class GateTests(unittest.TestCase):
    def test_single_field(self): self.assertEqual(classify_join([F], complete_cfg=True), Origin('field','this/texture'))
    def test_matching_branches(self): self.assertEqual(classify_join([F,F], complete_cfg=True), Origin('field','this/texture'))
    def test_conflicting_fields(self): self.assertIsNone(classify_join([F,G], complete_cfg=True))
    def test_incomplete_cfg(self): self.assertIsNone(classify_join([F], complete_cfg=False))
    def test_missing_return(self): self.assertIsNone(classify_path(F[:-1]))
    def test_unknown_call(self): self.assertIsNone(classify_path([('call','unknown'),('ret','')]))
    def test_unbalanced_stack(self): self.assertIsNone(classify_path(F[:-1]+[('ldnull',''),('ret','')]))
    def test_null_branch_conflict(self): self.assertIsNone(classify_join([F,[('ldnull',''),('ret','')]], complete_cfg=True))
    def test_receiver_mismatch(self): self.assertIsNone(classify_join([F,[('ldarg.receiver','other'),('ldfld','texture'),('ret','')]],complete_cfg=True))
    def test_allocations_not_identity(self): self.assertIsNone(classify_join([[('newobj','RenderTexture'),('ret','')]],complete_cfg=True))
    def test_cast_after_load(self): self.assertEqual(classify_path(F[:-1]+[('castclass','Texture'),('ret','')]),Origin('field','this/texture'))
    def test_cast_receiver_rejected(self): self.assertIsNone(classify_path([('ldarg.receiver','this'),('castclass','X'),('ldfld','texture'),('ret','')]))
    def test_extra_after_ret(self): self.assertIsNone(classify_path(F+[('ldnull','')]))

if __name__=='__main__': unittest.main()
