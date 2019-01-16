webpass = document.location.hash.replace('#', '')
if (typeof webpass == "undefined"){
    webpass = localStorage['webpass']
}
else{
    localStorage['webpass'] = webpass
    document.location.hash = ''
}
if (typeof webpass == "undefined" || webpass == ""){
    alert('Web password was not found in memory or URL')
}

function httpGet(theUrl) {
    var xmlHttp = new XMLHttpRequest()
    xmlHttp.open( "GET", theUrl, false ) // false for synchronous request
    xmlHttp.setRequestHeader('token', webpass)
    xmlHttp.send( null )
    if (xmlHttp.status == 200){
        return xmlHttp.responseText
    }
    else{
        return ""
    }
}
function overlay(overlayID) {
    el = document.getElementById(overlayID)
   el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible"
 }
