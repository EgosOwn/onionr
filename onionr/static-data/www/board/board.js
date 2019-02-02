webpassword = ''
requested = []

document.getElementById('webpassWindow').style.display = 'block';

var windowHeight = window.innerHeight;
document.getElementById('webpassWindow').style.height = windowHeight + "px";

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
            bl = httpGet('/gethtmlsafeblockdata/' + blockList[i])
            appendMessages(bl)
            requested.push(blockList[i])
            }
        }
}

document.getElementById('registerPassword').onclick = function(){
    webpassword = document.getElementById('webpassword').value
    if (httpGet('/ping') === 'pong!'){
        document.getElementById('webpassWindow').style.display = 'none'
        getBlocks()
    }
    else{
        alert('Sorry, but that password appears invalid.')
    }
}

document.getElementById('refreshFeed').onclick = function(){
    getBlocks()
}