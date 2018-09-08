
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

                            user.remember();

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
            callback(user);
            return user;
        }
    }
}

/* post class */
class Post {
    /* returns the html content of a post */
    getHTML() {
        var postTemplate = '<$= jsTemplate('onionr-timeline-post') $>';

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
            postTemplate = postTemplate.replaceAll('$liked', '<$= LANG.POST_UNLIKE $>');
        } else {
            postTemplate = postTemplate.replaceAll('$liked', '<$= LANG.POST_LIKE $>');
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
    var url = '/client/?action=info&token=' + Sanitize.url(getWebPassword()) + '&timingToken=' + Sanitize.url(getTimingToken());

    console.log(url);

    var http = new XMLHttpRequest();

    // sync

    http.open('GET', url, false);
    http.send(null);

    var id = JSON.parse(http.responseText)['pubkey'];

    User.getUser(id, function(data) {
        if(data === null || data === undefined) {
            jQuery('#modal').modal('show');

            var user = new User();

            user.setName('New User');
            user.setID(id);
            user.setIcon('<$= Template.jsTemplate("default-icon") $>');
            user.setDescription('A new OnionrUI user');

            user.remember();
            user.save();

            setCurrentUser(user);

            window.location.reload();
        } else {
            setCurrentUser(data);
        }
    });
}

currentUser = getCurrentUser();
