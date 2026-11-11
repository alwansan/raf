"""GFX144 source-free original-geometry regression cases (no Raft assets)."""
from __future__ import annotations

import io
import unittest

import numpy as np
from PIL import Image

from gfxlab.tools.gfx144_coplanar_face_audit import (
    paired_faces, project, closest_pairs, png_readback, DEPTH_TOLERANCE
)


def fixture(*, flip=True, z_offset=0., uv_shift=0., same_normal=False):
    front = [
        (-0.5, -0.5, 0., 0., 0.), (0.5, -0.5, 0., 1., 0.),
        (0., 0.5, 0., 0.5, 1.),
    ]
    rows = []
    for side in (0, 1):
        for x, y, z, u, v in front:
            normal_z = 1. if side == 0 or same_normal else -1.
            hand = 1. if side == 0 else -1.
            rows.append([x, y, z + (z_offset if side else 0.),
                         0., 0., normal_z, 1., 0., 0., hand,
                         u + (uv_shift if side else 0.), v])
    vertices = np.array(rows, dtype="<f4")
    cb2 = np.zeros((10,4),dtype="<f4")
    cb3 = np.zeros((21,4),dtype="<f4")
    cb2[:4] = np.eye(4,dtype="<f4")
    cb3[17:21] = np.eye(4,dtype="<f4")
    index = [0,1,2,3,5,4] if flip else [0,1,2,3,4,5]
    return vertices.tobytes(), cb2.tobytes(), cb3.tobytes(), np.array(index,dtype=np.int32).reshape(-1,3)


def detect(*, flip=True, z_offset=0., uv_shift=0., same_normal=False):
    mesh, cb2, cb3, index = fixture(flip=flip,z_offset=z_offset,
                                  uv_shift=uv_shift,same_normal=same_normal)
    verts, screen, depth = project(mesh, cb2, cb3)
    points = np.array([[128.5,128.5], [127.5,129.5]])
    nearest, tri_ids, barycentric, hits = closest_pairs(screen,depth,index,points)
    tie = (tri_ids[:,1] >= 0) & (abs(nearest[:,1]-nearest[:,0]) < DEPTH_TOLERANCE)
    paired = paired_faces(verts,screen,index,tri_ids,barycentric,tie)
    return tie, paired, hits


class GFX144SourceFreeTests(unittest.TestCase):
    def test_true_double_faced_triangle_is_detected(self):
        tie, paired, hits = detect()
        self.assertEqual(hits.tolist(),[2,2])
        self.assertEqual(tie.tolist(),[True,True])
        self.assertEqual(paired.tolist(),[True,True])

    def test_nearest_surfaces_at_different_depth_are_not_coplanar(self):
        tie, paired, hits = detect(z_offset=0.02)
        self.assertEqual(hits.tolist(),[2,2])
        self.assertFalse(tie.any())
        self.assertFalse(paired.any())

    def test_matching_normals_do_not_count_as_opposing_faces(self):
        tie, paired, _ = detect(same_normal=True)
        self.assertTrue(tie.all())
        self.assertFalse(paired.any())

    def test_matching_winding_is_not_opposing_face(self):
        tie, paired, _ = detect(flip=False)
        self.assertTrue(tie.all())
        self.assertFalse(paired.any())

    def test_different_original_uvs_are_not_matching_double_faces(self):
        tie, paired, _ = detect(uv_shift=0.05)
        self.assertTrue(tie.all())
        self.assertFalse(paired.any())

    def test_rejects_damaged_vertex_and_uniform_data(self):
        mesh, a, b, _ = fixture()
        with self.assertRaisesRegex(ValueError,"layout"):
            project(mesh[:-1],a,b)
        with self.assertRaisesRegex(ValueError,"layout"):
            project(mesh,a,b[:-4])

    def test_rejects_nan_source_geometry(self):
        mesh, a, b, _ = fixture()
        bad = np.frombuffer(mesh,dtype="<f4").copy()
        bad[0] = np.nan
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            project(bad.tobytes(),a,b)

    def test_rejects_degenerate_clip_w(self):
        mesh, a, b, _ = fixture()
        bad = np.frombuffer(b,dtype="<f4").copy().reshape(21,4)
        bad[20,3] = 0.
        with self.assertRaisesRegex(ValueError,"clip w"):
            project(mesh,a,bad.tobytes())

    def test_png_readback_restores_gles_bottom_left_origin(self):
        image = np.zeros((256,256,4),dtype=np.uint8)
        image[0,0] = [10,20,30,255]
        image[-1,-1] = [40,50,60,255]
        buf = io.BytesIO()
        Image.fromarray(image,"RGBA").save(buf,format="PNG")
        out = png_readback(buf.getvalue())
        self.assertEqual(out[0,-1].tolist(),[40,50,60,255])
        self.assertEqual(out[-1,0].tolist(),[10,20,30,255])


if __name__=="__main__":
    unittest.main()
