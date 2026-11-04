"""Regression over numeric-only authenticated original metadata, no raw assets."""
import json
from pathlib import Path
import unittest
from scripts.blur_cb_lane_map import build, lookup

class OriginalObservation(unittest.TestCase):
    def test_all_original_member_addresses_and_holes(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/blur_cb_observation.json').read_text())
        self.assertEqual(fixture['source_run'],41742032440)
        r=fixture['observation']
        self.assertTrue(r['original_verified'])
        self.assertEqual(r['original_object_sha256'],'c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52')
        buffers=members=lanes=holes=0
        for stage in r['stages']:
            for cb in stage['buffers']:
                m=build(cb);buffers+=1;holes+=m['unmapped_bytes']
                self.assertFalse(m['gpu_semantics_verified'])
                for ordinal,x in enumerate(cb['members']):
                    members+=1
                    n=x['serialized_dimension']*(4 if x['kind']=='matrix' else 1)
                    for c in range(n):
                        addr=x['serialized_index']+4*c
                        self.assertEqual(lookup(m,addr//16,(addr%16)//4),(ordinal,c))
                        lanes+=1
        self.assertEqual((buffers,members,lanes,holes),(6,7,70,968))
