#!/usr/bin/env python3
'''
    Onionr - P2P Microblogging Platform & Social network. Run with 'help' for usage.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import sys
class Onionr:
    def __init__(self):
        command = ''
        try:
            command = sys.argv[1].lower()
        except IndexError:
            pass
        else:
            if command == 'start':
                self.daemon()
            elif command == 'stop':
                self.killDaemon()
            elif command == 'stats':
                self.showStats()
            elif command == 'help' or command == '--help':
                self.showHelp()
        return
    def daemon(self):
        return
    def killDaemon(self):
        return
    def showStats(self):
        return
    def showHelp(self):
        return

main = Onionr()