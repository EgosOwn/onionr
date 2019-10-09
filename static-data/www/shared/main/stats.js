/*
    Onionr - Private P2P Communication

    This file loads stats to show on the main node web page

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
uptimeDisplay = document.getElementById('uptime')
connectedDisplay = document.getElementById('connectedNodes')
connectedDisplay.style.maxHeight = '300px'
connectedDisplay.style.overflowY = 'scroll'
storedBlockDisplay = document.getElementById('storedBlocks')
queuedBlockDisplay = document.getElementById('blockQueue')
lastIncoming = document.getElementById('lastIncoming')
totalRec = document.getElementById('totalRec')
securityLevel = document.getElementById('securityLevel')
sec_description_str = 'unknown'

function showSecStatNotice(){
    var secWarnEls = document.getElementsByClassName('secRequestNotice')
    for (el = 0; el < secWarnEls.length; el++){
        secWarnEls[el].style.display = 'block'
    }
}

function seconds2time (seconds) {
    //func from https://stackoverflow.com/a/7579799/2465421 by https://stackoverflow.com/users/14555/jottos
    var hours   = Math.floor(seconds / 3600)
    var minutes = Math.floor((seconds - (hours * 3600)) / 60)
    var seconds = seconds - (hours * 3600) - (minutes * 60)
    var time = ""

    if (hours != 0) {
      time = hours+":"
    }
    if (minutes != 0 || time !== "") {
      minutes = (minutes < 10 && time !== "") ? "0"+minutes : String(minutes)
      time += minutes+":"
    }
    if (time === "") {
      time = seconds+"s"
    }
    else {
      time += (seconds < 10) ? "0"+seconds : String(seconds)
    }
    return time
}

switch (httpGet('/config/get/general.security_level')){
    case "0":
        sec_description_str = 'normal'
        break;
    case "1":
        sec_description_str = 'high'
        break;
}

if (sec_description_str !== 'normal'){
    showSecStatNotice()
}

function getStats(){
    stats = JSON.parse(httpGet('getstats', webpass))
    uptimeDisplay.innerText = seconds2time(stats['uptime'])
    connectedDisplay.innerText = stats['connectedNodes']
    storedBlockDisplay.innerText = stats['blockCount']
    queuedBlockDisplay.innerText = stats['blockQueueCount']
    securityLevel.innerText = sec_description_str
    totalRec.innerText = httpGet('/hitcount')
    var lastConnect = httpGet('/lastconnect')
    if (lastConnect > 0){
        var humanDate = new Date(0)
        humanDate.setUTCSeconds(httpGet('/lastconnect'))
        humanDate = humanDate.toString()
        lastConnect = humanDate.substring(0, humanDate.indexOf('('));
    }
    else{
        lastConnect = 'None since start'
    }
    lastIncoming.innerText = lastConnect
}
getStats()
setInterval(function(){getStats()}, 10000)