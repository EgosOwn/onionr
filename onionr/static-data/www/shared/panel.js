shutdownBtn = document.getElementById('shutdownNode')

shutdownBtn.onclick = function(){
    if (! nowebpass){
        httpGet('shutdownclean')
        overlay('shutdownNotice')
    }
}
