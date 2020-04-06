mailSettings = {}

fetch('/config/get/mail', {
    headers: {
      "content-type": "application/json",
      "token": webpass
    }})
.then((resp) => resp.json())
.then(function(settings) {
    mailSettings = settings || {}
    if (mailSettings.default_forward_secrecy === false){
        document.getElementById('forwardSecrecySetting').checked = false
    }
    if (mailSettings.use_padding === false){
      document.getElementById('messagePaddingSetting').checked = false
    }
    if (mailSettings.notificationSetting === false){
      document.getElementById('notificationSetting').checked = false
    }
    if (mailSettings.notificationSound === false){
      document.getElementById('notificationSound').checked = false
    }
    if (typeof mailSettings.signature != undefined && mailSettings.signature != null && mailSettings.signature != ""){
      document.getElementById('mailSignatureSetting').value = mailSettings.signature
    }
    if (mailSettings.strangersNotification == false){
      document.getElementById('strangersNotification').checked = false
    }
  })