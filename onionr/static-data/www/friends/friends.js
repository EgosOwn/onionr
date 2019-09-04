/*
    Onionr - Private P2P Communication

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
addForm = document.getElementById('addFriend')

function removeFriend(pubkey){
    post_to_url('/friends/remove/' + pubkey, {'token': webpass})
}

addForm.onsubmit = function(){
    var friend = document.getElementsByName('addKey')[0]
    var alias = document.getElementsByName('data')[0]
    if (alias.value.toLowerCase().trim() == 'anonymous'){
        PNotify.error({
            text: "Anonymous is a reserved alias name"
        })
        return false
    }

    fetch('/friends/add/' + friend.value, {
        method: 'POST',
        headers: {
          "token": webpass
        }}).then(function(data) {
            if (alias.value.trim().length > 0){
                post_to_url('/friends/setinfo/' + friend.value + '/name', {'data': alias.value, 'token': webpass})
            }
        })

    return false
}

fetch('/friends/list', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.json()) // Transform the data into json
.then(function(resp) {
    var keys = [];
    for(var k in resp) keys.push(k);
    console.log(keys)

    if (keys.length == 0){
        friendListDisplay.innerText = "None yet :("
    }
    for (var i = 0; i < keys.length; i++){
        var peer = keys[i]
        var name = resp[keys[i]]['name']
        if (name === null || name === ''){
            name = peer
        }
        var entry = document.createElement('div')
        var nameText = document.createElement('input')
        removeButton = document.createElement('button')
        removeButton.classList.add('friendRemove')
        removeButton.classList.add('button', 'is-danger')
        entry.setAttribute('data-pubkey', peer)
        removeButton.innerText = 'X'
        nameText.value = name
        nameText.readOnly = true
        nameText.style.fontStyle = "italic"
        entry.style.paddingTop = '8px'
        entry.appendChild(removeButton)
        entry.appendChild(nameText)
        friendListDisplay.appendChild(entry)
    }
    // If friend delete buttons are pressed

    var friendRemoveBtns = document.getElementsByClassName('friendRemove')

    for (var x = 0; x < friendRemoveBtns.length; x++){
        var friendKey = friendRemoveBtns[x].parentElement.getAttribute('data-pubkey')
        friendRemoveBtns[x].onclick = function(){
            removeFriend(friendKey)
        }
    }


  })