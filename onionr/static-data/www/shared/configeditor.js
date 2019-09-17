/*
    Onionr - Private P2P Communication

    This file is for configuration editing in the web interface

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

var saveBtns = document.getElementsByClassName('saveConfig')
var saveBtn = document.getElementsByClassName('saveConfig')[0]
var configEditor = document.getElementsByClassName('configEditor')[0]
var config = {}

fetch('/config/get', {
headers: {
    "token": webpass
}})
.then((resp) => resp.text()) // Transform the data into text
.then(function(resp) {
    configEditor.value = resp
    config = JSON.parse(resp) //parse here so we can set the text field to pretty json
})

saveBtn.onclick = function(){
    var postData = configEditor.value
    try {
        JSON.parse(postData)
    } catch (e) {
        alert('Configuration is not valid JSON')
        return false
    }
    fetch('/config/setall', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(data) {
        PNotify.success({
            text: 'Config saved'
        })
      })
}