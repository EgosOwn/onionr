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
replyBtn = document.getElementById('replyBtn')

function openReply(bHash){
    var inbox = document.getElementsByClassName('threadEntry')
    var entry = ''
    var friendName = ''
    var key = ''
    for(var i = 0; i < inbox.length; i++) {
        if (inbox[i].getAttribute('data-hash') === bHash){
            entry = inbox[i]
        }
    }
    if (entry.getAttribute('data-nameSet') == 'true'){
        document.getElementById('friendSelect').value = entry.getElementsByTagName('input')[0].value
    }
    key = entry.getAttribute('data-pubkey')
    document.getElementById('draftID').value = key
    setActiveTab('send message')
}

function openThread(bHash, sender, date, sigBool, pubkey){
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
        sigMsg = 'Bad/no ' + sigMsg + ' (message could be impersonating someone)'
        sigEl.classList.add('danger')
        replyBtn.style.display = 'none'
    }
    sigEl.innerText = sigMsg
    overlay('messageDisplay')
    replyBtn.onclick = function(){
        openReply(bHash)
    }
}

function setActiveTab(tabName){
    threadPart.innerHTML = ""
    switch(tabName){
        case 'inbox':
            refreshPms()
            break
        case 'sentbox':
            getSentbox()
            break
        case 'send message':
            overlay('sendMessage')
            break
    }
}

function deleteMessage(bHash){
    fetch('/mail/deletemsg/' + bHash, {
        "method": "post",
        headers: {
            "token": webpass
        }})
    .then((resp) => resp.text()) // Transform the data into json
    .then(function(resp) {
    })
}

function loadInboxEntries(bHash){
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
        var deleteBtn = document.createElement('button')
        var humanDate = new Date(0)
        var metadata = resp['metadata']
        humanDate.setUTCSeconds(resp['meta']['time'])
        validSig.style.display = 'none'
        if (resp['meta']['signer'] != ''){
            senderInput.value = httpGet('/friends/getinfo/' + resp['meta']['signer'] + '/name')
        }
        if (! resp['meta']['validSig']){
            validSig.style.display = 'inline'
            validSig.innerText = 'Signature Validity: Bad'
            validSig.style.color = 'red'
        }
        entry.setAttribute('data-nameSet', true)
        if (senderInput.value == ''){
            senderInput.value = resp['meta']['signer']
            entry.setAttribute('data-nameSet', false)
        }
        bHashDisplay.innerText = bHash.substring(0, 10)
        entry.setAttribute('data-hash', bHash)
        entry.setAttribute('data-pubkey', resp['meta']['signer'])
        senderInput.readOnly = true
        dateStr.innerText = humanDate.toString()
        deleteBtn.innerText = 'X'
        deleteBtn.classList.add('dangerBtn', 'deleteBtn')
        if (metadata['subject'] === undefined || metadata['subject'] === null) {
            subjectLine.innerText = '()'
        }
        else{
            subjectLine.innerText = '(' + metadata['subject'] + ')'
        }
        //entry.innerHTML = 'sender ' + resp['meta']['signer'] + ' - ' + resp['meta']['time'] 
        threadPart.appendChild(entry)
        entry.appendChild(deleteBtn)
        entry.appendChild(bHashDisplay)
        entry.appendChild(senderInput)
        entry.appendChild(subjectLine)
        entry.appendChild(dateStr)
        entry.appendChild(validSig)
        entry.classList.add('threadEntry')

        entry.onclick = function(event){
            if (event.target.classList.contains('deleteBtn')){
                return
            }
            openThread(entry.getAttribute('data-hash'), senderInput.value, dateStr.innerText, resp['meta']['validSig'], entry.getAttribute('data-pubkey'))
        }

        deleteBtn.onclick = function(){
            entry.parentNode.removeChild(entry);
            deleteMessage(entry.getAttribute('data-hash'))
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
        loadInboxEntries(pms[i])
    }
    if (! showed){
        threadPlaceholder.style.display = 'block'
    }
}

function getSentbox(){
    fetch('/mail/getsentbox', {
        headers: {
          "token": webpass
        }})
    .then((resp) => resp.json()) // Transform the data into json
    .then(function(resp) {
        var keys = [];
        var entry = document.createElement('div')
        for(var k in resp) keys.push(k);
        if (keys.length == 0){
            threadPart.innerHTML = "nothing to show here yet."
        }
        for (var i = 0; i < keys.length; i++){
            var entry = document.createElement('div')
            var obj = resp[i]
            var toLabel = document.createElement('span')
            toLabel.innerText = 'To: '
            var toEl = document.createElement('input')
            var preview = document.createElement('span')
            var deleteBtn = document.createElement('button')
            var message = resp[i]['message']
            deleteBtn.classList.add('deleteBtn', 'dangerBtn')
            deleteBtn.innerText = 'X'
            toEl.readOnly = true
            if (resp[i]['name'] == null){
                toEl.value = resp[i]['peer']
            }
            else{
                toEl.value = resp[i]['name']
            }
            preview.innerText = '(' + resp[i]['subject'] + ')'
            entry.setAttribute('data-hash', resp[i]['hash'])
            entry.appendChild(deleteBtn)
            entry.appendChild(toLabel)
            entry.appendChild(toEl)
            entry.appendChild(preview)
            entry.onclick = (function(tree, el, msg) {return function() {
                console.log(resp)
                if (! entry.classList.contains('deleteBtn')){
                    showSentboxWindow(el.value, msg)
                }
            };})(entry, toEl, message);
            
            deleteBtn.onclick = function(){
                entry.parentNode.removeChild(entry);
                deleteMessage(entry.getAttribute('data-hash'))
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

function refreshPms(){
fetch('/mail/getinbox', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text()) // Transform the data into json
.then(function(data) {
    pms = data.split(',')
    getInbox()
  })
}

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
setActiveTab('inbox')