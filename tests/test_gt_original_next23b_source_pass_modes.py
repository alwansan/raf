"""Synthetic source tags exercise only the NEXT23b authenticated profile gate."""
import unittest
from scripts.gt_original_921_shaderlab import verified_source_next23b_pass_modes


def manifest():
    rows = [dict(subshader=0, **{'pass': i}, matched_pairs=289,
                 unmatched_vertex=0, unmatched_fragment=0,
                 original_state={'m_Tags': {'tags': tags}})
            for i, tags in enumerate(([['LightMode', 'ForwardBase']],
                                      [['LightMode', 'ForwardAdd']], [], [['LightMode', 'Always']]))]
    pairs = []
    for i in range(1156):
        stages = {}
        for field, stage in (('vs', 1), ('fs', 0)):
            stages[field] = dict(program_ref=f'program-{stage * 67 + i % 67:03d}',
                                 player_bucket=0, bucket_ordinal=i,
                                 original_variant_metadata={'m_BlobIndex': i},
                                 original_D3D11_link=dict(blob_index=i, segment_index=0,
                                                         metadata_sha256='a' * 64, entry_sha256='b' * 64))
        pairs.append(dict(subshader=0, **{'pass': i // 289}, **stages))
    return dict(original_passes=rows, paired=pairs, unpaired=[])


class Next23BSourcePassModes(unittest.TestCase):
    def test_modes_come_from_tags_including_absent_and_always(self):
        self.assertEqual(verified_source_next23b_pass_modes(manifest()),
                         ('ForwardBase', 'ForwardAdd', 'Untagged', 'Always'))

    def test_drift_missing_provenance_and_unknown_or_duplicate_tags_rejected(self):
        for change in (
            lambda m: m['paired'].pop(),
            lambda m: m['paired'][0]['vs'].pop('original_D3D11_link'),
            lambda m: m['paired'][0]['vs'].update(program_ref='invented'),
            lambda m: m['original_passes'][0].update(subshader=1),
            lambda m: m['original_passes'][0]['original_state']['m_Tags'].update(tags=[['LightMode', 'Unknown']]),
            lambda m: m['original_passes'][0]['original_state']['m_Tags']['tags'].append(['LightMode', 'ForwardBase']),
        ):
            m = manifest()
            change(m)
            with self.assertRaises(ValueError):
                verified_source_next23b_pass_modes(m)
