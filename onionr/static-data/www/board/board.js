requested = []

var windowHeight = window.innerHeight;
webpassword = webpass
function httpGet(theUrl) {
    var xmlHttp = new XMLHttpRequest()
    xmlHttp.open( "GET", theUrl, false ) // false for synchronous request
    xmlHttp.setRequestHeader('token', webpassword)
    xmlHttp.send( null )
    if (xmlHttp.status == 200){
        return xmlHttp.responseText
    }
    else{
        return "";
    }
}
function appendMessages(msg){
    el = document.createElement('div')
    el.className = 'entry'
    el.innerText = msg
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