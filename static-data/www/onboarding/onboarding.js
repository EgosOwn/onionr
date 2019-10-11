fetch('/getnewkeys', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(resp) {
        keys = keys.split('')
    })