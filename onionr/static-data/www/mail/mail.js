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
            var bHash = pms[i].substring(0, 10)
            var bHashDisplay = document.createElement('span')
            var senderInput = document.createElement('input')
            var subjectLine = document.createElement('span')
            var dateStr = document.createElement('span')
            var humanDate = new Date(0)
            humanDate.setUTCSeconds(resp['meta']['time'])
            senderInput.value = resp['meta']['signer']
            bHashDisplay.innerText = bHash
            senderInput.readOnly = true
            dateStr.innerText = humanDate.toString()
            if (resp['metadata']['subject'] === undefined || resp['metadata']['subject'] === null) {
                subjectLine.innerText = '()'
            }
            else{
                subjectLine.innerText = '(' + resp['metadata']['subject'] + ')'
            }
            //entry.innerHTML = 'sender ' + resp['meta']['signer'] + ' - ' + resp['meta']['time'] 
            threadPart.appendChild(entry)
            entry.appendChild(bHashDisplay)
            entry.appendChild(senderInput)
            entry.appendChild(subjectLine)
            entry.appendChild(dateStr)
            
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

