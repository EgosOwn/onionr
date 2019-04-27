var saveBtns = document.getElementsByClassName('saveConfig')
var saveBtn = document.getElementsByClassName('saveConfig')[0]
var configEditor = document.getElementsByClassName('configEditor')[0]
var config = {}

fetch('/config/get', {
headers: {
    "token": webpass
}})
.then((resp) => resp.json()) // Transform the data into json
.then(function(resp) {
    config = resp
    configEditor.value = JSON.stringify(config)
})

saveBtn.onclick = function(){
    
}