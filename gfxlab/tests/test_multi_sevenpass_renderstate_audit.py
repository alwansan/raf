import unittest
from gfxlab.tools.multi_sevenpass_renderstate_audit import (
    presence_count,bucket_queue,bucket_keywords
)
class TestSevenPassStateCensus(unittest.TestCase):
    def test_pass_fields_count_known_present_and_absent(self):
        s=presence_count([{"culling":{"raw":1},"zWrite":None},None,{"zWrite":1}],
                         ("culling","zWrite","zTest"))
        self.assertEqual(s["present_state_block"],2)
        self.assertEqual(s["missing_state_block"],1)
        self.assertEqual(s["field_present_culling"],1)
        self.assertEqual(s["field_nonnull_zWrite"],1)
        self.assertEqual(s["field_absent_zTest"],2)
    def test_bad_pass_state_rejected(self):
        with self.assertRaises(ValueError):
            presence_count([],( "zWrite",))
        with self.assertRaises(ValueError):
            presence_count(["not_dictionary"],("zWrite",))
    def test_source_render_queue_uses_buckets_only(self):
        self.assertEqual(bucket_queue(-1),"shader_default_queue_minus_one")
        self.assertEqual(bucket_queue(2000),"explicit_nonnegative_queue")
        self.assertEqual(bucket_queue(None),"unknown")
    def test_keywords_are_never_logged(self):
        self.assertEqual(bucket_keywords("A B"),"nonempty")
        self.assertEqual(bucket_keywords(""),"empty")
        self.assertEqual(bucket_keywords(None),"absent")
        self.assertEqual(bucket_keywords(["A"]),"nonempty")
        with self.assertRaises(ValueError):
            bucket_keywords(["A",55])
