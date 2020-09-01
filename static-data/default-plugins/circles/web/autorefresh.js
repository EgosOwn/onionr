/*
    Onionr - Private P2P Communication

    Auto refresh board posts

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
var checkbox = document.getElementById('refreshCheckbox')
function autoRefresh(){
    if (! checkbox.checked || document.hidden){return}
    getBlocks()
}

function setupInterval(){
    if (checkbox.checked){
        refreshInterval = setInterval(autoRefresh, 3000)
        autoRefresh()
        return
    }
    clearInterval(refreshInterval)
}

var refreshInterval = setInterval(autoRefresh, 3000)
setupInterval()

checkbox.onchange = function(){setupInterval}


document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === 'visible') {
      autoRefresh()
    }
  })
