import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('gate', Path(__file__).parents[1] / 'actions/scan/gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
class PolicyTest(unittest.TestCase):
    def test_fixable_is_blocked_and_unfixed_is_reported(self):
        base = {'Results': [{'Vulnerabilities': [
            {'Severity': 'HIGH', 'FixedVersion': '2', 'PkgName': 'a'},
            {'Severity': 'CRITICAL', 'PkgName': 'b'}]}]}
        blocked, pending = gate.evaluate(base)
        self.assertEqual([x[1] for x in blocked], ['a'])
        self.assertEqual([x[1] for x in pending], ['b'])
    def test_secret_is_blocked_and_redacted(self):
        secret = {'Severity': 'HIGH', 'Match': 'sensitive', 'Code': 'sensitive'}
        blocked, _ = gate.evaluate({'Results': [{'Secrets': [secret]}]})
        self.assertTrue(blocked)
        self.assertNotIn('Match', secret)
        self.assertNotIn('Code', secret)
    def test_empty_report_fails_closed(self):
        with self.assertRaises(ValueError): gate.evaluate({})
