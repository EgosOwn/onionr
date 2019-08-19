/*
    Onionr - Private P2P Communication

    Onionr chat message objects

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
chatMessages = {}
let Message = class {
    constructor(text, peer, outgoing){
        this.text = text // raw message string
        this.peer = peer // peer by public key
        this.outgoing = outgoing // boolean. false = outgoing message
        this.time = new Date().toISOString() // store message time
        this.tempIdentifier = Math.floor(Math.random() * 100000000000000000) // assign a random id, doesnt need to be secure

        // Add the message to the peer message feed object chatMessages
        if (chatMessages.hasOwnProperty(peer)){
            chatMessages[peer].push(this)
        }
        else{
            chatMessages[peer] = [this]
        }
    }
}
