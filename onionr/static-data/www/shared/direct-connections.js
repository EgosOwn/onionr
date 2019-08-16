/*
    Onionr - Private P2P Communication

    Functions to detect

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
direct_connections = {}

let waitForConnection = function(pubkey){
    fetch('/dc-client/isconnected/' + pubkey, {
        headers: {
          "token": webpass
        }})
    .then(function(resp) {
        if (resp.ok){
            if (resp.text === ""){
                // Try to get the client address again again in a few seconds
                setTimeout(function(){waitForConnection(pubkey)}, 3000)
            }
            else{
                // add to the dc object
                direct_connections[pubkey] = resp
            }
        }
    })   
}

let createConnection = function(pubkey){
    if (direct_connections.hasOwnProperty(pubkey)){
        return
    }
    fetch('/dc-client/connect/' + pubkey, {
        headers: {
          "token": webpass
        }})
    .then(function(resp) {
        if (resp.ok){
            if (resp.text === "pending"){
                setTimeout(function(){waitForConnection(pubkey)}, 3000)
            }
        }
    })
}