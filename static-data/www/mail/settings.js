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
var notificationSetting = document.getElementById('notificationSetting')
var friendOnlyNotification = document.getElementById('strangersNotification')
var notificationSound = document.getElementById('notificationSound')
var sigSetting = document.getElementById('mailSignatureSetting')

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
        mailSettings['forwardSecrecy'] = document.getElementById('forwardSecrecySetting').checked
        PNotify.success({
            text: 'Successfully toggled default forward secrecy'
        })
      })
}

notificationSound.onchange = function(e){
    var postData = JSON.stringify({"notificationSound": e.target.checked})
    fetch('/config/set/mail', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then(function(data) {
        mailSettings['notificationSound'] = notificationSound.checked
        PNotify.success({
            text: 'Successfully notification sound'
        })
      })
}

friendOnlyNotification.onchange = function(e){
    var postData = JSON.stringify({"strangersNotification": e.target.checked})
    fetch('/config/set/mail', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then(function(data) {
        mailSettings['strangersNotification'] = friendOnlyNotification.checked
        PNotify.success({
            text: 'Successfully toggled notifications from strangers'
        })
      })
}


notificationSetting.onchange = function(e){
    var notificationSettings = document.getElementsByClassName('notificationSetting')
    if (e.target.checked){
        for (i = 0; i < notificationSettings.length; i++){
            notificationSettings[i].style.display = "flex"
        }
    }
    else{
        for (i = 0; i < notificationSettings.length; i++){
            notificationSettings[i].style.display = "none"
        }
    }
    var postData = JSON.stringify({"notificationSetting": e.target.checked})
    fetch('/config/set/mail', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then(function(data) {
        mailSettings['notificationSetting'] = notificationSetting.checked
        PNotify.success({
            text: 'Successfully toggled default mail notifications'
        })
      })
}

sigSetting.onchange = function(){
    var postData = JSON.stringify({"signature": sigSetting.value})
    fetch('/config/set/mail', {
        method: 'POST',
        body: postData,
        headers: {
          "content-type": "application/json",
          "token": webpass
        }})
    .then(function(data) {
        mailSettings['signature'] = sigSetting.value
        PNotify.success({
            text: 'Set mail signature'
        })
      })
}