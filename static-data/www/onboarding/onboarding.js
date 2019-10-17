fetch('/getnewkeys', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(resp) {
        keys = resp.split('')
})

function getCheckValue(elName){
    return document.getElementsByName(elName)[0].checked
}

document.getElementById('onboardingForm').onsubmit = function(e){
    submitInfo = {}
    submitInfo.massSurveil = getCheckValue('state')
    submitInfo.stateTarget = getCheckValue('stateTarget')
    submitInfo.localThreat = getCheckValue('local')
    submitInfo.networkContrib = getCheckValue('networkContribution')
    submitInfo.plainContrib = getCheckValue('networkContributionPlain')
    submitInfo.donate = getCheckValue('donate')
    submitInfo.deterministic = getCheckValue('useDeterministic')
    submitInfo.mail = getCheckValue('useMail')

    e.preventDefault()
}