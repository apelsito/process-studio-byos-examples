"""Behavioral checks for the useful artifacts and misleading-input boundaries."""
import copy
import csv
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {'ps-kpi-scorecard': 'build_scorecard', 'ps-raci-matrix': 'build_raci',
           'ps-control-register': 'build_controls', 'ps-bpmn-export': 'build_bpmn',
           'ps-delivery-handoff': 'build_handoff'}


def module(skill):
    script = ROOT / 'skills' / skill / 'scripts' / (SCRIPTS[skill] + '.py')
    spec = importlib.util.spec_from_file_location(SCRIPTS[skill], script)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def fixture(skill):
    return json.loads((ROOT / 'skills' / skill / 'assets/example.json').read_text(encoding='utf-8'))


class ExampleTests(unittest.TestCase):
    def test_all_five_cli_artifacts_and_invalid_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            for skill, script in SCRIPTS.items():
                with self.subTest(skill=skill):
                    output = Path(tmp) / (skill + '.out')
                    command = [sys.executable, str(ROOT/'skills'/skill/'scripts'/(script+'.py')),
                               '--input', str(ROOT/'skills'/skill/'assets/example.json'), '--output', str(output)]
                    completed = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertGreater(output.stat().st_size, 100)
                    self.assertEqual(json.loads(completed.stdout)['artifact'], str(output))
                    invalid = Path(tmp) / 'invalid.json'
                    invalid.write_text('{}', encoding='utf-8')
                    bad_output = Path(tmp) / (skill + '-invalid.out')
                    failed = subprocess.run([*command[:2], '--input', str(invalid), '--output', str(bad_output)], capture_output=True, text=True)
                    self.assertEqual(failed.returncode, 2)
                    self.assertFalse(bad_output.exists())

    def test_kpi_direction_targets_unknowns_and_escaping(self):
        data = fixture('ps-kpi-scorecard')
        data['process'] = '<script>alert(1)</script>'
        report = module('ps-kpi-scorecard').render(data)
        self.assertIn('+37.50%', report)
        self.assertIn('+15.00%', report)
        self.assertIn('Not achieved', report)
        self.assertIn('Achieved', report)
        self.assertIn('Unknown', report)
        self.assertNotIn('<script>', report)
        self.assertIn('&lt;script&gt;', report)
        data['metrics'][0]['baseline'] = 0
        report = module('ps-kpi-scorecard').render(data)
        self.assertNotIn('inf%', report)
        self.assertNotIn('nan%', report)

    def test_kpi_rejects_nonfinite_boolean_and_duplicate_metrics(self):
        for value in (float('nan'), float('inf'), True):
            data = fixture('ps-kpi-scorecard')
            data['metrics'][0]['current'] = value
            with self.assertRaises(ValueError):
                module('ps-kpi-scorecard').render(data)
        data = fixture('ps-kpi-scorecard')
        data['metrics'].append(copy.deepcopy(data['metrics'][0]))
        with self.assertRaises(ValueError):
            module('ps-kpi-scorecard').render(data)

    def test_raci_preserves_assignments_and_flags_gaps(self):
        data = fixture('ps-raci-matrix')
        original = copy.deepcopy(data)
        report, warnings = module('ps-raci-matrix').build(data)
        rows = list(csv.reader(io.StringIO(report)))
        self.assertEqual(warnings, 1)
        self.assertEqual(len(rows), 3)
        self.assertIn('Expected one accountable owner; found 0', rows[2][-2])
        self.assertEqual(data, original)
        data['activities'][1]['assignments']['Requester'] = 'A'
        data['activities'][1]['assignments']['Finance owner'] = 'A'
        report, _ = module('ps-raci-matrix').build(data)
        self.assertIn('found 2', report)

    def test_raci_rejects_unknown_roles_and_escapes_formulas(self):
        data = fixture('ps-raci-matrix')
        data['activities'][0]['name'] = '=HYPERLINK("https://example.org")'
        report, _ = module('ps-raci-matrix').build(data)
        rows = list(csv.reader(io.StringIO(report)))
        self.assertTrue(rows[1][3].startswith("'="))
        data['activities'][0]['assignments']['Undeclared'] = 'R'
        with self.assertRaises(ValueError):
            module('ps-raci-matrix').build(data)

    def test_controls_scores_sorting_and_gaps(self):
        data = fixture('ps-control-register')
        report, gaps = module('ps-control-register').render(data)
        self.assertEqual(gaps, 3)
        self.assertLess(report.index('<td>R1</td>'), report.index('<td>R2</td>'))
        self.assertLess(report.index('<td>R2</td>'), report.index('<td>R3</td>'))
        self.assertIn('<td>20</td><td>High</td>', report)
        self.assertIn('Proposed control', report)
        self.assertIn('Missing evidence', report)
        self.assertIn('Unknown', report)
        data['risks'][0]['likelihood'] = 6
        with self.assertRaises(ValueError):
            module('ps-control-register').render(data)

    def test_bpmn_references_conditions_and_di(self):
        mod = module('ps-bpmn-export')
        root = ET.fromstring(mod.build(fixture('ps-bpmn-export')))
        ns = mod.NS
        process = root.find('bpmn:process', ns)
        self.assertEqual(process.get('isExecutable'), 'false')
        self.assertEqual(len(process.findall('bpmn:sequenceFlow', ns)), 5)
        self.assertEqual(len(root.findall('.//bpmndi:BPMNShape', ns)), 5)
        self.assertEqual(len(root.findall('.//bpmndi:BPMNEdge', ns)), 5)
        self.assertEqual(len(process.findall('.//bpmn:conditionExpression', ns)), 2)
        ids = [x.get('id') for x in root.iter() if x.get('id')]
        self.assertEqual(len(ids), len(set(ids)))

    def test_bpmn_rejects_disconnected_and_ambiguous_decisions(self):
        data = fixture('ps-bpmn-export')
        data['nodes'].append({'id': 'orphan', 'name': 'Orphan', 'type': 'task'})
        with self.assertRaises(ValueError):
            module('ps-bpmn-export').build(data)
        data = fixture('ps-bpmn-export')
        del data['flows'][2]['condition']
        with self.assertRaises(ValueError):
            module('ps-bpmn-export').build(data)

    def test_handoff_does_not_promote_claims_and_flags_missing_evidence(self):
        data = fixture('ps-delivery-handoff')
        original = copy.deepcopy(data)
        report, gaps = module('ps-delivery-handoff').build(data)
        self.assertEqual(gaps, 2)
        self.assertIn('locally\\_verified', report)
        self.assertIn('No runtime trace or acceptance supplied', report)
        self.assertEqual(data, original)
        data['items'][0]['layer'] = 'accepted'
        data['items'][0]['evidence'] = []
        report, gaps = module('ps-delivery-handoff').build(data)
        self.assertEqual(gaps, 3)
        self.assertIn('no evidence supplied for the claimed accepted layer', report)


if __name__ == '__main__':
    unittest.main()
