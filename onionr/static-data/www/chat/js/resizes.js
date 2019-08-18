let doResize = function(){
    let chatInput = document.getElementsByClassName('chatInput')[0]
    chatInput.style.width = "50%";
}
doResize()
window.onresize = doResize