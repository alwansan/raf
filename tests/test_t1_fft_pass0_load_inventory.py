import unittest

from scripts.t1_fft_pass0_load_inventory import inventory


DECL = """
Texture2D<float4> src : register(t0);
Texture2D<float4> lookup : register(t1);
RWTexture2D<float4> output : register(u2);
"""


class LoadInventoryTests(unittest.TestCase):
    def test_nested_calls_and_comments(self):
        result = inventory(DECL + """
        // src.Load(ignored)
        float4 a = src.Load(int3(x, y, 0));
        float4 b = src.Load(int3(x, y, 0)) + lookup.Load(int3(x, y, 0));
        """)
        self.assertEqual(result["source"]["load"], 2)
        self.assertEqual(result["butterfly"]["load"], 1)

    def test_unclassified_access_is_reported(self):
        result = inventory(DECL + "src.Load(p); lookup[p]; src.Sample(s, p); lookup.GetDimensions(x, y);")
        self.assertEqual(result["source"]["unclassified"], 1)
        self.assertEqual(result["butterfly"], {"load": 0, "dimensions": 1, "subscript": 1, "unclassified": 0, "argument_reference": 0, "coordinate_constructor": 0, "dimension_helper_arguments": 0})

    def test_bare_argument_and_coordinate_constructor(self):
        result = inventory(DECL + "helper(lookup, p); src.Load(uint3(p, 0));")
        self.assertEqual(result["butterfly"]["argument_reference"], 1)
        self.assertEqual(result["source"]["coordinate_constructor"], 1)
        self.assertEqual(result["source"]["unclassified"], 0)

    def test_typed_dimension_only_helper(self):
        result = inventory(DECL + """
        uint2 helper(Texture2D<float4> tex, uint mip)
        {
            uint width, height, levels;
            tex.GetDimensions(mip, width, height, levels);
            return uint2(width, height);
        }
        void main() { helper(src, 0); helper(lookup, 0); }
        """)
        self.assertEqual(result["source"]["dimension_helper_arguments"], 1)
        self.assertEqual(result["butterfly"]["dimension_helper_arguments"], 1)

    def test_helper_that_reads_texels_is_not_dimension_only(self):
        result = inventory(DECL + """
        float4 helper(Texture2D<float4> tex) { return tex.Load(int3(0, 0, 0)); }
        void main() { helper(src); }
        """)
        self.assertEqual(result["source"]["argument_reference"], 1)
        self.assertEqual(result["source"]["dimension_helper_arguments"], 0)

    def test_scalar_typed_dimension_helper(self):
        result = inventory(DECL.replace("Texture2D<float4> src", "Texture2D<float> src") + """
        uint2 helper(Texture2D<float> tex, uint mip, out uint levels)
        {
            uint2 dims;
            tex.GetDimensions(mip, dims.x, dims.y, levels);
            return dims;
        }
        void main() { uint levels; helper(src, 0, levels); }
        """)
        self.assertEqual(result["source"]["dimension_helper_arguments"], 1)
