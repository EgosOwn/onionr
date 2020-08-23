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

webpass = document.location.hash.replace('#', '')
nowebpass = false
myPub = ""

fetch('/getHumanReadable', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text())
.then(function(resp) {
    myPub = resp
})

function post_to_url(path, params) {

    var form = document.createElement("form")

    form.setAttribute("method", "POST")
    form.setAttribute("action", path)

    for(var key in params) {
        var hiddenField = document.createElement("input")
        hiddenField.setAttribute("type", "hidden")
        hiddenField.setAttribute("name", key)
        hiddenField.setAttribute("value", params[key])
        form.appendChild(hiddenField)
    }

    document.body.appendChild(form)
    form.submit()
}

if (typeof webpass == "undefined"){
    webpass = localStorage['webpass']
}
else{
    localStorage['webpass'] = webpass
    //document.location.hash = ''
}
if (typeof webpass == "undefined" || webpass == ""){
    alert('Web password was not found in memory or URL')
    nowebpass = true
}

function arrayContains(needle, arrhaystack) {
    return (arrhaystack.indexOf(needle) > -1);
}


function overlay(overlayID) {
    el = document.getElementById(overlayID)
   el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible"
   scroll(0,0)
 }

var passLinks = document.getElementsByClassName("idLink")
 for(var i = 0; i < passLinks.length; i++) {
    passLinks[i].href += '#' + webpass
 }

var refreshLinks = document.getElementsByClassName("refresh")

for(var i = 0; i < refreshLinks.length; i++) {
    //Can't use .reload because of webpass
    refreshLinks[i].onclick = function(){
        location.reload()
    }
}

for (var i = 0; i < document.getElementsByClassName('closeOverlay').length; i++){
    document.getElementsByClassName('closeOverlay')[i].onclick = function(e){
        document.getElementById(e.target.getAttribute('overlay')).style.visibility = 'hidden'
    }
}

function setIdStrings(){
    if (myPub === ""){
        setTimeout(function(){setIdStrings()}, 700)
        return
    }
    var idStrings = document.getElementsByClassName('myPub')
    for (var i = 0; i < idStrings.length; i++){
        if (idStrings[i].tagName.toLowerCase() == 'input'){
            idStrings[i].value = myPub
        }
        else{
            idStrings[i].innerText = myPub
        }
    }
}
setIdStrings()

/* Copy public ID on homepage  */
if (typeof myPubCopy != "undefined"){

    myPubCopy.onclick = function() {
        var copyText = document.getElementById("myPub");
        copyText.select()
        document.execCommand("copy")
        if (typeof PNotify != 'undefined'){
            PNotify.success({
                text: "Copied to clipboard"
              })
        }
        console.log("copied pubkey to clipboard")
    }
}

/* For Config toggle on homepage */
var toggle  = document.getElementById("configToggle")
var content = document.getElementById("configContent")

if(typeof toggle !== 'undefined' && toggle !== null) {
    toggle.addEventListener("click", function() {
    content.classList.toggle("show");
    })
}

var aboutBtns = document.getElementsByClassName('aboutLink')
var aboutModals = document.getElementsByClassName('aboutModal')
var aboutCloseBtns = document.getElementsByClassName('closeAboutModal')

var aboutText = ''

setAbout = function(){
    if (aboutText === ''){
        setTimeout(function(){setAbout()}, 100)
        return
    }
    let aboutBody = document.getElementsByClassName('aboutBody')
    for (i = 0; i < aboutBody.length; i++){
        aboutBody[i].innerHTML = aboutText
    }
}

for (x = 0; x < aboutBtns.length; x++){
    aboutBtns[x].onclick = function(){
        for (i = 0; i < aboutModals.length; i++){
            aboutModals[i].classList.add('is-active')
        }
    }
}
for (i = 0; i < aboutCloseBtns.length; i++){
    aboutCloseBtns[i].onclick = function(e){
        e.target.parentElement.parentElement.parentElement.classList.remove('is-active')
    }
}

setAbout()