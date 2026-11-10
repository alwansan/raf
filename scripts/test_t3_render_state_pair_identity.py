import unittest
from t3_render_state_pair_identity import pair
from t3_render_state_pair_diff import FIELDS


def sample():
    return {'material_guid': 'a' * 32, 'shader_guid': 'b' * 32,
            'pass_index': 0, 'source_sha256': 'c' * 64,
            'states': {k: None for k in FIELDS}}


class PairIdentityTests(unittest.TestCase):
    def test_same_identity_inconclusive_unknown_states(self):
        self.assertEqual(pair(sample(), sample())['status'], 'INCONCLUSIVE')

    def test_same_identity_mismatch(self):
        a, b = sample(), sample()
        a['states']['zwrite'], b['states']['zwrite'] = True, False
        self.assertEqual(pair(a, b)['changed_fields'], ['zwrite'])

    def test_different_material_rejected(self):
        a, b = sample(), sample()
        b['material_guid'] = 'd' * 32
        with self.assertRaisesRegex(ValueError, 'identity_mismatch:material_guid'):
            pair(a, b)

    def test_different_shader_rejected(self):
        a, b = sample(), sample()
        b['shader_guid'] = 'd' * 32
        with self.assertRaisesRegex(ValueError, 'identity_mismatch:shader_guid'):
            pair(a, b)

    def test_different_pass_rejected(self):
        a, b = sample(), sample()
        b['pass_index'] = 1
        with self.assertRaisesRegex(ValueError, 'identity_mismatch:pass_index'):
            pair(a, b)

    def test_bool_pass_rejected(self):
        a = sample()
        a['pass_index'] = True
        with self.assertRaisesRegex(ValueError, 'invalid_pass_index'):
            pair(a, sample())

    def test_bad_sha_rejected(self):
        a = sample()
        a['source_sha256'] = 'not verified'
        with self.assertRaisesRegex(ValueError, 'invalid_source_sha256'):
            pair(a, sample())

    def test_unknown_field_rejected(self):
        a = sample()
        a['extra'] = 'unsafe'
        with self.assertRaisesRegex(ValueError, 'invalid_envelope_fields'):
            pair(a, sample())

    def test_source_hash_not_authenticated(self):
        r = pair(sample(), sample())
        self.assertFalse(r['source_digests_content_verified'])
        self.assertFalse(r['device_fix_proven'])


if __name__ == '__main__':
    unittest.main()
