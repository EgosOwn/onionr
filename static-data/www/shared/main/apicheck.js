apiOnline = true
async function doPing(){
    out = setTimeout(function(){
        if (apiOnline){
        PNotify.notice('Connection lost with API server')
        }
        apiOnline = false
    }, 1000)
return await fetch('/ping', {
    headers: {
        "token": webpass
    }})
    .then((resp) => resp.text()) // Transform the data into text
    .then(function(resp) {
        if (!apiOnline){PNotify.success('API server connection reestablished')}
        apiOnline = true
        clearTimeout(out)
        return resp
    })
}

let pingCheck = async function(){
    result = await doPing()

}

pingCheckInterval = setInterval(function(){pingCheck()}, 3000)
