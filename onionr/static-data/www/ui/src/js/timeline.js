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
                if(String(blockContent['content']).length <= 280 && block.getParent() === null) {
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

    var maxlength = 280;

    var disable = true;
    var warn = false;

    if(content.length !== 0) {
        if(content.length - content.replaceAll('\n', '').length > 16) {
            // 16 max newlines
            message = '<$= LANG.POST_CREATOR_MESSAGE_MAXIMUM_NEWLINES $>';
        } else if(content.length <= maxlength) {
            // 280 max characters
            message = '<$= LANG.POST_CREATOR_MESSAGE_REMAINING $>'.replaceAll('%s', (280 - content.length));
            disable = false;

            if(maxlength - content.length < maxlength / 4) {
                warn = true;
            }
        } else {
            message = '<$= LANG.POST_CREATOR_MESSAGE_OVER $>'.replaceAll('%s', (content.length - maxlength));
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
        else if(warn)
            element.style.color = '#FF8C00';
        else
            element.style.color = 'gray';
    }

    if(disable)
        button.disabled = true;
    else
        button.disabled = false;
}

function replyCreatorChange() {
    var content = document.getElementById('onionr-reply-creator-content').value;
    var message = '';

    var maxlength = 280;

    var disable = true;
    var warn = false;

    if(content.length !== 0) {
        if(content.length - content.replaceAll('\n', '').length > 16) {
            // 16 max newlines
            message = '<$= LANG.POST_CREATOR_MESSAGE_MAXIMUM_NEWLINES $>';
        } else if(content.length <= maxlength) {
            // 280 max characters
            message = '<$= LANG.POST_CREATOR_MESSAGE_REMAINING $>'.replaceAll('%s', (280 - content.length));
            disable = false;

            if(maxlength - content.length < maxlength / 4) {
                warn = true;
            }
        } else {
            message = '<$= LANG.POST_CREATOR_MESSAGE_OVER $>'.replaceAll('%s', (content.length - maxlength));
        }
    }

    var element = document.getElementById('onionr-reply-creator-content-message');
    var button = document.getElementById("onionr-reply-creator-create");

    if(message === '')
        element.style.visibility = 'hidden';
    else {
        element.style.visibility = 'visible';

        element.innerHTML = message;

        if(disable)
            element.style.color = 'red';
        else if(warn)
            element.style.color = '#FF8C00';
        else
            element.style.color = 'gray';
    }

    if(disable)
        button.disabled = true;
    else
        button.disabled = false;
}

function focusReplyCreatorChange() {
    var content = document.getElementById('onionr-post-focus-reply-creator-content').value;
    var message = '';

    var maxlength = 280;

    var disable = true;
    var warn = false;

    if(content.length !== 0) {
        if(content.length - content.replaceAll('\n', '').length > 16) {
            // 16 max newlines
            message = '<$= LANG.POST_CREATOR_MESSAGE_MAXIMUM_NEWLINES $>';
        } else if(content.length <= maxlength) {
            // 280 max characters
            message = '<$= LANG.POST_CREATOR_MESSAGE_REMAINING $>'.replaceAll('%s', (280 - content.length));
            disable = false;

            if(maxlength - content.length < maxlength / 4) {
                warn = true;
            }
        } else {
            message = '<$= LANG.POST_CREATOR_MESSAGE_OVER $>'.replaceAll('%s', (content.length - maxlength));
        }
    }

    var element = document.getElementById('onionr-post-focus-reply-creator-content-message');
    var button = document.getElementById("onionr-post-focus-reply-creator-create");

    if(message === '')
        element.style.visibility = 'hidden';
    else {
        element.style.visibility = 'visible';

        element.innerHTML = message;

        if(disable)
            element.style.color = 'red';
        else if(warn)
            element.style.color = '#FF8C00';
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
            document.getElementById("onionr-profile-user-icon").src = "data:image/jpeg;base64," + Sanitize.html(data.getIcon());
            document.getElementById("onionr-profile-user-icon").b64 = Sanitize.html(data.getIcon());
            document.getElementById("onionr-profile-username").innerHTML = Sanitize.html(Sanitize.username(data.getName()));
            document.getElementById("onionr-profile-username").title = Sanitize.html(data.getID());
            document.getElementById("onionr-profile-description").innerHTML = Sanitize.html(Sanitize.description(data.getDescription()));
        }
    });
}

function updateUser() {
    toggleSaveButton(false);

    // jQuery('#modal').modal('show');

    var name = jQuery('#onionr-profile-username').text();
    var id = document.getElementById("onionr-profile-username").title;
    var icon = document.getElementById("onionr-profile-user-icon").b64;
    var description = jQuery("#onionr-profile-description").text();

    var user = new User();

    user.setName(name);
    user.setID(id);
    user.setIcon(icon);
    user.setDescription(Sanitize.description(description));

    user.remember();
    user.save(function() {
        setCurrentUser(user);

        window.location.reload();
    });
}

function cancelUpdate() {
    toggleSaveButton(false);

    var name = jQuery('#onionr-profile-username').text();
    var id = document.getElementById("onionr-profile-username").title;

    viewProfile(id, name);
}

function toggleSaveButton(show) {
    document.getElementById("onionr-profile-edit").style.display = (show ? 'block' : 'none');
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
        document.getElementById("onionr-post-creator-content").focus();
        postCreatorChange();
    } else {
        console.log('Not making empty post.');
    }
}

function getReplies(id, callback) {
    Block.getBlocks({'type' : 'onionr-post', 'parent' : id, 'signed' : true, 'reverse' : true}, callback);
}

function focusPost(id) {
    viewReplies(id);
}

function viewRepliesMobile(id) {
    var post = document.getElementById('onionr-post-' + id);

    var user_name = '';
    var user_id = '';
    var user_id_trunc = '';
    var user_icon = '';
    var post_content = '';

    if(post !== null && post !== undefined) {
        // if the post is in the timeline, get the data from it
        user_name = post.getElementsByClassName('onionr-post-user-name')[0].innerHTML;
        user_id = post.getElementsByClassName('onionr-post-user-id')[0].title;
        user_id_trunc = post.getElementsByClassName('onionr-post-user-id')[0].innerHTML;
        user_icon = post.getElementsByClassName('onionr-post-user-icon')[0].src;
        post_content = post.getElementsByClassName('onionr-post-content')[0].innerHTML;
    } else {
        // otherwise, fetch the data
    }

    document.getElementById('onionr-post-focus-user-icon').src = user_icon;
    document.getElementById('onionr-post-focus-user-name').innerHTML = user_name;
    document.getElementById('onionr-post-focus-user-id').innerHTML = user_id_trunc;
    document.getElementById('onionr-post-focus-user-id').title = user_id;
    document.getElementById('onionr-post-focus-content').innerHTML = post_content;

    document.getElementById('onionr-post-focus-reply-creator-user-name').innerHTML = Sanitize.html(Sanitize.username(getCurrentUser().getName()));
    document.getElementById('onionr-post-focus-reply-creator-user-icon').src = "data:image/jpeg;base64," + Sanitize.html(getCurrentUser().getIcon());
    document.getElementById('onionr-post-focus-reply-creator-content').value = '';
    document.getElementById('onionr-post-focus-reply-creator-content-message').value = '';

    jQuery('#onionr-post-focus').modal('show');
}

function viewReplies(id) {
    document.getElementById('onionr-replies-title').innerHTML = '<$= LANG.REPLIES $>';
    document.getElementById('onionr-reply-creator-panel').originalPost = id;
    document.getElementById('onionr-reply-creator-panel').innerHTML = '<$= jsTemplate('onionr-reply-creator') $>';

    document.getElementById('onionr-reply-creator-content').innerHTML = '';
    document.getElementById("onionr-reply-creator-content").placeholder = "<$= LANG.POST_CREATOR_PLACEHOLDER $>";
    document.getElementById('onionr-reply-creator-user-name').innerHTML = Sanitize.html(Sanitize.username(getCurrentUser().getName()));
    document.getElementById('onionr-reply-creator-user-icon').src = "data:image/jpeg;base64," + Sanitize.html(getCurrentUser().getIcon());

    document.getElementById('onionr-replies').innerHTML = '';
    getReplies(id, function(data) {
        var replies = document.getElementById('onionr-replies');

        replies.innerHTML = '';

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

                        replies.innerHTML += post.getHTML('reply');
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
}

function makeReply() {
    var content = document.getElementById("onionr-reply-creator-content").value;

    if(content.trim() !== '') {
        var post = new Post();

        var originalPost = document.getElementById('onionr-reply-creator-panel').originalPost;

        console.log('Original post hash: ' + originalPost);

        post.setUser(getCurrentUser());
        post.setParent(originalPost);
        post.setContent(content);
        post.setPostDate(new Date());

        post.save(function(data) {}); // async, but no function

        document.getElementById('onionr-replies').innerHTML = post.getHTML('reply') + document.getElementById('onionr-replies').innerHTML;

        document.getElementById("onionr-reply-creator-content").value = "";
        document.getElementById("onionr-reply-creator-content").focus();
        replyCreatorChange();
    } else {
        console.log('Not making empty reply.');
    }
}

jQuery('body').on('click', '[data-editable]', function() {
    var el = jQuery(this);
    var txt = el.text();
    var maxlength = el.attr("maxlength");

    var input = jQuery('<input/>').val(txt);
    input.attr('maxlength', maxlength);
    el.replaceWith(input);

    var save = function() {
        var newTxt = input.val();

        if(el.attr('id') === 'onionr-profile-username')
            newTxt = Sanitize.username(newTxt);
        if(el.attr('id') === 'onionr-profile-description')
            newTxt = Sanitize.description(newTxt);

        var p = el.text(newTxt);

        input.replaceWith(p);

        if(newTxt !== txt)
            toggleSaveButton(true);
    };

    var saveEnter = function(event) {
        console.log(event);
        console.log(event.keyCode);
        if (event.keyCode === 13)
            save();
    };

    input.one('blur', save).bind('keyup', saveEnter).focus();
});
//viewProfile('$user-id-url', '$user-name-url')
// jQuery('#onionr-post-user-id').on('click', function(e) { alert(3);});
//jQuery('#onionr-post *').on('click', function(e) { e.stopPropagation(); });
// jQuery('#onionr-post').click(function(e) { alert(1); });

currentUser = getCurrentUser();
if(currentUser !== undefined && currentUser !== null) {
    document.getElementById("onionr-post-creator-user-name").innerHTML = Sanitize.html(currentUser.getName());
    document.getElementById("onionr-post-creator-user-id").innerHTML = "<$= LANG.POST_CREATOR_YOU $>";
    document.getElementById("onionr-post-creator-user-icon").src = "data:image/jpeg;base64," + Sanitize.html(currentUser.getIcon());
    document.getElementById("onionr-post-creator-user-id").title = currentUser.getID();

    document.getElementById("onionr-post-creator-content").placeholder = "<$= LANG.POST_CREATOR_PLACEHOLDER $>";
    document.getElementById("onionr-post-focus-reply-creator-content").placeholder = "<$= LANG.POST_CREATOR_PLACEHOLDER $>";

    document.getElementById("onionr-post-focus-reply-creator-user-id").innerHTML = "<$= LANG.POST_CREATOR_YOU $>";
}

viewCurrentProfile = function() {
    viewProfile(encodeURIComponent(currentUser.getID()), encodeURIComponent(currentUser.getName()));
}

document.getElementById("onionr-post-creator-user-id").onclick = viewCurrentProfile;
document.getElementById("onionr-post-creator-user-name").onclick = viewCurrentProfile;

// on some browsers it saves the user input on reload. So, it should also recheck the input.
postCreatorChange();
