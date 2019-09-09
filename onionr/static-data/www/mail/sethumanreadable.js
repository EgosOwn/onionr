function setHumanReadableValue(el, key){
    fetch('/getHumanReadable/' + key, {
        headers: {
          "token": webpass
        }})
    .then((resp) => resp.text())
    .then(function(resp) {
        el.value = resp
    })
}