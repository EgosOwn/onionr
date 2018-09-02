function getUserInfo(id, callback) {
    var user = deserializeUser(id);
    if(user === null) {
        Block.getBlocks({'type' : 'onionr-user-info', 'signed' : true, 'reverse' : true}, function(data) {
            if(data.length !== 0) {
                try {
                    user = new User();

                    var userInfo = JSON.parse(data[0].getContent());

                    if(userInfo['id'] === id) {
                        user.setName(userInfo['name']);
                        user.setIcon(userInfo['icon']);
                        user.setID(id);

                        serializeUser(user);

                        return callback(user);
                    }
                } catch(e) {
                    console.log(e);
                    return callback(null);
                }
            } else {
                return callback(null);
            }
        });
    } else {
        return callback(user);
    }
}

/* just for testing rn */
Block.getBlocks({'type' : 'onionr-post', 'signed' : true, 'reverse' : true}, function(data) {
    for(var i = 0; i < data.length; i++) {
        try {
            var block = data[i];

            var finished = false;
            getUserInfo(new String(block.getHeader('signer', 'unknown')), function(user) {
                var post = new Post();

                var blockContent = JSON.parse(block.getContent());

                post.setContent(blockContent['content']);
                post.setPostDate(block.getDate());
                post.setUser(user);

                document.getElementById('onionr-timeline-posts').innerHTML += post.getHTML();

                finished = true;
            });

            while(!finished);
        } catch(e) {
            console.log(e);
        }
    }
});

function viewProfile(id, name) {
    id = decodeURIComponent(id);
    document.getElementById("onionr-profile-username").innerHTML = Sanitize.html(decodeURIComponent(name));

    getUserInfo(id, function(data) {
        if(data !== null) {
            document.getElementById("onionr-profile-username").innerHTML = Sanitize.html(data.getName());
            document.getElementById("onionr-profile-username").title = Sanitize.html(data.getID());
            document.getElementById("onionr-profile-user-icon").src = "data:image/jpeg;base64," + Sanitize.html(data.getIcon());
        }
    });
}
