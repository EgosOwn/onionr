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

var sendbutton = document.getElementById('sendMail')
messageContent = document.getElementById('draftText')
to = document.getElementById('draftID')
subject = document.getElementById('draftSubject')
friendPicker = document.getElementById('friendSelect')

function utf8Length(s) {
    var size = encodeURIComponent(s).match(/%[89ABab]/g);
    return s.length + (size ? size.length : 0);
  }

function padString(string_data, round_nearest_byte_exponent = 3){
    if (utf8Length(string_data) === 0){
        string_data += '0'
    }
    let round_size = 10 ** round_nearest_byte_exponent
    while (utf8Length(string_data) % round_size > 0){
        string_data += '0'
    }
    return string_data
}

function sendMail(toData, message, subject){
    let meta = {'subject': subject}

    if (document.getElementById('messagePaddingSetting').checked){
        message = padString(message)
    }

    if (document.getElementById('mailSignatureSetting').value !== false){
        message += "\n"
        message += document.getElementById('mailSignatureSetting').value
    }

    postData = {'message': message, 'to': toData, 'type': 'pm', 'encrypt': true, 'meta': JSON.stringify(meta)}
    postData.forward = document.getElementById('forwardSecrecySetting').checked
    postData = JSON.stringify(postData)
    sendForm.style.display = 'none'

    fetch('/insertblock', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }}).then(function(resp){
            if (!resp.ok){
                PNotify.error({
                    text: 'Malformed input'
                })
                sendForm.style.display = 'block'
                throw new Error("Malformed input in sendmail")
            }
            return resp
        })
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(data) {
        sendForm.style.display = 'block'
        PNotify.success({
            text: 'Queued for sending!',
            delay: 3500,
            mouseReset: false
        })
        to.value = subject.value = messageContent.value = ""
        friendPicker.value = ""
        subject.value = ""
      })
}

var friendPicker = document.getElementById('friendSelect')
friendPicker.onchange = function(){
    to.value = friendPicker.value
}

sendForm.onsubmit = function(){
    let getInstances = function(string, word) {
        return string.split(word).length - 1;
    }

    if(getInstances(to.value, '-') != 15){
        if (to.value.length != 56 && to.value.length != 52){
            PNotify.error({
                text: 'User ID is not valid'
            })
            return false
        }
    }
    sendMail(to.value, messageContent.value, subject.value)
    return false
}
