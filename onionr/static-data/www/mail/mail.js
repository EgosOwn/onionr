pms = ''
threadPart = document.getElementById('threads')
function getInbox(){
    for(var i = 0; i < pms.length; i++) {
        fetch('/getblockdata/' + pms[i], {
            headers: {
              "token": webpass
            }})
        .then((resp) => resp.json()) // Transform the data into json
        .then(function(resp) {
            var entry = document.createElement('div')
            entry.innerHTML = resp['meta']['time'] + ' - ' + resp['meta']['signer']
            threadPart.appendChild(entry)
          })
    }

}

fetch('/getblocksbytype/pm', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text()) // Transform the data into json
.then(function(data) {
    pms = data.split(',')
    getInbox()
  })

