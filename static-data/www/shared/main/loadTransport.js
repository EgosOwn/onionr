fetch('/gettoraddress', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text())
    .then(function(resp) {
        let torBoxes = document.getElementsByClassName('myTor')
        Array.from(torBoxes).forEach(element => {
            element.value = resp  
        })

    })

Array.from(document.getElementsByClassName('myTorCopy')).forEach(element => {
    element.onclick = function(){
        var copyText = document.getElementsByClassName('myTor')[0]
        copyText.select()
        document.execCommand("copy")
        if (typeof PNotify != 'undefined'){
            PNotify.success({
                text: "Copied to clipboard"
            })
        }
    }
})