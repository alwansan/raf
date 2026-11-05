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
        self.assertEqual(result, {"source": 2, "butterfly": 1})

    def test_unclassified_access_rejected(self):
        with self.assertRaises(ValueError):
            inventory(DECL + "src.Load(p); lookup.Load(p); src.Sample(s, p);")
