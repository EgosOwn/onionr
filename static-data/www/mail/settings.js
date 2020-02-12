/*
    Onionr - Private P2P Communication

    Handle mail settings

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

document.getElementById('forwardSecrecySetting').onchange = function(e){
    postData = JSON.stringify({"default_forward_secrecy": e.target.checked})
    fetch('/config/set/mail', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then((resp) => resp.text())
    .then(function(data) {
        PNotify.success({
            text: 'Successfully toggled default forward secrecy'
        })
      })
}
