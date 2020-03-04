import sys
import os
from subprocess import Popen, PIPE
import uuid

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
os.environ["ONIONR_HOME"] = TEST_DIR

print(f'running integration test for {__file__}')
try:
    with Popen(['./onionr.sh'], stdout=PIPE) as onionr_proc:
        output = onionr_proc.stdout.read().decode()
except SystemExit:
    pass
if onionr_proc.returncode != 10:
    raise ValueError('Raised non 10 exit ' + str(onionr_proc.returncode))

if 'Run with --help to see available commands' not in output:
    raise ValueError('No command run returned non-blank output')
