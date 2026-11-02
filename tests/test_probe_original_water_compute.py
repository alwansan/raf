import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.probe_original_water_compute import inspect


class WaterContractTests(unittest.TestCase):
    def fixture(self, folder):
        sources = {
            "Dx11FFT": (
                "class Dx11FFT { void ComputeFFT() {\n"
                " int idx = shader.FindKernel(\"FFT_Horizontal\");\n"
                " shader.SetTexture(idx, \"Source\", texture);\n"
                " shader.Dispatch(idx, 2, 1, 1);\n"
                " int _KernelIndex = idx;\n"
                "} }\n"
            ),
            "WavesRendererFFT": (
                "class WavesRendererFFT { void RenderMaps() {\n"
                " Graphics.Blit(source, destination, water, 3);\n"
                "} }\n"
            ),
        }
        expected = {}
        for stem, source in sources.items():
            (folder / (stem + ".cs")).write_text(source)
            expected[stem] = hashlib.sha256(source.encode()).hexdigest()
        return expected

    def test_private_original_compute_contract_and_readonly_behavior(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            expected = self.fixture(folder)
            before = {p.name: p.read_bytes() for p in folder.iterdir()}
            result = inspect(folder, expected)
            self.assertFalse(result["unity_compiled"])
            self.assertFalse(result["restored_authentic_water_compute_source_verified"])
            self.assertFalse(result["source_modified"])
            self.assertEqual(result["scripts"]["Dx11FFT"]["find_kernel_literal_identifiers"],
                             ["FFT_Horizontal"])
            self.assertEqual(result["scripts"]["Dx11FFT"]["calls"]["dispatch"], 1)
            self.assertEqual(result["scripts"]["WavesRendererFFT"]["calls"]["blit"], 1)
            self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir()})

    def test_missing_or_modified_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            expected = self.fixture(folder)
            (folder / "Dx11FFT.cs").write_text("class Wrong {}")
            with self.assertRaisesRegex(ValueError, "Unknown original"):
                inspect(folder, expected)
            (folder / "Dx11FFT.cs").unlink()
            with self.assertRaisesRegex(ValueError, "exactly one original"):
                inspect(folder, expected)

    def test_missing_compute_dispatch_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            expected = self.fixture(folder)
            txt = (folder / "Dx11FFT.cs").read_text().replace("shader.Dispatch(idx, 2, 1, 1);", "RunFallback();")
            (folder / "Dx11FFT.cs").write_text(txt)
            expected["Dx11FFT"] = hashlib.sha256(txt.encode()).hexdigest()
            with self.assertRaisesRegex(ValueError, "dispatch"):
                inspect(folder, expected)


if __name__ == "__main__":
    unittest.main()
