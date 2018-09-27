
/* handy localstorage functions for quick usage */

function set(key, val) {
    return localStorage.setItem(key, val);
}

function get(key, df) { // df is default
    value = localStorage.getItem(key);
    if(value == null)
        value = df;

    return value;
}

function remove(key) {
    return localStorage.removeItem(key);
}

function getParameter(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

/* usermap localStorage stuff */

var usermap = JSON.parse(get('usermap', '{}'));
var postmap = JSON.parse(get('postmap', '{}'))

function getUserMap() {
    return usermap;
}

function getPostMap(hash) {
    if(hash !== undefined) {
        if(hash in postmap)
            return postmap[hash];
        return null;
    }

    return postmap;
}

function deserializeUser(id) {
    if(!(id in getUserMap()))
        return null;

    var serialized = getUserMap()[id]
    var user = new User();

    user.setName(serialized['name']);
    user.setID(serialized['id']);
    user.setIcon(serialized['icon']);
    user.setDescription(serialized['description']);

    return user;
}

function getCurrentUser() {
    var user = get('currentUser', null);

    if(user === null)
        return null;

    return User.getUser(user, function() {});
}

function setCurrentUser(user) {
    set('currentUser', user.getID());
}

/* returns a relative date format, e.g. "5 minutes" */
function timeSince(date, size) {
    // taken from https://stackoverflow.com/a/3177838/3678023

    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = Math.floor(seconds / 31536000);

    if (size === null)
        size = 'desktop';

    var dates = {
        'mobile' : {
            'yr' : 'yrs',
            'mo' : 'mo',
            'd' : 'd',
            'hr' : 'h',
            'min' : 'm',
            'secs' : 's',
            'sec' : 's',
        },

        'desktop' : {
            'yr' : ' years',
            'mo' : ' months',
            'd' : ' days',
            'hr' : ' hours',
            'min' : ' minutes',
            'secs' : ' seconds',
            'sec' : ' second',
        },
    };

    if (interval > 1)
        return interval + dates[size]['yr'];
    interval = Math.floor(seconds / 2592000);

    if (interval > 1)
        return interval + dates[size]['mo'];
    interval = Math.floor(seconds / 86400);

    if (interval > 1)
        return interval + dates[size]['d'];
    interval = Math.floor(seconds / 3600);

    if (interval > 1)
        return interval + dates[size]['hr'];
    interval = Math.floor(seconds / 60);

    if (interval > 1)
        return interval + dates[size]['min'];

    if(Math.floor(seconds) !== 1)
        return Math.floor(seconds) + dates[size]['secs'];

    return '1' + dates[size]['sec'];
}

/* replace all instances of string */
String.prototype.replaceAll = function(search, replacement, limit) {
    // taken from https://stackoverflow.com/a/17606289/3678023
    var target = this;
    return target.split(search, limit).join(replacement);
};

/* useful functions to sanitize data */
class Sanitize {
    /* sanitizes HTML in a string */
    static html(html) {
        return String(html).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    /* URL encodes a string */
    static url(url) {
        return encodeURIComponent(url);
    }

    /* usernames */
    static username(username) {
        return String(username).replace(/[\W_]+/g, " ").substring(0, 25);
    }

    /* profile descriptions */
    static description(description) {
        return String(description).substring(0, 128);
    }
}

/* config stuff */
function getWebPassword() {
    return get("web-password", null);
}

function setWebPassword(password) {
    return set("web-password", password);
}

function getTimingToken() {
    return get("timing-token", null);
}

function setTimingToken(token) {
    return set("timing-token", token);
}

/* user class */
class User {
    constructor() {
        this.name = 'Unknown';
        this.id = 'unknown';
        this.image = 'img/default.png';
    }

    setName(name) {
        this.name = name;
    }

    getName() {
        return this.name;
    }

    setID(id) {
        this.id = id;
    }

    getID() {
        return this.id;
    }

    setIcon(image) {
        this.image = image;
    }

    getIcon() {
        return this.image;
    }

    setDescription(description) {
        this.description = description;
    }

    getDescription() {
        return this.description;
    }

    serialize() {
        return {
            'name' : this.getName(),
            'id' : this.getID(),
            'icon' : this.getIcon(),
            'description' : this.getDescription()
        };
    }

    /* save in usermap */
    remember() {
        usermap[this.getID()] = this.serialize();
        set('usermap', JSON.stringify(usermap));
    }

    /* save as a block */
    save(callback) {
        var block = new Block();

        block.setType('onionr-user');
        block.setContent(JSON.stringify(this.serialize()));

        return block.save(true, callback);
    }

    static getUser(id, callback) {
        console.log(callback);
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
                            user.setDescription(userInfo['description']);
                            user.setID(id);

                            user.remember();
                            console.log(callback);
                            callback(user);
                            return user;
                        }
                    } catch(e) {
                        console.log(e);

                        callback(null);
                        return null;
                    }
                } else {
                    callback(null);
                    return null;
                }
            });
        } else {
            console.log(callback);
            callback(user);
            return user;
        }
    }
}

/* post class */
class Post {
    /* returns the html content of a post */
    getHTML() {
        var postTemplate = '<!-- POST -->\
<div class="col-12">\
    <div class="onionr-post" id="onionr-post-$post-hash" onclick="focusPost(\'$post-hash\', \'user-id-url\', \'user-name-url\', \'\')">\
        <div class="row">\
            <div class="col-2">\
                <img class="onionr-post-user-icon" src="$user-image">\
            </div>\
            <div class="col-10">\
                <div class="row">\
                    <div class="col col-auto">\
                        <a class="onionr-post-user-name" id="onionr-post-user-name" href="#!" onclick="viewProfile(\'$user-id-url\', \'$user-name-url\')">$user-name</a>\
                        <a class="onionr-post-user-id" id="onionr-post-user-id" href="#!" onclick="viewProfile(\'$user-id-url\', \'$user-name-url\')" data-placement="top" data-toggle="tooltip" title="$user-id">$user-id-truncated</a>\
                    </div>\
\
                    <div class="col col-auto text-right ml-auto pl-0">\
                        <div class="onionr-post-date text-right" data-placement="top" data-toggle="tooltip" title="$date">$date-relative</div>\
                    </div>\
                </div>\
\
                <div class="onionr-post-content">\
                    $content\
                </div>\
\
                <div class="onionr-post-controls pt-2">\
                    <a href="#!" onclick="toggleLike(\'$post-hash\')" class="glyphicon glyphicon-heart mr-2">$liked</a>\
                    <a href="#!" onclick="reply(\'$post-hash\')" class="glyphicon glyphicon-comment mr-2">reply</a>\
                </div>\
            </div>\
        </div>\
    </div>\
</div>\
<!-- END POST -->\
';

        var device = (jQuery(document).width() < 768 ? 'mobile' : 'desktop');

        postTemplate = postTemplate.replaceAll('$user-name-url', Sanitize.html(Sanitize.url(this.getUser().getName())));
        postTemplate = postTemplate.replaceAll('$user-name', Sanitize.html(this.getUser().getName()));
        postTemplate = postTemplate.replaceAll('$user-id-url', Sanitize.html(Sanitize.url(this.getUser().getID())));

        postTemplate = postTemplate.replaceAll('$user-id-truncated', Sanitize.html(this.getUser().getID().substring(0, 12) + '...'));
        // postTemplate = postTemplate.replaceAll('$user-id-truncated', Sanitize.html(this.getUser().getID().split('-').slice(0, 4).join('-')));

        postTemplate = postTemplate.replaceAll('$user-id', Sanitize.html(this.getUser().getID()));
        postTemplate = postTemplate.replaceAll('$user-image', "data:image/jpeg;base64," + Sanitize.html(this.getUser().getIcon()));
        postTemplate = postTemplate.replaceAll('$content', Sanitize.html(this.getContent()).replaceAll('\n', '<br />', 16)); // Maximum of 16 lines
        postTemplate = postTemplate.replaceAll('$post-hash', this.getHash());
        postTemplate = postTemplate.replaceAll('$date-relative', timeSince(this.getPostDate(), device) + (device === 'desktop' ?  ' ago' : ''));
        postTemplate = postTemplate.replaceAll('$date', this.getPostDate().toLocaleString());

        if(this.getHash() in getPostMap() && getPostMap()[this.getHash()]['liked']) {
            postTemplate = postTemplate.replaceAll('$liked', 'unlike');
        } else {
            postTemplate = postTemplate.replaceAll('$liked', 'like');
        }

        return postTemplate;
    }

    setUser(user) {
        this.user = user;
    }

    getUser() {
        return this.user;
    }

    setContent(content) {
        this.content = content;
    }

    getContent() {
        return this.content;
    }

    setPostDate(date) { // unix timestamp input
        if(date instanceof Date)
            this.date = date;
        else
            this.date = new Date(date * 1000);
    }

    getPostDate() {
        return this.date;
    }

    setHash(hash) {
        this.hash = hash;
    }

    getHash() {
        return this.hash;
    }

    save(callback) {
        var args = {'type' : 'onionr-post', 'sign' : true, 'content' : JSON.stringify({'content' : this.getContent()})};

        var url = '/client/?action=insertBlock&data=' + Sanitize.url(JSON.stringify(args)) + '&token=' + Sanitize.url(getWebPassword()) + '&timingToken=' + Sanitize.url(getTimingToken());

        console.log(url);

        var http = new XMLHttpRequest();

        if(callback !== undefined) {
            // async

            var thisObject = this;

            http.addEventListener('load', function() {
                thisObject.setHash(Block.parseBlockArray(JSON.parse(http.responseText)['hash']));
                callback(thisObject.getHash());
            }, false);

            http.open('GET', url, true);
            http.timeout = 5000;
            http.send(null);
        } else {
            // sync

            http.open('GET', url, false);
            http.send(null);

            this.setHash(Block.parseBlockArray(JSON.parse(http.responseText)['hash']));

            return this.getHash();
        }
    }
}

/* block class */
class Block {
    constructor(type, content) {
        this.type = type;
        this.content = content;
    }

    // returns the block hash, if any
    getHash() {
        return this.hash;
    }

    // returns the block type
    getType() {
        return this.type;
    }

    // returns the block header
    getHeader(key, df) { // df is default
        if(key !== undefined) {
            if(this.getHeader().hasOwnProperty(key))
                return this.getHeader()[key];
            else
                return (df === undefined ? null : df);
        } else
            return this.header;
    }

    // returns the block metadata
    getMetadata(key, df) { // df is default
        if(key !== undefined) {
            if(this.getMetadata().hasOwnProperty(key))
                return this.getMetadata()[key];
            else
                return (df === undefined ? null : df);
        } else
            return this.metadata;
    }

    // returns the block content
    getContent() {
        return this.content;
    }

    // returns the parent block's hash (not Block object, for performance)
    getParent() {
        if(!(this.parent instanceof Block) && this.parent !== undefined && this.parent !== null)
            this.parent = Block.openBlock(this.parent); // convert hash to Block object
        return this.parent;
    }

    // returns the date that the block was received
    getDate() {
        return this.date;
    }

    // returns a boolean that indicates whether or not the block is valid
    isValid() {
        return this.valid;
    }

    // returns a boolean thati ndicates whether or not the block is signed
    isSigned() {
        return this.signed;
    }

    // returns the block signature
    getSignature() {
        return this.signature;
    }

    // returns the block type
    setType(type) {
        this.type = type;
        return this;
    }

    // sets block metadata by key
    setMetadata(key, val) {
        this.metadata[key] = val;
        return this;
    }

    // sets block content
    setContent(content) {
        this.content = content;
        return this;
    }

    // sets the block parent by hash or Block object
    setParent(parent) {
        this.parent = parent;
        return this;
    }

    // indicates if the Block exists or not
    exists() {
        return !(this.hash === null || this.hash === undefined);
    }

    // saves the block, returns the hash
    save(sign, callback) {
        var type = this.getType();
        var content = this.getContent();
        var parent = this.getParent();

        if(content !== undefined && content !== null && type !== '') {
            var args = {'content' : content};

            if(type !== undefined && type !== null && type !== '')
                args['type'] = type;
            if(parent !== undefined && parent !== null && parent.getHash() !== undefined && parent.getHash() !== null && parent.getHash() !== '')
                args['parent'] = parent.getHash();
            if(sign !== undefined && sign !== null)
                args['sign'] = String(sign) !== 'false'


            var url = '/client/?action=insertBlock&data=' + Sanitize.url(JSON.stringify(args)) + '&token=' + Sanitize.url(getWebPassword()) + '&timingToken=' + Sanitize.url(getTimingToken());

            console.log(url);

            var http = new XMLHttpRequest();

            if(callback !== undefined) {
                // async

                http.addEventListener('load', function() {
                    callback(Block.parseBlockArray(JSON.parse(http.responseText)['hash']));
                }, false);

                http.open('GET', url, true);
                http.timeout = 5000;
                http.send(null);
            } else {
                // sync

                http.open('GET', url, false);
                http.send(null);

                return Block.parseBlockArray(JSON.parse(http.responseText)['hash']);
            }
        }

        return false;
    }

    /* static functions */

    // recreates a block by hash
    static openBlock(hash) {
        return parseBlock(response);
    }

    // converts an associative array to a Block
    static parseBlock(val) {
        var block = new Block();

        block.type = val['type'];
        block.content = val['content'];
        block.header = val['header'];
        block.metadata = val['metadata'];
        block.date = new Date(val['date'] * 1000);
        block.hash = val['hash'];
        block.signature = val['signature'];
        block.signed = val['signed'];
        block.valid = val['valid'];
        block.parent = val['parent'];

        if(block.getParent() !== null) {
            // if the block data is already in the associative array

            /*
            if (blocks.hasOwnProperty(block.getParent()))
                block.setParent(Block.parseAssociativeArray({blocks[block.getParent()]})[0]);
            */
        }

        return block;
    }

    // converts an array of associative arrays to an array of Blocks
    static parseBlockArray(blocks) {
        var outputBlocks = [];

        for(var key in blocks) {
            if(blocks.hasOwnProperty(key)) {
                var val = blocks[key];

                var block = Block.parseBlock(val);

                outputBlocks.push(block);
            }
        }

        return outputBlocks;
    }

    static getBlocks(args, callback) { // callback is optional
        args = args || {}

        var url = '/client/?action=searchBlocks&data=' + Sanitize.url(JSON.stringify(args)) + '&token=' + Sanitize.url(getWebPassword()) + '&timingToken=' + Sanitize.url(getTimingToken());

        console.log(url);

        var http = new XMLHttpRequest();

        if(callback !== undefined) {
            // async

            http.addEventListener('load', function() {
                callback(Block.parseBlockArray(JSON.parse(http.responseText)['blocks']));
            }, false);

            http.open('GET', url, true);
            http.timeout = 5000;
            http.send(null);
        } else {
            // sync

            http.open('GET', url, false);
            http.send(null);

            return Block.parseBlockArray(JSON.parse(http.responseText)['blocks']);
        }
    }
}

/* temporary code */

var tt = getParameter("timingToken");
if(tt !== null && tt !== undefined) {
    setTimingToken(tt);
}

if(getWebPassword() === null) {
    var password = "";
    while(password.length != 64) {
        password = prompt("Please enter the web password (run `./RUN-LINUX.sh --get-password`)");
    }

    setWebPassword(password);
}

if(getCurrentUser() === null) {
    jQuery('#modal').modal('show');

    var url = '/client/?action=info&token=' + Sanitize.url(getWebPassword()) + '&timingToken=' + Sanitize.url(getTimingToken());

    console.log(url);

    var http = new XMLHttpRequest();

    // sync

    http.addEventListener('load', function() {
        var id = JSON.parse(http.responseText)['pubkey'];

        User.getUser(id, function(data) {
            if(data === null || data === undefined) {
                var user = new User();

                user.setName('New User');
                user.setID(id);
                user.setIcon('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\
');
                user.setDescription('A new OnionrUI user');

                user.remember();
                user.save();

                setCurrentUser(user);
            } else {
                setCurrentUser(data);
            }

            window.location.reload();
        });
    }, false);

    http.open('GET', url, true);
    http.send(null);
}

currentUser = getCurrentUser();
