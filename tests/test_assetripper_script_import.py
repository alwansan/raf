from pathlib import Path
import tempfile
import unittest
from scripts.configure_assetripper_export import configure
from scripts.verify_assetripper_script_import import verify


class ScriptImportTests(unittest.TestCase):
    def log(self):
        return 'Import : During Mono initialization, found 151 assemblies\nGeneral : ScriptExportMode: Decompiled\nGeneral : === COMPLETED ===\n'

    def test_success_exit_with_unknown_backend_is_rejected(self):
        with self.assertRaises(ValueError):verify(self.log()+"Import : Could not initialize assembly manager. Switching to the 'Unknown' scripting backend.")

    def test_completed_mono_source_export_is_required(self):
        self.assertEqual(verify(self.log())['managed_provider_count'],151)
        for text in [self.log().replace('Decompiled','Hybrid'),self.log().replace('151','0'),self.log().replace('General : === COMPLETED ===','')]:
            with self.assertRaises(ValueError):verify(text)

    def test_settings_do_not_replace_existing_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(configure(root)['Export']['ScriptExportMode'],0)
            with self.assertRaises(FileExistsError):configure(root)
    def test_new_layout_loss_or_unknown_structure_is_rejected(self):
        for extra in ['layout mismatched binary content', 'Could not read MonoBehaviour structure for `Other.PlayerConfig`']:
            with self.assertRaises(ValueError):verify(self.log()+extra)
        result=verify(self.log()+'Could not read MonoBehaviour structure for `Sirenix.Serialization.GlobalSerializationConfig`')
        self.assertEqual(result['original_unresolved_structure_types'],{'Sirenix.Serialization.GlobalSerializationConfig':1})
