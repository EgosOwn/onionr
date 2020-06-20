fetch('/config/get/transports.tor', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(resp) {
        var displays = document.getElementsByClassName('torInfo')
        if (resp == true){
            var torSource = new EventSourcePolyfill('/torcircuits', {
                headers: {
                    "token": webpass
                }
              })
            displays = document.getElementsByClassName('torInfo')
            
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
        }
        else{
            console.debug("No tor enabled, not getting tor stats")
            displays[0].innerHTML = "<i class=\"fas fa-plug\"></i> Tor is disabled"
        }
})
