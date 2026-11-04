"""B09 bounded synthetic tests, not claims about source Raft or Unity pixels."""
from pathlib import Path
import hashlib
import tempfile
import unittest

from scripts.b09_stage_original_spectrum import stage_pairs, _variant_key, _safe


def variants(stage_program):
    return [(0, i, row) for i, row in enumerate(stage_program.get("variants", []))]


def link(row, entries, stage):
    if row.get("wrong_stage") == stage:
        raise ValueError("Simulated authentic stage-type mismatch")
    return (f"DXBC-{stage}-{row['m_ShaderHardwareTier']}".encode(),
            {"blob_index": row["index"], "segment_index": 0})


def original_pair(left, right, *, pass_type=0):
    def v(idx, tier):
        return {"index": idx, "m_ShaderHardwareTier": tier, "m_KeywordIndices": []}
    return {"m_Type": pass_type, "progVertex": {"variants": [v(*p) for p in left]},
            "progFragment": {"variants": [v(*p) for p in right]}}


class SpectrumStageTests(unittest.TestCase):
    def generate(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            return stage_pairs(payload, [], linked_program=link,
                               stage_variants=variants, output_dir=Path(tmp))

    def test_out_of_order_variants_pair_by_permutation_not_index(self):
        rows = self.generate(original_pair([(10, 3), (11, 2)], [(20, 2), (21, 3)]))
        self.assertEqual(len(rows), 2)
        self.assertEqual({x['stages']['1']['original_blob_index'] for x in rows}, {10, 11})
        self.assertEqual({x['stages']['0']['original_blob_index'] for x in rows}, {20, 21})
        matched = {x['stages']['1']['original_blob_index']: x['stages']['0']['original_blob_index'] for x in rows}
        self.assertEqual(matched, {10: 21, 11: 20})
        self.assertTrue(all(len(x['variant_key_sha256']) == 64 for x in rows))

    def test_publishes_only_sha_and_index_metadata_no_bytecode(self):
        report = self.generate(original_pair([(10, 2)], [(20, 2)]))
        self.assertEqual(len(report), 1)
        self.assertNotIn('DXBC-', str(report))
        self.assertEqual(report[0]['stages']['1']['sha256'], hashlib.sha256(b'DXBC-1-2').hexdigest())

    def test_unpaired_original_variants_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'do not match'):
            self.generate(original_pair([(1, 3)], [(2, 4)]))

    def test_duplicate_serialized_permutation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.generate(original_pair([(1, 3), (2, 3)], [(3, 3)]))

    def test_normal_program_requires_both_nonempty_stages(self):
        with self.assertRaisesRegex(ValueError, 'no variants'):
            self.generate(original_pair([(1, 2)], []))

    def test_non_normal_pass_refused_not_placeholder(self):
        with self.assertRaisesRegex(ValueError, 'Non-normal'):
            self.generate(original_pair([(1, 2)], [(2, 2)], pass_type=1))

    def test_empty_or_wrong_stage_code_refused(self):
        row = original_pair([(1, 2)], [(2, 2)])
        row['progVertex']['variants'][0]['wrong_stage'] = 1
        with self.assertRaisesRegex(ValueError, 'stage-type'):
            self.generate(row)

    def test_missing_required_program_refused(self):
        row = original_pair([(1, 2)], [(2, 2)])
        del row['progFragment']
        with self.assertRaisesRegex(ValueError, 'Missing original'):
            self.generate(row)

    def test_symlinked_private_parent_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'real').mkdir()
            (root / 'link').symlink_to(root / 'real', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'Linked'):
                _safe(root / 'link' / 'new')

    def test_variant_identity_is_stable_independent_of_dict_key_order(self):
        a = {'m_KeywordIndices': [1, 2], 'm_ShaderHardwareTier': 2}
        b = {'m_ShaderHardwareTier': 2, 'm_KeywordIndices': [1, 2]}
        self.assertEqual(_variant_key(a), _variant_key(b))
        self.assertNotEqual(_variant_key(a), _variant_key({'m_ShaderHardwareTier': 2, 'm_KeywordIndices': [2, 1]}))


if __name__ == '__main__':
    unittest.main()
