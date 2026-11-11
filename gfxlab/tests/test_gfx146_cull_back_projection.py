"""GFX146 synthetic tests: CCW/back/front source-only geometric cull selection."""
import unittest
import numpy as np

from gfxlab.tests.test_gfx144_coplanar_face_audit import fixture
from gfxlab.tools.gfx144_coplanar_face_audit import project
from gfxlab.tools.gfx146_cull_back_projection import evaluate, source_cull_fallback_verified


def source_rows(*, fallback="back", override=0, runtime=False):
    return {
        "experiment":"GFX145","original_material_slots":7,
        "original_unity_Cull_runtime_verified":runtime,
        "all_passes":[{
            "fallback_cull_enum":fallback,
            "runtime_unity_effective_cull_verified":False,
            "material_slots_with_matching_saved_float":override,
        } for _ in range(7)]
    }


def run_geometry(z_offset=0.,flip=True):
    mesh, cb2, cb3, triangles=fixture(z_offset=z_offset, flip=flip)
    _,screen,depth=project(mesh,cb2,cb3)
    points=np.array([[128.5,128.5],[127.5,129.5]])
    return evaluate(screen,depth,triangles,points)


class CullBackProjectionTests(unittest.TestCase):
    def test_authentic_cull_source_metadata_accepted_without_runtime_claim(self):
        self.assertTrue(source_cull_fallback_verified(source_rows()))

    def test_wrong_original_fallback_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"fallback"):
            source_cull_fallback_verified(source_rows(fallback="off"))

    def test_unresolved_dynamic_state_must_not_be_called_runtime_verified(self):
        with self.assertRaisesRegex(ValueError,"effective Unity"):
            source_cull_fallback_verified(source_rows(runtime=True))

    def test_direct_material_override_invalidates_fallback_only_conclusion(self):
        with self.assertRaisesRegex(ValueError,"fallback"):
            source_cull_fallback_verified(source_rows(override=2))

    def test_cull_back_removes_double_faces_without_losing_nearest_depth(self):
        out=run_geometry()
        self.assertEqual(out["total_triangles"],2)
        self.assertEqual(out["source_screen_CCW_front_triangles"],1)
        self.assertEqual(out["source_screen_CW_back_triangles"],1)
        self.assertEqual(out["CullBack_covered_original_pixels"],2)
        self.assertEqual(out["CullBack_visible_depth_changed_pixels"],0)

    def test_cull_front_changes_nearest_depth_on_separated_back_face(self):
        out=run_geometry(z_offset=0.02)
        self.assertEqual(out["CullBack_visible_depth_changed_pixels"],0)
        self.assertEqual(out["CullFront_visible_depth_changed_pixels"],2)
        self.assertEqual(out["CullFront_missing_original_pixels"],0)

    def test_winding_must_include_both_front_and_back_faces(self):
        with self.assertRaisesRegex(ValueError,"front/back"):
            run_geometry(flip=False)


if __name__=="__main__":
    unittest.main()
