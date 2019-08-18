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
firstConvoLoad = true

function createConvoList(){
    convoListElement.innerHTML = ""
    for (friend in friendList){
        let convoEntry = document.createElement('li')
        let connectStatus = document.createElement('span')
        connectStatus.classList.add("connectStatus")
        if (firstConvoLoad){
            connectStatus.innerText = " ⌛"
        }
        else{
            connectStatus.innerText = " X"
            connectStatus.style.color = "red"
            console.log(direct_connections)
            if (direct_connections.hasOwnProperty(friend)){
                connectStatus.innerText = " ✅"
                connectStatus.style.color = "green"
            }
        }

        convoEntry.classList.add('convoEntry')
        convoEntry.setAttribute('data-pubkey', friend)
        convoEntry.innerText = friendList[friend]
        convoEntry.appendChild(connectStatus)
        convoListElement.append(convoEntry)
        firstConvoLoad = false
    }
    setTimeout(function(){createConvoList()}, 3000)
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
        // Create a connection to each peer
        createConnection(keys[i])
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