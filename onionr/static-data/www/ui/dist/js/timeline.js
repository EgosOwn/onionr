/* just for testing rn */
Block.getBlocks({'type' : 'onionr-post', 'signed' : true, 'reverse' : true}, function(data) {
    for(var i = 0; i < data.length; i++) {
        try {
            var block = data[i];

            var finished = false;
            User.getUser(new String(block.getHeader('signer', 'unknown')), function(user) {
                var post = new Post();

                var blockContent = JSON.parse(block.getContent());

                // just ignore anything shorter than 280 characters
                if(String(blockContent['content']).length <= 280) {
                    post.setContent(blockContent['content']);
                    post.setPostDate(block.getDate());
                    post.setUser(user);

                    post.setHash(block.getHash());

                    document.getElementById('onionr-timeline-posts').innerHTML += post.getHTML();
                }

                finished = true;
            });

            while(!finished);
        } catch(e) {
            console.log('Troublemaker block: ' + data[i].getHash());
            console.log(e);
        }
    }
});

function toggleLike(hash) {
    var post = getPostMap(hash);
    if(post === null || !getPostMap()[hash]['liked']) {
        console.log('Liking ' + hash + '...');

        if(post === null)
            getPostMap()[hash] = {};

        getPostMap()[hash]['liked'] = true;

        set('postmap', JSON.stringify(getPostMap()));

        var block = new Block();

        block.setType('onionr-post-like');
        block.setContent(JSON.stringify({'hash' : hash}));
        block.save(true, function(hash) {});
    } else {
        console.log('Unliking ' + hash + '...');
    }
}

function postCreatorChange() {
    var content = document.getElementById('onionr-post-creator-content').value;
    var message = '';

    var disable = true;

    if(content.length !== 0) {
        if(content.length - content.replaceAll('\n', '').length > 16) {
            // 16 max newlines
            message = 'Please use less than 16 newlines';
        } else if(content.length <= 280) {
            // 280 max characters
            message = '%s characters remaining'.replaceAll('%s', (280 - content.length));
            disable = false;
        } else {
            message = '%s characters over maximum'.replaceAll('%s', (content.length - 280));
        }
    }

    var element = document.getElementById('onionr-post-creator-content-message');
    var button = document.getElementById("onionr-post-creator-create");

    if(message === '')
        element.style.visibility = 'hidden';
    else {
        element.style.visibility = 'visible';

        element.innerHTML = message;

        if(disable)
            element.style.color = 'red';
        else
            element.style.color = 'gray';
    }

    if(disable)
        button.disabled = true;
    else
        button.disabled = false;
}

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
        postCreatorChange();
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

currentUser = getCurrentUser();

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

// on some browsers it saves the user input on reload. So, it should also recheck the input.
postCreatorChange();
