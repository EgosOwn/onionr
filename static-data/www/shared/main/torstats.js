/*
    Onionr - Private P2P Communication

    Get and show tor statistics

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
*/
fetch('/config/get/transports.tor', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(resp) {
        var displays = document.getElementsByClassName('torInfo')
        if (resp == "true"){
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
