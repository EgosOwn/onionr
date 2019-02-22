/*
    Onionr - P2P Anonymous Storage Network

    This file handles the UI for managing friends/contacts

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

friendListDisplay = document.getElementById('friendList')

fetch('/friends/list', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.json()) // Transform the data into json
.then(function(resp) {
    var keys = [];
    for(var k in resp) keys.push(k);
    console.log(keys)
    for (var i = 0; i < keys.length; i++){
        friendListDisplay.innerText = ''
        var peer = keys[i]
        var name = resp[keys[i]]['name']
        if (name === null || name === ''){
            name = 'Anonymous'
        }
        var entry = document.createElement('div')
        entry.style.paddingTop = '8px'
        entry.innerText = name + ' - ' + peer
        friendListDisplay.appendChild(entry)
    }
  })