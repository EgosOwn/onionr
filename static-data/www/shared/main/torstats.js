var torSource = new EventSourcePolyfill('/torcircuits', {
    headers: {
        "token": webpass
    }
  })
var displays = document.getElementsByClassName('torInfo')

for (x = 0; x < displays.length; x++){
    displays[x].style.whiteSpace = 'pre'
}

torSource.onmessage = function(e){
    let data = JSON.parse(e.data)
    let i = 0
    let displaying = true
    for (x = 0; x < displays.length; x++){
       let circuitCount = Object.keys(data).length
       let node = Object.keys(data)[0]
       if (circuitCount > 0){
           displays[x].innerText = "Using " + circuitCount + " Tor circuits with " + data[node]['nodes'][0]['finger'] + " as guard.\nGuard nick: " + data[node]['nodes'][0]['nick']
       }
       else{
           displays[x].innerText = "Using 0 Tor circuits."
       }

    }
}
