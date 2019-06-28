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
    var dateEl = document.createElement('div')
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

    /* Template Test */
    // Test to see if the browser supports the HTML template element by checking
    // for the presence of the template element's content attribute.
    if ('content' in document.createElement('template')) {

        // Instantiate the table with the existing HTML tbody
        // and the row with the template
        var template = document.getElementById('cMsgTemplate');

        // Clone the new row and insert it into the table
        var feed = document.getElementById("feed");
        var clone = document.importNode(template.content, true);
        var div = clone.querySelectorAll("div");
        div[2].textContent = msg['content'];
        div[3].textContent = msgDate;

        feed.appendChild(clone);

    } else {
    // Find another way to add the rows to the table because 
    // the HTML template element is not supported.
    }
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

window.onload = function() {
    getBlocks();
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