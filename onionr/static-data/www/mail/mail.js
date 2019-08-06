/*
    Onionr - Private P2P Communication

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
replyBtn = document.getElementById('replyBtn')
addUnknownContact = document.getElementById('addUnknownContact')

function addContact(pubkey, friendName){
    fetch('/friends/add/' + pubkey, {
        method: 'POST',
        headers: {
          "token": webpass
        }}).then(function(data) {
            if (friendName.trim().length > 0){
                post_to_url('/friends/setinfo/' + pubkey + '/name', {'data': friendName, 'token': webpass})
            }
        })
}

function openReply(bHash, quote, subject){
    var inbox = document.getElementsByClassName('threadEntry')
    var entry = ''
    var friendName = ''
    var key = ''
    for(var i = 0; i < inbox.length; i++) {
        if (inbox[i].getAttribute('data-hash') === bHash){
            entry = inbox[i]
        }
    }
    if (entry.getAttribute('data-nameset') == 'true'){
        document.getElementById('friendSelect').value = entry.getElementsByTagName('input')[0].value
    }
    key = entry.getAttribute('data-pubkey')
    document.getElementById('draftID').value = key
    document.getElementById('draftSubject').value = 'RE: ' + subject

    // Add quoted reply
    var splitQuotes = quote.split('\n')
    for (var x = 0; x < splitQuotes.length; x++){
        splitQuotes[x] = '> ' + splitQuotes[x]
    }
    quote = '\n' + key.substring(0, 12) + ' wrote:' + '\n' + splitQuotes.join('\n')
    document.getElementById('draftText').value = quote
    setActiveTab('compose')
}

function openThread(bHash, sender, date, sigBool, pubkey, subjectLine){
    addUnknownContact.style.display = 'none'
    var messageDisplay = document.getElementById('threadDisplay')
    var blockContent = httpGet('/getblockbody/' + bHash)

    document.getElementById('fromUser').value = sender || 'Anonymous'
    document.getElementById('subjectView').innerText = subjectLine
    messageDisplay.innerText = blockContent
    var sigEl = document.getElementById('sigValid')
    var sigMsg = 'signature'

    // show add unknown contact button if peer is unknown but still has pubkey
    if (sender === pubkey && sender !== myPub && sigBool){
        addUnknownContact.style.display = 'inline'
    }

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
        openReply(bHash, messageDisplay.innerText, subjectLine)
    }
    addUnknownContact.onclick = function(){
        var friendName = prompt("Enter an alias for this contact:")
        if (friendName === null || friendName.length == 0){
            return
        }
        addContact(pubkey, friendName)
    }
}

function setActiveTab(tabName){
    threadPart.innerHTML = ""
    window.inboxActive = false
    switch(tabName){
        case 'inbox':
            window.inboxActive = true
            refreshPms()
            getInbox()
            break
        case 'sent':
            getSentbox()
            break
        case 'compose':
            overlay('sendMessage')
            setActiveTab('inbox')
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

function mailPing(){
    fetch('/mail/ping', {
        "method": "get",
        headers: {
            "token": webpass
        }})
    .then(function(resp) {
        var pings = document.getElementsByClassName('mailPing')
        if (resp.ok){
            for (var i=0; i < pings.length; i++){
                pings[i].style.display = 'none';
            }
        }
        else{
            for (var i=0; i < pings.length; i++){
                pings[i].style.display = 'block';
            }
        }
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
        humanDate = humanDate.toString()
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
            senderInput.value = resp['meta']['signer'] || 'Anonymous'
            entry.setAttribute('data-nameSet', false)
        }
        //bHashDisplay.innerText = bHash.substring(0, 10)
        entry.setAttribute('data-hash', bHash)
        entry.setAttribute('data-pubkey', resp['meta']['signer'])
        senderInput.readOnly = true
        dateStr.innerText = humanDate.substring(0, humanDate.indexOf('('))
        deleteBtn.classList.add('delete', 'deleteBtn')
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
            openThread(entry.getAttribute('data-hash'), senderInput.value, dateStr.innerText, resp['meta']['validSig'], entry.getAttribute('data-pubkey'), subjectLine.innerText)
        }

        deleteBtn.onclick = function(){
            entry.parentNode.removeChild(entry);
            deleteMessage(entry.getAttribute('data-hash'))
        }
        
      }.bind(bHash))
}

function getInbox(){
    if (! window.inboxActive){
        return
    }
    var els = document.getElementsByClassName('threadEntry')
    var showed = false
    var requested = ''
    for(var i = 0; i < pms.length; i++) {
        var add = true
        if (pms[i].trim().length == 0){
            threadPart.innerText = 'No messages to show ¯\\_(ツ)_/¯'
            continue
        }
        else{
            threadPlaceholder.style.display = 'none'
            showed = true
        }
        for (var x = 0; x < els.length; x++){
            if (pms[i] === els[x].getAttribute('data-hash')){
                add = false
            }
        }
        if (add && window.inboxActive) {
            loadInboxEntries(pms[i])
        }
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
        for (var i = 0; i < keys.length; i++) (function(i, resp){
            var entry = document.createElement('div')
            var obj = resp[i]
            var toLabel = document.createElement('span')
            toLabel.innerText = 'To: '
            var toEl = document.createElement('input')
            var sentDate = document.createElement('span')
            var humanDate = new Date(0)
            humanDate.setUTCSeconds(resp[i]['date'])
            humanDate = humanDate.toString()
            var preview = document.createElement('span')
            var deleteBtn = document.createElement('button')
            var message = resp[i]['message']
            deleteBtn.classList.add('deleteBtn', 'delete')
            toEl.readOnly = true
            sentDate.innerText = humanDate.substring(0, humanDate.indexOf('('))
            if (resp[i]['name'] == null || resp[i]['name'].toLowerCase() == 'anonymous'){
                toEl.value = resp[i]['peer']
            }
            else{
                toEl.value = resp[i]['name']
            }
            preview.innerText = '(' + resp[i]['subject'] + ')'
            entry.classList.add('sentboxList')
            entry.setAttribute('data-hash', resp[i]['hash'])
            entry.appendChild(deleteBtn)
            entry.appendChild(toLabel)
            entry.appendChild(toEl)
            entry.appendChild(preview)
            entry.appendChild(sentDate)

            threadPart.appendChild(entry)

            entry.onclick = function(e){
                if (e.target.classList.contains('deleteBtn')){
                    deleteMessage(e.target.parentNode.getAttribute('data-hash'))
                    e.target.parentNode.parentNode.removeChild(e.target.parentNode)
                    return
                }
                showSentboxWindow(toEl.value, message)
            }
        })(i, resp)
        threadPart.appendChild(entry)
      }.bind(threadPart))
}

function showSentboxWindow(to, content){
    document.getElementById('toID').value = to
    document.getElementById('sentboxDisplayText').innerText = content
    overlay('sentboxDisplay')
}

function refreshPms(callNext){
    if (! window.inboxActive){
        return
    }
fetch('/mail/getinbox', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text()) // Transform the data into json
.then(function(data) {
    pms = data.split(',')
    if (callNext){
        getInbox()
    }
  })
}

tabBtns.onclick = function(event){
    var children = tabBtns.children[0].children
    for (var i = 0; i < children.length; i++) {
        var btn = children[i]
        btn.classList.remove('is-active')
    }
    event.target.parentElement.parentElement.classList.add('is-active')
    setActiveTab(event.target.innerText.toLowerCase())
}

for (var i = 0; i < document.getElementsByClassName('refresh').length; i++){
    document.getElementsByClassName('refresh')[i].style.float = 'right'
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
        var name = resp[keys[i]]['name'] || ""
        option.value = keys[i]
        if (name.length == 0){
            option.text = keys[i]
        }
        else{
            option.text = name
        }
        friendSelectParent.appendChild(option)
    }
})
setActiveTab('inbox')

setInterval(function(){mailPing()}, 10000)
mailPing()
window.inboxInterval = setInterval(function(){refreshPms(true)}, 3000)
refreshPms(true)