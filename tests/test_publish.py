import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(os.name == 'posix' and shutil.which('bash'), 'Requires the Linux action environment')
class RegistryPublishTest(unittest.TestCase):
    def exercise(self, failures, inspect_failures=0, bad_digest=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / 'docker'
            docker.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root=Path(os.environ['FIXTURE_DIR'])
args=sys.argv[1:]
with (root/'calls').open('a') as out:out.write(json.dumps(args)+'\\n')
kind='push' if args[0]=='push' else 'inspect' if args[:3]==['buildx','imagetools','inspect'] else 'tag'
if kind=='tag':sys.exit(0)
counter=root/kind
count=int(counter.read_text())+1 if counter.exists() else 1
counter.write_text(str(count))
if count <= int(os.environ['FAIL_'+kind.upper()]):
 print('unknown blob',file=sys.stderr);sys.exit(1)
if kind=='inspect':print('invalid' if os.environ['BAD_DIGEST']=='1' else '"sha256:'+'a'*64+'"')
''')
            docker.chmod(0o755)
            sleep = root / 'sleep'
            sleep.write_text('#!/bin/sh\nexit 0\n')
            sleep.chmod(0o755)
            env = {**os.environ, 'PATH': str(root)+os.pathsep+os.environ['PATH'],
                   'FIXTURE_DIR': str(root), 'FAIL_PUSH': str(failures),
                   'FAIL_INSPECT': str(inspect_failures), 'BAD_DIGEST': str(int(bad_digest)),
                   'IMAGE': 'ghcr.io/example/test', 'CANDIDATE': 'candidate:gate',
                   'GITHUB_SHA': 'b'*40, 'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
                   'GITHUB_OUTPUT': str(root/'output'), 'GITHUB_STEP_SUMMARY': str(root/'summary')}
            script = Path(__file__).parents[1]/'actions/publish/push.sh'
            result = subprocess.run(['bash', str(script)], env=env, capture_output=True, timeout=15)
            calls = [json.loads(line) for line in (root/'calls').read_text().splitlines()]
            output = (root/'output').read_text() if (root/'output').exists() else ''
            return result.returncode, calls, output

    def test_transient_push_and_inspect_failures_publish_the_same_candidate(self):
        code, calls, output = self.exercise(2, 1)
        self.assertEqual(code, 0)
        pushes = [call for call in calls if call[0]=='push']
        self.assertEqual(len(pushes), 3)
        self.assertEqual(pushes, [pushes[0]]*3)
        self.assertEqual(len([call for call in calls if call[0]=='tag']), 1)
        self.assertEqual(output, 'digest=sha256:'+'a'*64+'\n')

    def test_permanent_push_failure_stops_before_digest_or_attestation(self):
        code, calls, output = self.exercise(99)
        self.assertNotEqual(code, 0)
        self.assertEqual(len([call for call in calls if call[0]=='push']), 3)
        self.assertFalse(any(call[0]=='buildx' for call in calls))
        self.assertEqual(output, '')

    def test_failed_or_invalid_digest_never_reports_publication_success(self):
        for kwargs in [{'inspect_failures':99}, {'bad_digest':True}]:
            code, _, output = self.exercise(0, **kwargs)
            self.assertNotEqual(code, 0)
            self.assertEqual(output, '')
