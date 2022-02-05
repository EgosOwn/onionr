import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid

import requests

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR
import onionrprocess

class TestOnionrProcess(unittest.TestCase):
    def test_onionr_process(self):
        def _sub_proc():
            return 2
        def _sub_proc_arg(arg):
            return arg
        def _sub_proc_kwarg(arg=''):
            return arg
        def _sub_proc_kwarg_default(arg=4):
            return arg
        def _sub_proc_both(arg, arg2=5):
            return (arg, arg2)
        self.assertEqual(onionrprocess.run_func_in_new_process(_sub_proc), 2)
        self.assertEqual(onionrprocess.run_func_in_new_process(_sub_proc_arg, 3), 3)
        self.assertEqual(onionrprocess.run_func_in_new_process(_sub_proc_kwarg, 4), 4)
        self.assertEqual(onionrprocess.run_func_in_new_process(_sub_proc_kwarg_default), 4)
        self.assertEqual(onionrprocess.run_func_in_new_process(_sub_proc_both, 6), (6, 5))

unittest.main()
