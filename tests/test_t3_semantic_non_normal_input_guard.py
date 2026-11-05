"""Fail-closed checks for non-normalmap semantic RGBA identity path."""
import unittest
from PIL import Image
from scripts.t3_normalmap_dxt5_semantic import semantic_rgba_input


class NonNormalSemanticInputGuard(unittest.TestCase):
    def test_valid_linear_dxt1_passthrough(self):
        image = Image.new("RGBA", (2, 2), (1, 2, 3, 255))
        self.assertIs(semantic_rgba_input(image, format_code=10,
            color_space=1, lightmap_format=0), image)

    def test_invalid_image_mode_is_not_exact(self):
        with self.assertRaisesRegex(ValueError, "invalid_authenticated_decoded_texture_input"):
            semantic_rgba_input(Image.new("RGB", (1, 1)), format_code=10,
                color_space=1, lightmap_format=0)

    def test_invalid_image_object_is_not_exact(self):
        with self.assertRaises(ValueError):
            semantic_rgba_input(None, format_code=10,
                color_space=1, lightmap_format=0)

    def test_invalid_format_is_not_exact(self):
        with self.assertRaisesRegex(ValueError, "invalid_authenticated_decoded_texture_input"):
            semantic_rgba_input(Image.new("RGBA", (1, 1)), format_code=0,
                color_space=1, lightmap_format=0)

    def test_invalid_dimensions_are_not_exact(self):
        with self.assertRaises(ValueError):
            semantic_rgba_input(Image.new("RGBA", (0, 1)), format_code=10,
                color_space=1, lightmap_format=0)


if __name__ == "__main__":
    unittest.main()
