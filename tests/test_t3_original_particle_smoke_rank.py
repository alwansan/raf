"""Source-free controls for anonymous original smoke Shader48 rank evidence."""
import importlib.util
from pathlib import Path
import unittest

P=Path(__file__).resolve().parents[1]/"scripts"/"t3_original_particle_emitter_semantics.py"
S=importlib.util.spec_from_file_location("t3_rank",P)
M=importlib.util.module_from_spec(S)
S.loader.exec_module(M)

class RankTests(unittest.TestCase):
    def test_smoke_and_fire_separate_same_rank_sources(self):
        # Independent 34-use shaders must never be conflated by numeric rank.
        ranks={("private-a",1):34, ("private-b",2):34, ("private-c",3):108}
        rows=[("smoke_like",("private-a",1),("scene",i),2) for i in range(17)]
        rows += [("fire_like",("private-b",2),("scene",i+20),2) for i in range(17)]
        rows += [("fire_like",("private-c",3),("scene",i+50),2) for i in range(25)]
        result=M.safe_ranked_semantic_hints(ranks,rows)
        smoke=result["smoke_like_anonymous_source_Shader48_candidates"]
        fire=result["fire_like_anonymous_source_Shader48_candidates"]
        self.assertEqual(smoke,[{"original_source_particle_Shader48_total_material_use_rank":34,
                                 "matched_semantic_material_slots":34,
                                 "matched_semantic_renderer_objects":17}])
        self.assertEqual({v["original_source_particle_Shader48_total_material_use_rank"] for v in fire},{34,108})
        self.assertEqual(len(fire),2)
        self.assertNotIn("private-",str(result))
    def test_two_same_rank_shaders_remain_two_anonymous_rows(self):
        got=M.safe_ranked_semantic_hints({("A",1):34,("B",1):34},[
            ("smoke_like",("A",1),("scene",1),2),
            ("smoke_like",("B",1),("scene",2),2)])
        self.assertEqual(len(got["smoke_like_anonymous_source_Shader48_candidates"]),2)
    def test_renderer_dedupes_across_two_material_slots(self):
        got=M.safe_ranked_semantic_hints({("A",1):34},[
            ("smoke_like",("A",1),("scene",1),1),
            ("smoke_like",("A",1),("scene",1),1)])
        self.assertEqual(got["smoke_like_anonymous_source_Shader48_candidates"][0]["matched_semantic_renderer_objects"],1)
    def test_reject_unknown_shader_label_and_rank_overflow(self):
        ranks={("A",1):1}
        for row in [("smoke_like",("B",2),("scene",1),1),
                    ("unknown",("A",1),("scene",1),1),
                    ("smoke_like",("A",1),("scene",1),2),
                    ("smoke_like",("A",1),("scene",1),0)]:
            with self.subTest(row=row),self.assertRaises(ValueError):
                M.safe_ranked_semantic_hints(ranks,[row])

if __name__=="__main__":
    unittest.main()
