/*
    Onionr - Private P2P Communication

    Checks if the api server is still online

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
apiOnline = true
async function doPing(){
    out = setTimeout(function(){
        if (apiOnline){
        PNotify.notice('Connection lost with API server')
        }
        apiOnline = false
    }, 10000)
return await fetch('/ping', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(resp) {
        if (!apiOnline){PNotify.success('API server connection reestablished')}
        apiOnline = true
        clearTimeout(out)
        return resp
    })
}

let pingCheck = async function(){
    if (document.hidden){return}
    result = await doPing()

}

pingCheckInterval = setInterval(function(){pingCheck()}, 3000)
