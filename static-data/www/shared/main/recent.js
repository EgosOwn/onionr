var getRecent = function(){
    var recentSource = new EventSourcePolyfill('/recentblocks', {
        headers: {
            "token": webpass
        }
    })


    recentSource.onmessage = function(e){
        if (e.data == "none"){
            return
        }
        var existing = document.getElementsByClassName('recentBlockList')[0].innerText;
        let data = JSON.parse(e.data)
        Object.entries(data.blocks).forEach(([key, value]) => {
            if (existing.includes(key)){
                return
            }
            existing =  key + " - " + value + "\n" + existing
        })
        document.getElementsByClassName('recentBlockList')[0].innerText = existing
        console.debug(data)
    }
    return recentSource
}
recentSource = getRecent()
function toggleRecentStream() {
    if (document.hidden){
        console.debug("Stopped recent block stream")
        recentSource.close()
        return
    }
    if (document.getElementsByClassName('recentModal')[0].classList.contains('is-active')){
        recentSource.close()
        getRecent()
    }
}


document.getElementsByClassName('recentBlocksBtn')[0].onclick = function(){
    document.getElementsByClassName('recentModal')[0].classList.add('is-active')
}


document.getElementsByClassName('recentBlocksBtn')
document.addEventListener("visibilitychange", toggleRecentStream, false);

document.getElementsByClassName('closeRecentModal')[0].onclick = function(){
    document.getElementsByClassName('recentBlockList')[0].innerText = ""
    document.getElementsByClassName('recentModal')[0].classList.remove('is-active')
}