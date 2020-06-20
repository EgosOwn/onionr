var recentSource = new EventSourcePolyfill('/recentblocks', {
    headers: {
        "token": webpass
    }
  })


recentSource.onmessage = function(e){
    console.debug(e)
}
