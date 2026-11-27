"""Pure byte commitment controls (no Unity or original asset access)."""
import json
from hashlib import sha256
import unittest
from scripts.gt_fft_receipt_contract import verify_commitments, verify_original_commitments, require_same_decoded_receipt

def raw(x):
    return json.dumps(x,sort_keys=True).encode()

class ReceiptTests(unittest.TestCase):
    def fixture(self):
        candidate=b"authored candidate"
        source=raw({"status":"PREPARED","synthetic_only":True})
        bundle=b"authored bundle placeholder"
        unity={"receiptSchemaVersion":2,"unityVersion":"2021.3.45f2","checkpoint":"compiler_results",
               "failureType":"","candidateSha256":sha256(candidate).hexdigest(),"candidateBytes":len(candidate),
               "sourceReceiptSha256":sha256(source).hexdigest(),"bundleSha256":sha256(bundle).hexdigest(),
               "bundleBytes":len(bundle),"passCount":7,"registeredKeywordVariants":1,"errors":0,
               "androidVulkanOnly":True,"privateBundleCompiled":True,"originalMaterialGuidProven":False,
               "gamePlayerBuilt":False,"devicePixelsProven":False,"compilerControl":"hlslcc"}
        return candidate,source,unity,bundle

    def test_exact_commitment_and_original_scope_rejection(self):
        c,s,u,b=self.fixture()
        _,_,p=verify_commitments(c,s,raw(u),b)
        self.assertTrue(p["unity_receipt_byte_commitments_verified"])
        self.assertFalse(p["cryptographic_attestation_verified"])
        with self.assertRaisesRegex(ValueError,"fft_source_receipt:status"):
            verify_original_commitments(c,s,raw(u),b)

    def test_same_length_mutations(self):
        c,s,u,b=self.fixture()
        for i in (0,1,3):
            vals=[c,s,raw(u),b]
            v=vals[i]; at=v.index(b"a") if b"a" in v else 1
            vals[i]=v[:at]+b"x"+v[at+1:]
            self.assertEqual(len(v),len(vals[i]))
            with self.subTest(i=i),self.assertRaises(ValueError):
                verify_commitments(*vals)

    def test_missing_schema_and_wrong_types(self):
        c,s,u,b=self.fixture()
        for k,v in (("receiptSchemaVersion",1),("bundleBytes",True),("errors",False),
                    ("privateBundleCompiled",1),("compilerControl","unknown"),("failureType","Exception")):
            with self.subTest(k=k),self.assertRaises(ValueError):
                verify_commitments(c,s,raw(dict(u,**{k:v})),b)

    def test_duplicate_json_and_receipt_byte_binding(self):
        c,s,u,b=self.fixture()
        data=raw(u)
        with self.assertRaises(ValueError):
            verify_commitments(c,s,b'{"receiptSchemaVersion":2,'+data[1:],b)
        a=verify_commitments(c,s,data,b)[2]
        z=verify_commitments(c,s,data+b" ",b)[2]
        with self.assertRaises(ValueError):
            require_same_decoded_receipt(a,z)
        with self.assertRaises(ValueError):
            require_same_decoded_receipt({"ok":True},{"ok":1})
