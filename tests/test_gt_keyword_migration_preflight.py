import unittest
from scripts import gt_keyword_migration_preflight as p

class LiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=p.audit(p.ROOT)
    def test_all_ten_actual_source_groups(self):
        self.assertEqual(self.r["group_count"],10)
        self.assertEqual(self.r["private_selector_groups"],10)
        self.assertEqual(self.r["private_entrypoint_selector_groups"],10)
        self.assertTrue(all(len(x["source"]["git_blob_sha1"])==40 and len(x["installer"]["sha256"])==64 for x in self.r["groups"]))
    def test_actual_installer_gap(self):
        self.assertEqual(self.r["positive_engine_keyword_receipt_fields"],0)
        self.assertEqual(self.r["explicit_false_shared_override_groups"],1)
        self.assertTrue(all(x["receipt"]["receipt_checks_compiled_table_and_entrypoints"] and x["receipt"]["receipt_checks_stage_route_counts"] for x in self.r["groups"]))
    def test_historical_count_not_runtime(self):
        h=self.r["historical"];self.assertEqual(h["post23"]["non_dummy"],688)
        self.assertFalse(h["post23"]["runtime_keyword_parity_proven"])
        self.assertEqual(sum(h["NEXT23b"]["original_routes_by_pass"]),1156)
        self.assertFalse(h["NEXT23b"]["original_engine_routes_proven"])
    def test_fire_three_not_three_exported(self):
        f=self.r["historical"]["Particle108"];self.assertEqual((f["textures"],f["actual_external_images"]),(3,2))
        self.assertTrue(f["local_type0_source_top_alpha_decoded"])
        self.assertFalse(f["local_exported_pixels_compared"])
    def test_fail_closed_even_after_authored_PASS(self):
        self.assertEqual(self.r["historical"]["V17"]["packed_pixels"],1288)
        for k in ("acceptance_eligible","original_runtime_parity_proven","original_source_authorization_verified","original_assets_read","production_activation","Android_device","XAPK"):self.assertIs(self.r[k],False)
    def test_actual_source_mutation_not_mislabeled(self):
        b,_=p.read(p.ROOT,p.source_path("30"));s=b.decode()
        self.assertIn("engine_keywords=False",s)
        q=p.inspect_composer(s.replace("engine_keywords=False","engine_keywords=True"))
        self.assertEqual(q["compose_mode"],"literal_true_engine_candidate")
        self.assertFalse(q["engine_keyword_runtime_parity_proven"])
        with self.assertRaises(ValueError):p.inspect_composer(s.replace("engine_keywords=False","unresolved=True"))
    def test_actual_shared_override_mutation(self):
        b,_=p.read(p.ROOT,p.SHARED);s=b.decode();self.assertIn("counts_override is None,",s)
        q=p.inspect_shared(s.replace('"engine_keywords_verified": counts_override is None,','"engine_keywords_verified": True,'))
        self.assertFalse(q["engine_keyword_requirement_is_counts_override_none"])
        self.assertTrue(q["explicit_runtime_receipt_value_required"])
        b,_=p.read(p.ROOT,p.install_path("30"));result=p.inspect_installer(b.decode(),q)
        self.assertFalse(result["engine_keyword_runtime_parity_proven"])

if __name__=="__main__":unittest.main()
