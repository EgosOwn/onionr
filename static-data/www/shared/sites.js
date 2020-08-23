/*
    Onionr - Private P2P Communication

    handle opening of sites on main page

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
function checkHex(str) {
    regexp = /^[0-9a-fA-F]+$/
    if (regexp.test(str)){
        return true
    }
    return false
}

document.getElementById('openSite').onclick = function(){
    var hash = document.getElementById('siteViewer').value.trim()
    if (hash.includes('.onion')){
        PNotify.notice({
            text: 'This is for Onionr sites, not Tor onion services.'
        })
        return
    }
    if (hash.length == 0){ return }
    if (checkHex(hash) && hash.length >= 50 || hash.length == 52 || hash.length == 56){
        window.location.href = '/site/' + hash
    }
    else{
        PNotify.notice({
            text: 'Invalid site hash/ID'
        })
    }
}