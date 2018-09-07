/* just for testing rn */
Block.getBlocks({'type' : 'onionr-post', 'signed' : true, 'reverse' : true}, function(data) {
    for(var i = 0; i < data.length; i++) {
        try {
            var block = data[i];

            var finished = false;
            User.getUser(new String(block.getHeader('signer', 'unknown')), function(user) {
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
            console.log('Troublemaker block: ' + data[i].getHash());
            console.log(e);
        }
    }
});

function viewProfile(id, name) {
    id = decodeURIComponent(id);
    document.getElementById("onionr-profile-username").innerHTML = Sanitize.html(decodeURIComponent(name));

    User.getUser(id, function(data) {
        if(data !== null) {
            document.getElementById("onionr-profile-username").innerHTML = Sanitize.html(data.getName());
            document.getElementById("onionr-profile-username").title = Sanitize.html(data.getID());
            document.getElementById("onionr-profile-user-icon").src = "data:image/jpeg;base64," + Sanitize.html(data.getIcon());
            document.getElementById("onionr-profile-user-icon").b64 = Sanitize.html(data.getIcon());
        }
    });
}

function updateUser() {
    toggleSaveButton(false);

    jQuery('#modal').modal('show');

    var name = jQuery('#onionr-profile-username').text();
    var id = document.getElementById("onionr-profile-username").title;
    var icon = document.getElementById("onionr-profile-user-icon").b64;
    var description = 'todo';

    var user = new User();

    user.setName(name);
    user.setID(id);
    user.setIcon(icon);
    user.setDescription(description);

    user.remember();
    user.save();

    window.location.reload();
}

function cancelUpdate() {
    toggleSaveButton(false);

    var name = jQuery('#onionr-profile-username').text();
    var id = document.getElementById("onionr-profile-username").title;

    viewProfile(id, name);
}

function toggleSaveButton(show) {
    document.getElementById("onionr-profile-save").style.display = (show ? 'block' : 'none');
    document.getElementById("onionr-profile-cancel").style.display = (show ? 'block' : 'none');
}

function makePost() {
    var content = document.getElementById("onionr-post-creator-content").value;

    if(content.trim() !== '') {
        var post = new Post();

        post.setUser(getCurrentUser());
        post.setContent(content);
        post.setPostDate(new Date());

        post.save(function(data) {}); // async, but no function

        document.getElementById('onionr-timeline-posts').innerHTML = post.getHTML() + document.getElementById('onionr-timeline-posts').innerHTML;

        document.getElementById("onionr-post-creator-content").value = "";
    } else {
        console.log('Not making empty post.');
    }
}

$('body').on('click', '[data-editable]', function() {
    var el = jQuery(this);
    var txt = el.text();

    var input = jQuery('<input/>').val(txt);
    el.replaceWith(input);

    var save = function() {
        var newTxt = input.val();
        var p = el.text(Sanitize.username(newTxt));
        input.replaceWith(p);

        if(newTxt !== txt)
            toggleSaveButton(true);
    };

    input.one('blur', save).focus();
});

document.getElementById("onionr-post-creator-user-name").innerHTML = Sanitize.html(currentUser.getName());
document.getElementById("onionr-post-creator-user-id").innerHTML = "you";
document.getElementById("onionr-post-creator-user-icon").src = "data:image/jpeg;base64," + Sanitize.html(currentUser.getIcon());
document.getElementById("onionr-post-creator-user-id").title = currentUser.getID();
document.getElementById("onionr-post-creator-content").placeholder = "Enter a message here...";

viewCurrentProfile = function() {
    viewProfile(encodeURIComponent(currentUser.getID()), encodeURIComponent(currentUser.getName()));
}

document.getElementById("onionr-post-creator-user-id").onclick = viewCurrentProfile;
document.getElementById("onionr-post-creator-user-name").onclick = viewCurrentProfile;
