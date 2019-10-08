fetch('/getmotd', {
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text()) 
.then(function(resp) {
    resp = resp.trim()
    if (resp.length <= 1){return}
    let motds = document.getElementsByClassName("motdContent")
    for (x = 0; x < motds.length; x++){
        motds[x].innerText = resp
    }
})