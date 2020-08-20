/*
    Onionr - Private P2P Communication

    Handles onboarding for Onionr

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

fetch('/getnewkeys', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text())
    .then(function(resp) {
        keys = resp.split('')
})

function getCheckValue(elName){
    return document.getElementsByName(elName)[0].checked
}

function sendConfig(configInfo){
    fetch('/setonboarding', {
        method: 'POST',
        headers: {
          "token": webpass,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({configInfo})
        }).then(function(data) {
            window.location.href = window.location.origin + '/' + window.location.hash
        })
}


document.getElementById('onboardingForm').onsubmit = function(e){
    submitInfo = {}
    submitInfo.massSurveil = getCheckValue('state')
    submitInfo.stateTarget = getCheckValue('stateTarget')
    submitInfo.localThreat = getCheckValue('local')
    submitInfo.networkContrib = getCheckValue('networkContribution')
    submitInfo.plainContrib = getCheckValue('networkContributionPlain')
    submitInfo.donate = getCheckValue('donate')
    //submitInfo.deterministic = getCheckValue('useDeterministic')
    submitInfo.mail = getCheckValue('useMail')
    submitInfo.circles = getCheckValue('useCircles')
    submitInfo.useDark = getCheckValue('useDarkTheme')

    if (submitInfo.donate){
        openDonateModal(submitInfo)
        return false
    }

    sendConfig(submitInfo)

    e.preventDefault()
}

/* Fix label clicking since bulma is weird */

let labelClickFix = function(labels) {
    for (i = 0; i < labels.length; i++){
        labels[i].onclick = function(event){
            document.getElementsByName(event.target.getAttribute("for"))[0].checked ^= 1
        }
    }

}
let setupLabelFix = function(){
    var labels = document.getElementsByTagName('label')
    var icons = document.getElementsByTagName('i')
    labelClickFix(labels)
    labelClickFix(icons)
}
setupLabelFix()
