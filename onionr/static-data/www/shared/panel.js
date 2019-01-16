shutdownBtn = document.getElementById('shutdownNode')

shutdownBtn.onclick = function(){
    httpGet('shutdownclean')
    overlay('shutdownNotice')
}
