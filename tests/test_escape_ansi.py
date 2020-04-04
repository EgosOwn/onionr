#!/usr/bin/env python3
import sys, os, random
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR_1 = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
TEST_DIR_2 = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
import time

os.environ["ONIONR_HOME"] = TEST_DIR_1
from utils import identifyhome, createdirs
from onionrsetup import setup_config
createdirs.create_dirs()

from onionrutils.escapeansi import escape_ANSI

class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"

class OnionrForwardSecrecyTests(unittest.TestCase):
    def test_no_replace(self):
        msg = 'test message'
        self.assertEqual(escape_ANSI(msg), msg)

    def test_escape_ansi(self):
        msg = "test"
        for color in dir(Colors):
            color = getattr(Colors, color)
            try:
                if '[' not in color and r'\0' not in color: continue
            except TypeError:
                continue
            try:
                self.assertEqual(escape_ANSI(color + msg), msg)
            except TypeError:
                pass
            self.assertEqual(escape_ANSI(msg), msg)

unittest.main()
