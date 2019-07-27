friendList = {}
convoListElement = document.getElementsByClassName('conversationList')[0]

function createConvoList(){
    console.log(friendList)

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