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

            var bHashDisplay = document.createElement('a')
            var senderInput = document.createElement('input')
            var subjectLine = document.createElement('span')
            var dateStr = document.createElement('span')
            var humanDate = new Date(0)
            humanDate.setUTCSeconds(resp['meta']['time'])
            senderInput.value = resp['meta']['signer']
            bHashDisplay.innerText = pms[i - 1].substring(0, 10)
            bHashDisplay.setAttribute('hash', pms[i - 1]);
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
            
          }.bind([pms, i]))
    }

}

fetch('/getblocksbytype/pm', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text()) // Transform the data into json
.then(function(data) {
    pms = data.split(',')
    getInbox(pms)
  })

