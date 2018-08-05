
/* just for testing rn */
Block.getBlocks({'type' : 'onionr-post', 'signed' : true, 'reverse' : true}, function(data) {
    for(var i = 0; i < data.length; i++) {
        try {
            var block = data[i];

            var post = new Post();
            var user = new User();

            var blockContent = JSON.parse(block.getContent());

            user.setName('unknown');
            user.setID(new String(block.getHeader('signer', 'unknown')));
            post.setContent(blockContent['content']);
            post.setPostDate(block.getDate());
            post.setUser(user);

            document.getElementById('onionr-timeline-posts').innerHTML += post.getHTML();
        } catch(e) {
            console.log(e);
        }
    }
});

function viewProfile(id, name) {
    document.getElementById("onionr-profile-username").innerHTML = encodeHTML(decodeURIComponent(name));
}
