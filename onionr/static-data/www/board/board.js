requested = []

var windowHeight = window.innerHeight;
webpassword = webpass
newPostForm = document.getElementById('addMsg')

function appendMessages(msg){
    var humanDate = new Date(0)
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
    return false
}