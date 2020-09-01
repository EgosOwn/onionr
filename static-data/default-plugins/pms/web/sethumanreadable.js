/*
    Onionr - Private P2P Communication

    Load human readable public keys into a cache

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
function loadHumanReadableToCache(key){
    fetch('/getHumanReadable/' + key, {
        headers: {
          "token": webpass
        }})
    .then((resp) => resp.text())
    .then(function(resp) {
        humanReadableCache[key] = resp
    })
}

function setHumanReadableValue(el, key){
    if (typeof humanReadableCache[key] != 'undefined'){
        el.innerText = humanReadableCache[key].split('-').slice(0,3).join('-')
        return
    }
    else{
        loadHumanReadableToCache(key)
        setTimeout(function(){setHumanReadableValue(el, key)}, 100)
        return
    }
}