/*
    Onionr - Private P2P Communication

    This file handles the mail interface

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

shutdownBtn = document.getElementById('shutdownNode')
restartBtn = document.getElementById('restartNode')

shutdownBtn.onclick = function(){
    if (! nowebpass){
        if (confirm("Really shutdown Onionr?")){
            httpGet('/shutdownclean')
            overlay('shutdownNotice')
        }
    }
}

if (document.location.pathname != "/onboarding/"){

    restartBtn.onclick = function(){
        if (! nowebpass){
            if (confirm("Really restart Onionr?")){
                fetch('/restartclean', {
                    headers: {
                    "token": webpass
                }})
                PNotify.notice('Node is restarting')
            }
        }
    }

    fetch('/config/get/onboarding.done', {
        method: 'GET',
        headers: {
            "content-type": "application/json",
            "token": webpass
        }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(data) {
        if (data === 'false'){
            window.location.href = window.location.pathname = "/onboarding/" + window.location.hash
        }
        })
}