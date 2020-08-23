/*
    Onionr - Private P2P Communication

    Get and show recent blocks

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
var getRecent = function(){
    var recentSource = new EventSourcePolyfill('/recentblocks', {
        headers: {
            "token": webpass
        }
    })


    recentSource.onmessage = function(e){
        if (e.data == "none"){
            return
        }
        var existing = document.getElementsByClassName('recentBlockList')[0].innerText;
        let data = JSON.parse(e.data)
        Object.entries(data.blocks).forEach(([key, value]) => {
            if (existing.includes(key)){
                return
            }
            existing =  "\n" + key + " - " + value + "\n" + existing
        })
        document.getElementsByClassName('recentBlockList')[0].innerText = existing
        console.debug(data)
    }
    return recentSource
}
recentSource = getRecent()
function toggleRecentStream() {
    if (document.hidden){
        console.debug("Stopped recent block stream")
        recentSource.close()
        return
    }
    if (document.getElementsByClassName('recentModal')[0].classList.contains('is-active')){
        recentSource.close()
        getRecent()
    }
}


document.getElementsByClassName('recentBlocksBtn')[0].onclick = function(){
    document.getElementsByClassName('recentModal')[0].classList.add('is-active')
}


document.getElementsByClassName('recentBlocksBtn')
document.addEventListener("visibilitychange", toggleRecentStream, false);

document.getElementsByClassName('closeRecentModal')[0].onclick = function(){
    document.getElementsByClassName('recentBlockList')[0].innerText = ""
    document.getElementsByClassName('recentModal')[0].classList.remove('is-active')
}