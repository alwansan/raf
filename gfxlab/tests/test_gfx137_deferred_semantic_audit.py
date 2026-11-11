"""Synthetic, source-free positive/negative cases for GFX137 MRT auditing."""
import unittest

from gfxlab.tools.gfx137_deferred_semantic_audit import NAMES, audit_deferred_mrt


def fixture():
    images = {}
    for name in NAMES:
        mode, target = name.split("-rt")
        target = int(target)
        image = bytearray()
        for pixel in range(16):
            covered = pixel < 12
            rgba = [30+target*20, 60+target*20, 90+target*20, 255] if covered else [0, 0, 0, 0]
            if target == 3:
                rgba = [0, 0, 0, 0]
            if covered and mode == "flat" and target == 2:
                rgba[1] += 20
            if covered and mode == "nonmetal" and target == 0 and pixel < 2:
                rgba[0] += 5
            if covered and mode == "nonmetal" and target == 1:
                rgba[2] += 20
            image.extend(rgba)
        images[name] = bytes(image)
    return images


class DeferredContractTests(unittest.TestCase):
    def setUp(self):
        self.ref = fixture()
        self.raw = dict(self.ref)

    def assertRejected(self, match):
        with self.assertRaisesRegex(ValueError, match):
            audit_deferred_mrt(self.raw, self.ref, minimum_covered=2)

    def test_valid_reference_and_exact_device(self):
        result = audit_deferred_mrt(self.raw, self.ref, minimum_covered=2)
        self.assertTrue(result["coverage_matches_reference"])
        self.assertEqual(result["coverage_pixels"], 12)
        self.assertEqual(result["device_control_changed_pixels"]["flat"], [0, 0, 12, 0])
        self.assertEqual(result["device_control_changed_pixels"]["nonmetal"], [2, 12, 0, 0])
        self.assertFalse(result["phase_closed"])
        self.assertTrue(all(row["mesa_rgba_exact"] for row in result["targets"].values()))

    def test_nonzero_device_rgb_drift_is_measured(self):
        pixels = bytearray(self.raw["native-rt2"])
        pixels[4] += 3
        self.raw["native-rt2"] = bytes(pixels)
        self.raw["nonmetal-rt2"] = bytes(pixels)
        result = audit_deferred_mrt(self.raw, self.ref, minimum_covered=2)
        self.assertEqual(result["targets"]["native-rt2"]["max_channel_absolute_error_0_to_255"], 3)
        self.assertGreater(result["targets"]["native-rt2"]["covered_rgb_mean_absolute_error_0_to_255"], 0)

    def test_missing_capture(self):
        self.raw.pop("nonmetal-rt3")
        self.assertRejected("12 Deferred")

    def test_truncated_capture(self):
        self.raw["flat-rt1"] = self.raw["flat-rt1"][:-4]
        self.assertRejected("length")

    def test_malformed_reference(self):
        self.ref["native-rt0"] = bytes(64)
        self.assertRejected("[Rr]eference")

    def test_reference_unrelated_control_change(self):
        b = bytearray(self.ref["flat-rt0"])
        b[0] += 1
        self.ref["flat-rt0"] = bytes(b)
        self.assertRejected("reference.*unrelated")

    def test_coverage_difference_is_rejected(self):
        b = bytearray(self.raw["native-rt0"])
        b[3] = 0
        self.raw["native-rt0"] = bytes(b)
        self.assertRejected("coverage differs")

    def test_coverage_change_across_controls(self):
        b = bytearray(self.raw["flat-rt0"])
        b[3] = 0
        self.raw["flat-rt0"] = bytes(b)
        self.assertRejected("alpha changed")

    def test_unrelated_target_changed(self):
        b = bytearray(self.raw["flat-rt1"])
        b[1] += 1
        self.raw["flat-rt1"] = bytes(b)
        self.assertRejected("unrelated")

    def test_no_normal_response(self):
        self.raw["flat-rt2"] = self.raw["native-rt2"]
        self.assertRejected("material response")

    def test_no_metallic_response(self):
        self.raw["nonmetal-rt1"] = self.raw["native-rt1"]
        self.assertRejected("material response")

    def test_missing_background(self):
        self.ref = {k: bytes(v[:12*4]) for k, v in self.ref.items()}
        self.raw = dict(self.ref)
        self.assertRejected("invalid native RT0 coverage|missing background")


class BatchIntegrationTests(unittest.TestCase):
    """Check the actual GFX124 ZIP auditor, not only the isolated metric helper."""

    def test_deferred_zip_can_reject_forged_control_with_valid_hashes(self):
        import io
        import json
        from hashlib import sha256
        from zipfile import ZipFile
        from gfxlab.tools.gfx124_batch_zip_audit import audit

        seed = fixture()
        reference = {name: data * 4096 for name, data in seed.items()}

        def run(device):
            apk, logs = io.BytesIO(), io.BytesIO()
            with ZipFile(apk, 'w') as package:
                package.writestr('assets/batch.json', json.dumps({'tests': [
                    {'id':'M02-deferred', 'primary':'M02-0', 'deferred':'M02-0-deferred'}]}))
                for name, data in reference.items():
                    package.writestr(f'assets/M02-0-deferred/{name}.rgba', data)
            rows = []
            with ZipFile(logs, 'w') as archive:
                for name in NAMES:
                    filename = f'M02-deferred-{name}.rgba'
                    data, expected = device[name], reference[name]
                    errors = [abs(a-b) for a,b in zip(data, expected)]
                    rows.append({'name':f'M02-deferred-{name}', 'raw':filename,
                                 'raw_rgba_sha256':sha256(data).hexdigest(),
                                 'mesa_rgba_sha256':sha256(expected).hexdigest(),
                                 'rgba_absolute_error_sum':sum(errors),
                                 'max_rgba_channel_error':max(errors)})
                    archive.writestr(filename, data)
                archive.writestr('summary.json', json.dumps({
                    'experiment':'GFX124', 'phase_closed':False,
                    'renderer':'synthetic', 'gles':'ES3', 'planned_tests':1,
                    'completed_tests':1, 'tests': [{'id':'M02-deferred',
                    'draw_completed':True, 'captures':rows}]}))
            apk.seek(0)
            logs.seek(0)
            return audit(logs, apk)

        good = run(reference)
        self.assertTrue(good['tests'][0]['deferred_semantics']['coverage_matches_reference'])
        mutated = dict(reference)
        buffer = bytearray(mutated['flat-rt1'])
        buffer[0] ^= 1
        mutated['flat-rt1'] = bytes(buffer)
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            run(mutated)
