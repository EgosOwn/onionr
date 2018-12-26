webpassword = ''
requested = {}
document.getElementById('feed').innerText = 'none :)'

function httpGet(theUrl) {
    var xmlHttp = new XMLHttpRequest()
    xmlHttp.open( "GET", theUrl, false ) // false for synchronous request
    xmlHttp.setRequestHeader('token', webpassword)
    xmlHttp.send( null )
    return xmlHttp.responseText
}
function appendMessages(msg){
    document.getElementById('feed').append(msg)
    document.getElementById('feed').appendChild(document.createElement('br'))
}

function getBlocks(){
    var feedText =  httpGet('/getblocksbytype/txt')
    var blockList = feedText.split(',')
    for (i = 0; i < blockList.length; i++){
        bl = httpGet('/gethtmlsafeblockdata/' + blockList[i])
        appendMessages(bl)
    }
}

document.getElementById('webpassword').oninput = function(){
    webpassword = document.getElementById('webpassword').value
}

document.getElementById('refreshFeed').onclick = function(){
    getBlocks()
}