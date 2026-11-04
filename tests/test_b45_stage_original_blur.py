"""B45 synthetic private stage attestation: hashes and negative controls only."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.b45_stage_original_blur import stage

TEXT = b'Synthetic test payload; not original source'


def recovered(private, *, negative=True):
    (private / "candidate.shader").write_bytes(TEXT)
    return {
        "private_shaderlab_constructed": True,
        "shaderlab_passes": 2,
        "shaderlab_bytes": len(TEXT),
        "shaderlab_sha256": hashlib.sha256(TEXT).hexdigest(),
        "raster": [{"positive": [{"within_tolerance": True}],
                    "negative": {"1": negative}},
                   {"positive": [{"within_tolerance": True}],
                    "negative": {"1": True}}],
    }


class PrivateBlurStageTests(unittest.TestCase):
    def try_stage(self, base, fake=None):
        root = Path(base)
        checkout = root / "repo"
        checkout.mkdir(exist_ok=True)
        scratch = root / "private"
        scratch.mkdir(exist_ok=True)
        candidate = scratch / "original-derived.shader"
        report = scratch / "aggregate.json"

        def fake_recover(_root, _repo, _runner, private, _progress):
            return recovered(private) if fake is None else fake(private)

        with mock.patch("scripts.b45_stage_original_blur.recover", side_effect=fake_recover), \
             mock.patch("scripts.b45_stage_original_blur.CANDIDATE_SHA256", hashlib.sha256(TEXT).hexdigest()), \
             mock.patch("scripts.b45_stage_original_blur.CANDIDATE_BYTES", len(TEXT)):
            result = stage(root, checkout, root / "no-real-gpu", candidate, report)
        return result, candidate, report

    def test_exact_original_source_is_private_and_report_is_aggregate(self):
        with tempfile.TemporaryDirectory() as d:
            result, candidate, report = self.try_stage(d)
            self.assertEqual(candidate.read_bytes(), TEXT)
            self.assertTrue(result["private_shader_staged"])
            self.assertFalse(result["private_shader_published"])
            self.assertNotIn(TEXT.decode(), report.read_text())
            self.assertEqual(json.loads(report.read_text())["private_shader_bytes"], len(TEXT))

    def test_negative_raster_mutation_cannot_stage_candidate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "repo").mkdir(); (root / "private").mkdir()
            def fake(_src, _repo, _run, private, _progress):
                return recovered(private, negative=False)
            with mock.patch("scripts.b45_stage_original_blur.recover", side_effect=fake), \
                 mock.patch("scripts.b45_stage_original_blur.CANDIDATE_SHA256", hashlib.sha256(TEXT).hexdigest()), \
                 mock.patch("scripts.b45_stage_original_blur.CANDIDATE_BYTES", len(TEXT)):
                with self.assertRaises(ValueError):
                    stage(root, root / "repo", root / "host",
                          root / "private" / "candidate.shader", root / "private" / "report.json")
            self.assertFalse((root / "private" / "candidate.shader").exists())

    def test_cannot_overwrite_or_write_inside_repository(self):
        with tempfile.TemporaryDirectory() as d:
            result, candidate, report = self.try_stage(d)
            with self.assertRaises(ValueError):
                self.try_stage(d)
            checkout = Path(d) / "repo"
            with self.assertRaises(ValueError):
                stage(Path(d), checkout, Path(d) / "host", checkout / "bad.shader",
                      Path(d) / "private" / "newreport.json")


if __name__ == "__main__":
    unittest.main()
