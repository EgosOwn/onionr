fetch('/shared/sidebar/sidebar.html', {
    "method": "get",
    headers: {
        "token": webpass
    }})
.then((resp) => resp.text())
.then(function(resp) {
    document.getElementById('sidebarContainer').innerHTML = resp
})



window.addEventListener("keydown", function(event) {
    if (event.key === "s"){
        let quickviews = bulmaQuickview.attach()
        document.getElementsByClassName('sidebarBtn')[0].click()
    }
}, true)
