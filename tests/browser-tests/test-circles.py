from unittest.mock import patch
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/-%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
os.environ["ONIONR_HOME"] = TEST_DIR

from utils import createdirs

from subprocess import Popen
import subprocess
from time import sleep

from helium import start_firefox, click, Text


from onionrcommands.openwebinterface import get_url
from onionrutils import escapeansi
BROWSER_HEADLESS = os.getenv('ONIONR_TEST_HEADLESS')

def start_onionr():
    testargs = ["onionr.py", "start"]
    with patch.object(sys, 'argv', testargs):
        parser.register()


class OnionrTests(unittest.TestCase):
    def test_circles_home_load(self):
        Popen(['./onionr.sh', 'start'])
        while b'http' not in Popen(['./onionr.sh', 'url'], stdout=subprocess.PIPE).communicate()[0]:
            sleep(1)
        url = 'http' + escapeansi.escape_ANSI(Popen(['./onionr.sh', 'url'], stdout=subprocess.PIPE).communicate()[0].decode().split('http')[1])
        web_driver = start_firefox(url=url, headless=BROWSER_HEADLESS)
        if Text('Get Started').exists():
            click('Get Started')
        click('Circles')
        if not Text('Circle Name').exists():
            Popen(['./onionr.sh', 'stop']).wait()
            web_driver.quit()
            raise ValueError
        Popen(['./onionr.sh', 'stop']).wait()
        web_driver.quit()



unittest.main()