import unittest,copy
from gfxlab.tools.owner_stage_probe_audit097 import audit_records,BUILD,SOURCE

def fixture():
 s={'experiment':'GFX-MULTI-094','source_sha':SOURCE,'build_source_sha':BUILD,'all_pairs_tested':True,'completed_pairs':157,'expected_pairs':157,'compiled_stages':285,'linked_pairs':128,'failed_pairs':29,'originalShaderRestored':False,'phase_closed':False,'model_rendered':False,'PC_pixel_parity':False,'android_sdk':35,'renderer':'Adreno (TM) 730'}
 rows=[{'event':'environment'}]
 for i in range(157):
  p='P%03d'%i
  if i<128:rows.append({'event':'compile','pair':p,'stage':'vert','success':True,'gl_error':0,'driver_log':''})
  rows.append({'event':'compile','pair':p,'stage':'frag','success':True,'gl_error':0,'driver_log':''})
  if i>=128:rows.append({'event':'CPU_translation_unavailable','pair':p,'reason':{'vertex':'BaseInstance_ES_unsupported'}})
  rows.append(dict(event='link',pair=p,success=i<128,**({} if i<128 else {'skipped_compile_failure':True})))
 return s,rows
class Owner097(unittest.TestCase):
 def test_29_CPU_skips_are_not_driver_failures(self):
  s,r=fixture();d=audit_records(s,r)
  self.assertEqual(d['actual_device_compile_or_link_failures'],0);self.assertEqual(d['CPU_BaseInstance_unavailable_pairs'],29)
  self.assertFalse(d['original_Material_payload_or_model_pixels_proven'])
 def test_missing_event_rejected(self):
  s,r=fixture();r.pop()
  with self.assertRaises(ValueError):audit_records(s,r)
 def test_duplicate_compile_rejected(self):
  s,r=fixture();r.append(r[1])
  with self.assertRaises(ValueError):audit_records(s,r)
 def test_wrong_build_rejected(self):
  s,r=fixture();s['build_source_sha']='wrong'
  with self.assertRaises(ValueError):audit_records(s,r)
 def test_summary_lie_rejected(self):
  s,r=fixture();s['linked_pairs']=157
  with self.assertRaises(ValueError):audit_records(s,r)
 def test_nonzero_gl_error_not_lost(self):
  s,r=fixture();r[1]['gl_error']=1280
  self.assertEqual(audit_records(s,r)['nonzero_GL_error_events'],1)
 def test_phase_claim_rejected(self):
  s,r=fixture();s['originalShaderRestored']=True
  with self.assertRaises(ValueError):audit_records(s,r)
 def test_unknown_CPU_reason_rejected(self):
  s,r=fixture()
  for x in r:
   if x['event']=='CPU_translation_unavailable':x['reason']={'vertex':'invented'};break
  with self.assertRaises(ValueError):audit_records(s,r)
if __name__=='__main__':unittest.main()
