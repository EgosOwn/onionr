var checkbox = document.getElementById('refreshCheckbox')
function autoRefresh(){
    if (! checkbox.checked){return}
    getBlocks()
}

function setupInterval(){
    if (checkbox.checked){
        refreshInterval = setInterval(autoRefresh, 3000)
        autoRefresh()
        return
    }
    clearInterval(refreshInterval)
}

var refreshInterval = setInterval(autoRefresh, 3000)
setupInterval()

checkbox.onchange = function(){setupInterval}