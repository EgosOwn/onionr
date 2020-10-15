fetch('/shared/sidebar/sidebar.html', {
    "method": "get",
    headers: {
        "token": webpass
    }})
.then((resp) => resp.text())
.then(function(resp) {
    document.getElementById('sidebarContainer').innerHTML = resp
    var quickviews = bulmaQuickview.attach()
    sidebarAddPeerRegister()
})

function sidebarAddPeerRegister(){
    document.getElementById('addPeerBtn').onclick = function(){
        let newPeer = document.getElementById('addPeerInput').value

        if (! newPeer.includes(".")){
            PNotify.error({text: "Invalid peer address"})
            return
        }
        fetch('/addpeer/' + newPeer, {
            method: 'POST',
            headers: {
            "token": webpass
            }})
        .then(function(resp){
            if (! resp.ok){
                if (resp.status == 409){
                    PNotify.notice({text: "Peer already added"})
                    return
                }
                PNotify.error({text: "Could not add peer. Is your input valid?"})
                throw new Error("Could not add peer " + newPeer)
            }
        })
        .then((resp) => resp.text())
        .then(function(data) {
            if (data == "success"){
                PNotify.success({
                    text: 'Peer added'
                })
                return
            }
            else if(data == "already added"){
                PNotify.notice({
                    text: 'Peer already added'
                })
                return
            }
            PNotify.error({text: data})

        })
    }
}

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
