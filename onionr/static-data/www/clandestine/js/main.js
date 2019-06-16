friendList = []
convoListElement = document.getElementsByClassName('conversationList')[0]

function createConvoList(){
    for (var x = 0; x < friendList.length; x++){
        var convoEntry = document.createElement('div')
        convoEntry.classList.add('convoEntry')
        convoEntry.setAttribute('data-pubkey', friendList[x])
        convoEntry.innerText = friendList[x]
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
        friendList.push(keys[i])
    }
    createConvoList()
})