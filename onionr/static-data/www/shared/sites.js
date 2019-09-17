function checkHex(str) {
    regexp = /^[0-9a-fA-F]+$/
    if (regexp.test(str)){
        return true
    }
    return false
}

document.getElementById('openSite').onclick = function(){
    var hash = document.getElementById('siteViewer').value

    if (checkHex(hash) && hash.length == 64){
        window.location.href = '/site/' + hash
    }
    else{
        PNotify.notice({
            text: 'Invalid site hash'
        })
    }
}