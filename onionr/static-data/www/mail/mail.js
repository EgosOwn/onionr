/*
    Onionr - P2P Anonymous Storage Network

    This file handles the mail interface

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

pms = ''
sentbox = ''
threadPart = document.getElementById('threads')
threadPlaceholder = document.getElementById('threadPlaceholder')
tabBtns = document.getElementById('tabBtns')
threadContent = {}
myPub = httpGet('/getActivePubkey')

function openThread(bHash, sender, date, sigBool){
    var messageDisplay = document.getElementById('threadDisplay')
    var blockContent = httpGet('/getblockbody/' + bHash)
    document.getElementById('fromUser').value = sender
    messageDisplay.innerText = blockContent
    var sigEl = document.getElementById('sigValid')
    var sigMsg = 'signature'

    if (sigBool){
        sigMsg = 'Good ' + sigMsg
        sigEl.classList.remove('danger')
    }
    else{
        sigMsg = 'Bad/no ' + sigMsg + ' (message could be fake)'
        sigEl.classList.add('danger')
    }
    sigEl.innerText = sigMsg
    overlay('messageDisplay')
}

function setActiveTab(tabName){
    threadPart.innerHTML = ""
    switch(tabName){
        case 'inbox':
            getInbox()
            break
        case 'sentbox':
            getSentbox()
            break
        case 'send message':
            overlay('sendMessage')
            break
    }
}

function loadInboxEntrys(bHash){
    fetch('/getblockheader/' + bHash, {
        headers: {
          "token": webpass
        }})
    .then((resp) => resp.json()) // Transform the data into json
    .then(function(resp) {
        //console.log(resp)
        var entry = document.createElement('div')
        var bHashDisplay = document.createElement('span')
        var senderInput = document.createElement('input')
        var subjectLine = document.createElement('span')
        var dateStr = document.createElement('span')
        var validSig = document.createElement('span')
        var humanDate = new Date(0)
        var metadata = resp['metadata']
        humanDate.setUTCSeconds(resp['meta']['time'])
        if (resp['meta']['signer'] != ''){
            senderInput.value = httpGet('/friends/getinfo/' + resp['meta']['signer'] + '/name')
        }
        if (resp['meta']['validSig']){
            validSig.innerText = 'Signature Validity: Good'
        }
        else{
            validSig.innerText = 'Signature Validity: Bad'
            validSig.style.color = 'red'
        }
        if (senderInput.value == ''){
            senderInput.value = resp['meta']['signer']
        }
        bHashDisplay.innerText = bHash.substring(0, 10)
        entry.setAttribute('hash', bHash)
        senderInput.readOnly = true
        dateStr.innerText = humanDate.toString()
        if (metadata['subject'] === undefined || metadata['subject'] === null) {
            subjectLine.innerText = '()'
        }
        else{
            subjectLine.innerText = '(' + metadata['subject'] + ')'
        }
        //entry.innerHTML = 'sender ' + resp['meta']['signer'] + ' - ' + resp['meta']['time'] 
        threadPart.appendChild(entry)
        entry.appendChild(bHashDisplay)
        entry.appendChild(senderInput)
        entry.appendChild(validSig)
        entry.appendChild(subjectLine)
        entry.appendChild(dateStr)
        entry.classList.add('threadEntry')

        entry.onclick = function(){
            openThread(entry.getAttribute('hash'), senderInput.value, dateStr.innerText, resp['meta']['validSig'])
        }
        
      }.bind(bHash))
}

function getInbox(){
    var showed = false
    var requested = ''
    for(var i = 0; i < pms.length; i++) {
        if (pms[i].trim().length == 0){
            continue
        }
        else{
            threadPlaceholder.style.display = 'none'
            showed = true
        }
        loadInboxEntrys(pms[i])
    }
    if (! showed){
        threadPlaceholder.style.display = 'block'
    }
}

function getSentbox(){
    fetch('/apipoints/mail/sentbox', {
        headers: {
          "token": webpass
        }})
    .then((resp) => resp.json()) // Transform the data into json
    .then(function(resp) {
        var keys = [];
        var entry = document.createElement('div')
        var entryUsed;
        for(var k in resp) keys.push(k);
        for (var i = 0; i < keys.length; i++){
            var entry = document.createElement('div')
            var obj = resp[i];
            var toLabel = document.createElement('span')
            toLabel.innerText = 'To: '
            var toEl = document.createElement('input')
            var preview = document.createElement('span')
            toEl.readOnly = true
            toEl.value = resp[keys[i]][1]
            preview.innerText = '(' + resp[keys[i]][2] + ')'
            entry.appendChild(toLabel)
            entry.appendChild(toEl)
            entry.appendChild(preview)
            entryUsed = resp[keys[i]]
            entry.onclick = function(){
                console.log(resp)
                showSentboxWindow(toEl.value, entryUsed[0])
            }
            threadPart.appendChild(entry)
        } 
        threadPart.appendChild(entry)
      }.bind(threadPart))
}

function showSentboxWindow(to, content){
    document.getElementById('toID').value = to
    document.getElementById('sentboxDisplayText').innerText = content
    overlay('sentboxDisplay')
}

fetch('/getblocksbytype/pm', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text()) // Transform the data into json
.then(function(data) {
    pms = data.split(',')
    setActiveTab('inbox')
  })

tabBtns.onclick = function(event){
    var children = tabBtns.children
    for (var i = 0; i < children.length; i++) {
        var btn = children[i]
        btn.classList.remove('activeTab')
    }
    event.target.classList.add('activeTab')
    setActiveTab(event.target.innerText.toLowerCase())
}


var idStrings = document.getElementsByClassName('myPub')
for (var i = 0; i < idStrings.length; i++){
    if (idStrings[i].tagName.toLowerCase() == 'input'){
        idStrings[i].value = myPub
    }
    else{
        idStrings[i].innerText = myPub
    }
}


for (var i = 0; i < document.getElementsByClassName('refresh').length; i++){
    document.getElementsByClassName('refresh')[i].style.float = 'right'
}

for (var i = 0; i < document.getElementsByClassName('closeOverlay').length; i++){
    document.getElementsByClassName('closeOverlay')[i].onclick = function(e){
        document.getElementById(e.target.getAttribute('overlay')).style.visibility = 'hidden'
    }
}

fetch('/friends/list', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.json()) // Transform the data into json
.then(function(resp) {
    var friendSelectParent = document.getElementById('friendSelect')
    var keys = [];
    var friend
    for(var k in resp) keys.push(k);

    friendSelectParent.appendChild(document.createElement('option'))
    for (var i = 0; i < keys.length; i++) {
        var option = document.createElement("option")
        var name = resp[keys[i]]['name']
        option.value = keys[i]
        if (name.length == 0){
            option.text = keys[i]
        }
        else{
            option.text = name
        }
        friendSelectParent.appendChild(option)
    }

    for (var i = 0; i < keys.length; i++){
        
        //friendSelectParent
        //alert(resp[keys[i]]['name'])
    }
})