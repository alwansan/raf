"""T3 external texture dependency safety checks using public fake identities."""
from collections import Counter
import unittest
from scripts import t3_external_texture_lineage as m

class OriginalExternalTable(unittest.TestCase):
    def fake(self, ext=25, fid=1):
        s={('sharedassets6.assets',i+1):{} for i in range(41)}
        s[('sharedassets6.assets',1)].update(
            {f'SYNTH_{i}':((fid,i+1),(1.,1.,0.,0.)) for i in range(ext)})
        for i in range(227-ext):
            s[('sharedassets6.assets',i%41+1)][f'SLOT_{i}']=((0,0),(1.,1.,0.,0.))
        return s
    def check(self,slots=None,paths=None,manifest=None,pins=None):
        return m.dependencies(
            slots if slots is not None else self.fake(),
            paths if paths is not None else ["archive:/Raft_Data/sharedassets0.assets"],
            manifest if manifest is not None else Counter({"sharedassets0.assets":1}),
            pins if pins is not None else {"sharedassets0.assets":(100,"a"*64)})
    def test_exact_external_provider_counts(self):
        v=self.check()
        self.assertEqual(v['external_reference_slots'],25)
        self.assertEqual(v['texenv_slots'],227)
        self.assertEqual(v['required_sha_pinned_public_provider_names'],{"sharedassets0.assets":25})
        self.assertFalse(v['source_to_export_external_target_identity_verified'])
    def test_external_index_not_assumed_zero_based(self):
        with self.assertRaisesRegex(ValueError,"outside_dependency_table"):
            self.check(slots=self.fake(fid=2))
    def test_external_owner_not_uniquely_declared(self):
        with self.assertRaisesRegex(ValueError,"not_uniquely_declared"):
            self.check(manifest=Counter({"sharedassets0.assets":2}))
    def test_alias_to_selected_owner_rejected(self):
        with self.assertRaisesRegex(ValueError,"aliases_local_owner"):
            self.check(paths=["sharedassets6.assets"],manifest=Counter({"sharedassets6.assets":1}))
    def test_unpinned_candidate_stays_unverified(self):
        v=self.check(pins={})
        self.assertEqual(v['declared_but_not_pre_pinned'],25)
        self.assertEqual(v['required_sha_pinned_public_provider_names'],{})
    def test_null_pointer_with_external_id_rejected(self):
        slots=self.fake()
        slots[('sharedassets6.assets',1)]['SYNTH_0']=((1,0),None)
        with self.assertRaisesRegex(ValueError,"null_external"):
            self.check(slots=slots)
    def test_wrong_source_owner_rejected(self):
        slots=self.fake()
        slots[('wrong.assets',1)] = slots.pop(('sharedassets6.assets',1))
        with self.assertRaisesRegex(ValueError,"wrong_selected"):
            self.check(slots=slots)
    def test_bare_pathid_does_not_count_external(self):
        slots=self.fake()
        slots[('sharedassets6.assets',1)]['SYNTH_0']=((0,234),None)
        with self.assertRaisesRegex(ValueError,"source_counts_drift"):
            self.check(slots=slots)
    def test_no_private_material_identifiers_in_report(self):
        s=str(self.check())
        self.assertNotIn('SYNTH',s)
        self.assertNotIn('m_PathID',s)
        self.assertNotIn('archive:',s)
if __name__=="__main__": unittest.main()
