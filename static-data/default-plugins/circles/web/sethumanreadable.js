/*
    Onionr - Private P2P Communication

    Set human readable public keys onto post author elements

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
humanReadableKeys = {}

function setHumanReadableIDOnPost(el, key){
    if (typeof humanReadableKeys[key] == "undefined"){
        fetch('/getHumanReadable/' + key, {
            method: 'GET',
            headers: {
              "token": webpass
            }})
        .then((resp) => resp.text()) // Transform the data into json
        .then(function(data) {
            if (data.includes('HTML')){
                return
            }
            humanReadableKeys[key] = data
            setHumanReadableIDOnPost(el, key)
        })
        return
    }
    el.innerText = humanReadableKeys[key].split('-').slice(0, 3).join(' ')
}