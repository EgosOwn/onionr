import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid
TEST_DIR = 'testdata/-%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
os.environ["ONIONR_HOME"] = TEST_DIR
from unittest.mock import patch

from utils import createdirs

from subprocess import Popen
import subprocess
from time import sleep

from helium import start_firefox, click, Text, Config


from onionrcommands.openwebinterface import get_url
from onionrutils import escapeansi
BROWSER_HEADLESS = os.getenv('ONIONR_TEST_HEADLESS')

Config.implicit_wait_secs = 30

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
        if not Text('Circles').exists():
            click('Get Started')
        sleep(2)
        click('Circles')
        sleep(5)
        if not Text('Circle Name').exists():
            Popen(['./onionr.sh', 'stop']).wait()
            web_driver.quit()
            raise ValueError
        Popen(['./onionr.sh', 'stop']).wait()
        web_driver.quit()

unittest.main()