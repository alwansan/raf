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
        self.assertEqual(result["butterfly"], {"load": 0, "dimensions": 1, "subscript": 1, "unclassified": 0, "argument_reference": 0, "coordinate_constructor": 0})

    def test_bare_argument_and_coordinate_constructor(self):
        result = inventory(DECL + "helper(lookup, p); src.Load(uint3(p, 0));")
        self.assertEqual(result["butterfly"]["argument_reference"], 1)
        self.assertEqual(result["source"]["coordinate_constructor"], 1)
        self.assertEqual(result["source"]["unclassified"], 0)
