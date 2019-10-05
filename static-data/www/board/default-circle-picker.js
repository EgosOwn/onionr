recommendedIDs = document.getElementById('recommendedBoards')

recommendedIDs.onchange = function(){
    document.getElementById('feedIDInput').value = recommendedIDs.value
    getBlocks()
}