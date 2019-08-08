/*
    Onionr - Private P2P Communication

    Main Onionr chat UI script

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
*/
friendList = {}
convoListElement = document.getElementsByClassName('conversationList')[0]

function createConvoList(){

    for (friend in friendList){
        var convoEntry = document.createElement('li')
        convoEntry.classList.add('convoEntry')
        convoEntry.setAttribute('data-pubkey', friend)
        convoEntry.innerText = friendList[friend]
        convoListElement.append(convoEntry)
    }
}

fetch('/friends/list', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.json()) // Transform the data into json
.then(function(resp) {
    var keys = []
    for(var k in resp) keys.push(k)
    for (var i = 0; i < keys.length; i++){
        friendList[keys[i]] = resp[keys[i]]['name']
    }
    createConvoList()
})

// Correct conversation list height
function correctConvoList(){
    margin = 50
    els = document.getElementsByClassName('convoListContainer')
    for (x = 0; x < els.length; x++){
        els[x].style.height = window.innerHeight - (2 * margin) + 'px'
    }
}
setInterval(function(){correctConvoList()}, 30)