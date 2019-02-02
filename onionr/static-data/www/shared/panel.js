shutdownBtn = document.getElementById('shutdownNode')
refreshStatsBtn = document.getElementById('refreshStats')
shutdownBtn.onclick = function(){
    if (! nowebpass){
        httpGet('shutdownclean')
        overlay('shutdownNotice')
    }
}

refreshStatsBtn.onclick = function(){
    getStats()
}