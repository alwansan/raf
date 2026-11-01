import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.ci_memory_watch import memory_fields,sample,summarize,main

class MemoryTests(unittest.TestCase):
    def test_four_hour_budget_is_bounded_and_samples_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'memory.jsonl'
            args=['monitor','--output',str(out),'--samples','1440','--interval','10']
            with patch('sys.argv',args), patch('scripts.ci_memory_watch.sample',return_value={'MemAvailable_kb':10}), patch('scripts.ci_memory_watch.time.sleep'), patch('scripts.ci_memory_watch.signal.signal'):
                main()
            self.assertEqual(len(out.read_text().splitlines()),1440)
            for count in ('0','1441'):
                with patch('sys.argv',['monitor','--output',str(out),'--samples',count]):
                    with self.assertRaises(ValueError): main()
    def test_only_memory_allowlist_is_parsed(self):
        data=memory_fields('MemTotal: 16000 kB\nMemAvailable: 2000 kB\nSwapTotal: 8000 kB\nSwapFree: 7000 kB\nUnrelated: 9000 kB')
        self.assertEqual(data,{'MemTotal_kb':16000,'MemAvailable_kb':2000,'SwapTotal_kb':8000,'SwapFree_kb':7000})
    def test_process_sample_has_no_command_arguments_or_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'meminfo').write_text('MemAvailable: 2000 kB\n');proc=root/'123';proc.mkdir()
            (proc/'status').write_text('Name:\tUnity\nVmRSS:\t1234 kB\n')
            (proc/'environ').write_text('SECRET=must_not_read');(proc/'cmdline').write_text('private arguments')
            row=sample(root)
            self.assertEqual(row['largest_processes'],[{'name':'Unity','rss_kb':1234}])
            self.assertNotIn('private',json.dumps(row));self.assertNotIn('SECRET',json.dumps(row))
    def test_summary_tolerates_partial_last_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'memory.jsonl';p.write_text('{"MemAvailable_kb":123,"SwapFree_kb":456,"largest_processes":[{"rss_kb":789}]}\n{"partial"')
            with patch('scripts.ci_memory_watch.docker_states',return_value=[]):out=summarize(p)
            self.assertEqual(out['samples'],1);self.assertEqual(out['minimum_available_kb'],123)
            self.assertEqual(out['maximum_top_process_rss_kb'],789)
