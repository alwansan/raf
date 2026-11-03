"""Test-owned serialization only; no proprietary original object bytes."""
import hashlib
import struct
import unittest
from scripts.probe_original_water_quality_values import decode


def fixture():
    b=bytearray()
    def emit(fmt,*values):b.extend(struct.pack('<'+fmt,*values))
    def align():b.extend(b'\0'*((-len(b))%4))
    def boolean(v):emit('B',v);align()
    def name(s):v=s.encode();emit('i',len(v));b.extend(v);align()
    emit('iq',0,0);boolean(1);emit('iq',1,838);name('OwnedFixture');emit('6i',0,1,14,12,14,1);emit('i',2)
    for cap in (32,512):
        name('TestLevel');emit('i',cap);boolean(0);boolean(1);emit('f',1);emit('i',0);boolean(1)
        emit('ffii',1,0.5,100,50);boolean(1)
    boolean(1);emit('i',1)
    return bytes(b)

class QualityValueTests(unittest.TestCase):
    def parse(self,b):return decode(b,hashlib.sha256(b).hexdigest())
    def test_values_and_full_consumption_without_runtime_or_typetree_claim(self):
        b=fixture();r=self.parse(b)
        self.assertEqual([x['spectrum_limit'] for x in r['quality_levels']],[32,512])
        self.assertEqual(r['bytes_consumed'],len(b))
        self.assertTrue(r['synchronize_with_unity'])
        self.assertFalse(r['active_phone_quality_or_requested_water_resolution_verified'])
        self.assertFalse(r['original_full_typetree_verified'])
        self.assertNotIn('OwnedFixture',str(r));self.assertNotIn('TestLevel',str(r))

    def test_fingerprint_truncation_and_trailing_bytes_rejected(self):
        b=fixture()
        with self.assertRaisesRegex(ValueError,'fingerprint'):decode(b,'0'*64)
        for changed in (b[:-1],b+b'\0\0\0\0'):
            with self.assertRaises(ValueError):self.parse(changed)

    def test_bad_bool_alignment_enum_and_saved_index_rejected(self):
        b=fixture();r=self.parse(b);start=r['quality_levels'][0]['offset'];name_bytes=4+len('TestLevel');after_name=(start+name_bytes+3)&~3
        for offset,fmt,value in ((12,'B',2),(13,'B',1),(after_name+4,'B',2),
                                 (after_name+16,'i',9),(len(b)-4,'i',9)):
            changed=bytearray(b);struct.pack_into('<'+fmt,changed,offset,value)
            with self.assertRaises(ValueError):self.parse(bytes(changed))

    def test_nonfinite_measurement_is_not_accepted_as_valid_quality_float(self):
        b=fixture();r=self.parse(b);start=r['quality_levels'][0]['offset'];after_name=(start+4+len('TestLevel')+3)&~3
        for value in (float('nan'),float('inf'),-1.0):
            changed=bytearray(b);struct.pack_into('<f',changed,after_name+12,value)
            with self.assertRaises(ValueError):self.parse(bytes(changed))

if __name__=='__main__':unittest.main()
