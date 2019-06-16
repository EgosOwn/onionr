requested = []

var windowHeight = window.innerHeight;
webpassword = webpass
newPostForm = document.getElementById('addMsg')

function appendMessages(msg){
    var humanDate = new Date(0)
    if (msg.length == 0){
        return
    }
    var msg = JSON.parse(msg)
    var dateEl = document.createElement('span')
    var el = document.createElement('div')
    var msgDate = msg['meta']['time']
    if (msgDate === undefined){
        msgDate = 'unknown'
    }
    else{
        humanDate.setUTCSeconds(msgDate)
        msgDate = humanDate.toDateString() + ' ' + humanDate.toTimeString()
    }
    dateEl.textContent = msgDate
    el.className = 'entry'
    el.innerText = msg['content']
    document.getElementById('feed').appendChild(dateEl)
    document.getElementById('feed').appendChild(el)
    document.getElementById('feed').appendChild(document.createElement('br'))
}

function getBlocks(){
    if (document.getElementById('none') !== null){
        document.getElementById('none').remove();

    }
    var feedText =  httpGet('/getblocksbytype/txt')
    var blockList = feedText.split(',')
    for (i = 0; i < blockList.length; i++){
        if (! requested.includes(blockList[i])){
            bl = httpGet('/getblockdata/' + blockList[i])
            appendMessages(bl)
            requested.push(blockList[i])
            }
        }
}

document.getElementById('refreshFeed').onclick = function(){
    getBlocks()
}

newPostForm.onsubmit = function(){
    var message = document.getElementById('newMsgText').value
    var postData = {'message': message, 'type': 'txt', 'encrypt': false}
    postData = JSON.stringify(postData)
    newPostForm.style.display = 'none'
    fetch('/insertblock', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then((resp) => resp.text()) // Transform the data into json
    .then(function(data) {
        newPostForm.style.display = 'block'
        alert('Queued for submission!')
      })
    return false
}