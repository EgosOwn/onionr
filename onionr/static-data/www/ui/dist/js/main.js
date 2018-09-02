
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

function getUserMap() {
    return usermap;
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

function serializeUser(user) {
    if(user !== null && user !== undefined) {
        var serialized = {'name' : user.getName(), 'id' : user.getID(), 'icon' : user.getIcon()};

        usermap[user.getID()] = serialized;

        set('usermap', JSON.stringify(getUserMap()));

        return serialized;
    }
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
String.prototype.replaceAll = function(search, replacement) {
    // taken from https://stackoverflow.com/a/17606289/3678023
    var target = this;
    return target.split(search).join(replacement);
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

    serialize() {
        return {
            'name' : this.getName(),
            'id' : this.getID(),
            'icon' : this.getIcon()
        };
    }

    remember() {
        usermap[this.getID()] = this.serialize();
        set('usermap', JSON.stringify(usermap));
    }
}

/* post class */
class Post {
    /* returns the html content of a post */
    getHTML() {
        var postTemplate = '<!-- POST -->\
<div class="col-12">\
    <div class="onionr-post">\
        <div class="row">\
            <div class="col-2">\
                <img class="onionr-post-user-icon" src="$user-image">\
            </div>\
            <div class="col-10">\
                <div class="row">\
                    <div class="col col-auto">\
                        <a class="onionr-post-user-name" href="#!" onclick="viewProfile(\'$user-id-url\', \'$user-name-url\')">$user-name</a>\
                        <a class="onionr-post-user-id" href="#!" onclick="viewProfile(\'$user-id-url\', \'$user-name-url\')" data-placement="top" data-toggle="tooltip" title="$user-id">$user-id-truncated</a>\
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
                    <a href="#!" onclick="toggleLike(\'$post-id\')" class="glyphicon glyphicon-heart mr-2">like</a>\
                    <a href="#!" onclick="reply(\'$post-id\')" class="glyphicon glyphicon-comment mr-2">reply</a>\
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
        postTemplate = postTemplate.replaceAll('$content', Sanitize.html(this.getContent()));
        postTemplate = postTemplate.replaceAll('$date-relative', timeSince(this.getPostDate(), device) + (device === 'desktop' ?  ' ago' : ''));
        postTemplate = postTemplate.replaceAll('$date', this.getPostDate().toLocaleString());

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

if(getWebPassword() === null) {
    var password = "";
    while(password.length != 64) {
        password = prompt("Please enter the web password (run `./RUN-LINUX.sh --get-password`)");
    }

    setTimingToken(prompt("Please enter the timing token (optional)"));

    setWebPassword(password);
    window.location.reload(true);
}

var tt = getParameter("timingToken");
if(tt !== null && tt !== undefined) {
    setTimingToken(tt);
}
