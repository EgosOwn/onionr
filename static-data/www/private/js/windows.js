/*
    Onionr - Private P2P Communication

    Hide restart button if node OS is windows
    since restart is broken on windows

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
*/
var hideRestartIfWindows = function(){
    if (onionrNodeOS === 'windows'){
        document.getElementById('restartNode').style.display = 'none'
    }
}

setTimeout(function(){hideRestartIfWindows()}, 500)
