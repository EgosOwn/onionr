/*
    Onionr - Private P2P Communication

    This file handles the boards/circles interface

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
requested = []
newPostForm = document.getElementById('addMsg')
firstLoad = true
lastLoadedBoard = 'global'
loadingMessage = document.getElementById('loadingBoard')
loadedAny = false
loadingTimeout = 8000

let toggleLoadingMessage = function(){
    switch (loadingMessage.style.display){
        case "inline-block":
            loadingMessage.style.display = "none"
            break;
        default:
            loadingMessage.style.display = "initial"
            break;
    }
}

fetch('/circles/version', {
    method: 'GET',
    headers: {
      "token": webpass
}})
.then((ver) => ver.text())
.then(function(ver) {
    document.getElementById('circlesVersion').innerText = ver
})

function appendMessages(msg, blockHash, beforeHash, channel) {
    if (channel !== document.getElementById('feedIDInput').value) return // ignore if channel name isn't matching
    if (msg.length == 0) return // ignore empty messages

    var humanDate = new Date(0)
    var msgDate = msg['meta']['time']
    var feed = document.getElementById("feed")
    var beforeEl = null

    if (msgDate === undefined){
        msgDate = 'unknown'
    } else {
        humanDate.setUTCSeconds(msgDate)
        msgDate = humanDate.toLocaleString("en-US", {timeZone: "Etc/GMT"})
    }

    var el = document.createElement('div')
    el.innerText = msg['content']

    if (beforeHash !== null) {
        for (i = 0; i < feed.children.length; i++) {
            if (feed.children[i].getAttribute('data-bl') === beforeHash) {
                beforeEl = feed.children[i]
            }
        }
    }

    /* Template Test */
    // Test to see if the browser supports the HTML template element by checking
    // for the presence of the template element's content attribute.
    if ('content' in document.createElement('template')) {

        // Instantiate the table with the existing HTML tbody
        // and the row with the template
        var template = document.getElementById('cMsgTemplate')

        // Clone the new row and insert it into the table
        var clone = document.importNode(template.content, true)
        var div = clone.querySelectorAll("div")
        var identicon = clone.querySelectorAll("img")

        div[0].classList.add('entry')
        div[0].setAttribute('timestamp', msg['meta']['time'])

        div[0].setAttribute('data-bl', blockHash)
        div[2].textContent = msg['content']
        if (typeof msg['meta']['signer'] != 'undefined' && msg['meta']['signer'].length > 0){
            div[3].textContent = msg['meta']['signer'].substr(0, 5)
            setHumanReadableIDOnPost(div[3], msg['meta']['signer'])
            div[3].onclick = function(){
                navigator.clipboard.writeText(div[3].title).then(function() {
                    PNotify.notice("Copied poster identity to clipboard")
                })
            }
            div[3].title = msg['meta']['signer']
            userIcon(msg['meta']['signer']).then(function(data){
                identicon[0].src = "data:image/svg+xml;base64," + data
            })
        }
        else{
            identicon[0].remove()
        }
        div[4].textContent = msgDate

        loadingMessage.style.display = "none"
        loadedAny = true
        if (firstLoad){
            //feed.appendChild(clone)
            feed.prepend(clone)
            firstLoad = false
        }
        else{
            if (beforeEl === null){
                feed.prepend(clone)
            }
            else{
                beforeEl.insertAdjacentElement("beforebegin", clone.children[0])
            }

        }
    }
}

function getBlocks(){
    var feed = document.getElementById("feed")
    var ch = document.getElementById('feedIDInput').value
    if (lastLoadedBoard !== ch){
        requested = []

        toggleLoadingMessage()
        loadedAny = false

        while (feed.firstChild) feed.removeChild(feed.firstChild); // remove all messages from feed

        setTimeout(function(){
            if (! loadedAny && ch == document.getElementById('feedIDInput').value){
                PNotify.notice("There are no posts for " + ch + ". You can be the first!")
            }
        }, loadingTimeout)
    }

    lastLoadedBoard = ch
    if (document.getElementById('none') !== null){
        document.getElementById('none').remove();

    }

    fetch('/circles/getpostsbyboard/' + ch, {
        method: 'GET',
        headers: {
          "token": webpass
    }})
    .then((resp) => resp.text())
    .then(function(feedText) {
        var blockList = feedText.split(',')

        for (i = 0; i < blockList.length; i++){
            blockList[i] = "0".repeat(64 - blockList[i].length) + blockList[i] // pad hash with zeroes

            if (! requested.includes(blockList[i])){
                if (blockList[i].length == 0) continue
                else requested.push(blockList[i])
                loadMessage(blockList[i], blockList, i, ch);
            }
        }
        sortEntries()
    })
}

function loadMessage(blockHash, blockList, count, channel){
    if (blockHash == '0000000000000000000000000000000000000000000000000000000000000000'){
        return
    }
    fetch('/getblockdata/' + blockHash, {
        method: 'GET',
        headers: {
          "token": webpass
    }}).then(function(response) {
        if (!response.ok) {
            let on404 = function() {
            if (response.status == 404){
                fetch('/circles/removefromcache/' + channel + '/' + blockHash, {
                    method: 'POST',
                    headers: {
                        "content-type": "application/json",
                        "token": webpass
                    }
                })
            }
            else{
                console.log(error)
            }
            }()
            return
        }
        response.json().then(function(data){
            let before = blockList[count - 1]
            let delay = 2000
            if (typeof before == "undefined"){
                before = null
            } else {
                let existing = document.getElementsByClassName('cMsgBox')
                for (x = 0; x < existing.length; x++){
                    if (existing[x].getAttribute('data-bl') === before){
                        delay = 0
                    }
                }
            }
            setTimeout(function(){appendMessages(data, blockHash, before, channel)}, delay)
        })
        return response;
    })
}

document.getElementById('refreshFeed').onclick = function() {
    getBlocks()
}

newPostForm.onsubmit = function(){
    var message = document.getElementById('newMsgText').value
    var channel = document.getElementById('feedIDInput').value
    var meta = {'ch': channel}
    let doSign = document.getElementById('postAnon').checked
    var postData = {'message': message, 'sign': doSign, 'type': 'brd', 'encrypt': false, 'meta': JSON.stringify(meta)}
    postData = JSON.stringify(postData)
    newPostForm.style.display = 'none'
    fetch('/insertblock', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }
    })
    .then((resp) => resp.text())
    .then(function(data) {
        newPostForm.style.display = 'block'
        if (data == 'failure due to duplicate insert'){
            PNotify.error({
                text: "This message is already queued"
            })
            return
        }
        PNotify.success({
            text: "Message queued for posting"
        })
        setTimeout(function(){getBlocks()}, 500)
    })
    return false
}

resetCirclePickers = function(){
    document.getElementById('recommendedBoards').value = ""
    document.getElementById('popularBoards').value = ""
}

document.getElementById('feedIDInput').onchange = resetCirclePickers

