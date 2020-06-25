/*
    Onionr - Private P2P Communication

    Show transport addresses

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
fetch('/gettoraddress', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text())
    .then(function(resp) {
        let torBoxes = document.getElementsByClassName('myTor')
        if (!resp.endsWith('.onion')){
            Array.from(torBoxes).forEach(element => {
                element.parentElement.parentElement.remove()
            })
        }
        Array.from(torBoxes).forEach(element => {
            element.value = resp  
        })

    })

Array.from(document.getElementsByClassName('myTorCopy')).forEach(element => {
    element.onclick = function(){
        var copyText = document.getElementsByClassName('myTor')[0]
        copyText.select()
        document.execCommand("copy")
        if (typeof PNotify != 'undefined'){
            PNotify.success({
                text: "Copied to clipboard"
            })
        }
    }
})