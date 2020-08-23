fetch('/shared/sidebar/sidebar.html', {
    "method": "get",
    headers: {
        "token": webpass
    }})
.then((resp) => resp.text())
.then(function(resp) {
    document.getElementById('sidebarContainer').innerHTML = resp
    var quickviews = bulmaQuickview.attach()
})

window.addEventListener("keydown", function(event) {
    if (event.key === "s"){
        if (document.activeElement.nodeName == "TEXTAREA" || document.activeElement.nodeName == "INPUT"){
            if (! document.activeElement.hasAttribute("readonly")){
                return
            }
        }
        let refreshSideBar = function(){
            if (document.hidden){return}
            var existingValue = document.getElementById("insertingBlocks").innerText
            var existingUploadValue = document.getElementById("uploadBlocks")
            fetch('/getgeneratingblocks', {
                "method": "get",
                headers: {
                    "token": webpass
                }})
                .then((resp) => resp.text())
                .then(function(resp) {
                    console.debug(resp.length, existingValue)
                    if (resp.length <= 2 && existingValue !== "0"){
                        document.getElementById("insertingBlocks").innerText = "0"
                        return
                    }
                    if (existingValue === resp.split(',').length){
                        return
                    }
                    document.getElementById("insertingBlocks").innerText = resp.split(',').length - 1
                })
            fetch('/getblockstoupload', {
                "method": "get",
                headers: {
                    "token": webpass
                }})
                .then((resp) => resp.text())
                .then(function(resp) {
                    console.debug(resp.length, existingUploadValue)
                    if (resp.length <= 2 && existingUploadValue !== "0"){
                        document.getElementById("uploadBlocks").innerText = "0"
                        return
                    }
                    if (existingUploadValue === resp.split(',').length){
                        return
                    }
                    document.getElementById("uploadBlocks").innerText = resp.split(',').length - 1
                })
        }
        setInterval(refreshSideBar, 3000)

        setTimeout(function(){document.getElementsByClassName('sidebarBtn')[0].click()}, 300)
    }
}, true)
