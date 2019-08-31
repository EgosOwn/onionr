requested = []

var windowHeight = window.innerHeight;
webpassword = webpass
newPostForm = document.getElementById('addMsg')
firstLoad = true
lastLoadedBoard = 'global'

function appendMessages(msg){
    var humanDate = new Date(0)
    if (msg.length == 0){
        return
    }
    var msg = JSON.parse(msg)
    var dateEl = document.createElement('div')
    var el = document.createElement('div')
    var msgDate = msg['meta']['time']
    if (msgDate === undefined){
        msgDate = 'unknown'
    }
    else{
        humanDate.setUTCSeconds(msgDate)
        msgDate = humanDate.toDateString()
    }
    el.className = 'entry'
    el.innerText = msg['content']

    /* Template Test */
    // Test to see if the browser supports the HTML template element by checking
    // for the presence of the template element's content attribute.
    if ('content' in document.createElement('template')) {

        // Instantiate the table with the existing HTML tbody
        // and the row with the template
        var template = document.getElementById('cMsgTemplate')

        // Clone the new row and insert it into the table
        var feed = document.getElementById("feed")
        var clone = document.importNode(template.content, true);
        var div = clone.querySelectorAll("div")
        div[2].textContent = msg['content']
        if (typeof msg['meta']['signer'] != 'undefined'){
            div[3].textContent = msg['meta']['signer'].substr(0, 5)
            div[3].title = msg['meta']['signer']
        }
        div[4].textContent = msgDate

        if (firstLoad){
            feed.appendChild(clone)
        }
        else{
            feed.prepend(clone)
        }

    } else {
    // Find another way to add the rows to the table because 
    // the HTML template element is not supported.
    }
}

function getBlocks(){
    var feed = document.getElementById("feed")
    var ch = document.getElementById('feedIDInput').value
    if (lastLoadedBoard !== ch){
        while (feed.firstChild) {
            feed.removeChild(feed.firstChild);
        }
        requested = [] // reset requested list
    }

    lastLoadedBoard = ch
    if (document.getElementById('none') !== null){
        document.getElementById('none').remove();

    }
    var feedText =  httpGet('/flow/getpostsbyboard/' + ch)
    var blockList = feedText.split(',').reverse()
    console.log(blockList)
    for (i = 0; i < blockList.length; i++){
        while (blockList[i].length < 64) blockList[i] = "0" + blockList[i]
        if (! requested.includes(blockList[i])){
            if (blockList[i].length == 0){
                continue
            }
            bl = httpGet('/getblockdata/' + blockList[i])
            appendMessages(bl)
            requested.push(blockList[i])
            }
    }
    firstLoad = false
}

document.getElementById('refreshFeed').onclick = function(){
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
        }})
    .then((resp) => resp.text()) // Transform the data into json
    .then(function(data) {
        newPostForm.style.display = 'block'
        if (data == 'failure due to duplicate insert'){
            alert('This message is already queued')
            return
        }
        setTimeout(function(){getBlocks()}, 3000)
      })
    return false
}