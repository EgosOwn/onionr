
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

var usermap = JSON.parse(get('usermap', '{}'));

function getUserMap() {
    return usermap;
}

function deserializeUser(id) {
    var serialized = getUserMap()[id]
    var user = new User();
    user.setName(serialized['name']);
    user.setID(serialized['id']);
    user.setIcon(serialized['icon']);
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

/* sanitizes HTML in a string */
function encodeHTML(html) {
    return String(html).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* URL encodes a string */
function encodeURL(url) {
    return encodeURIComponent(url);
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
        var postTemplate = '<$= jsTemplate('onionr-timeline-post') $>';

        var device = (jQuery(document).width() < 768 ? 'mobile' : 'desktop');

        postTemplate = postTemplate.replaceAll('$user-name-url', encodeHTML(encodeURL(this.getUser().getName())));
        postTemplate = postTemplate.replaceAll('$user-name', encodeHTML(this.getUser().getName()));
        postTemplate = postTemplate.replaceAll('$user-id-url', encodeHTML(encodeURL(this.getUser().getID())));
        postTemplate = postTemplate.replaceAll('$user-id-truncated', encodeHTML(this.getUser().getID().split('-').slice(0, 4).join('-')));
        postTemplate = postTemplate.replaceAll('$user-id', encodeHTML(this.getUser().getID()));
        postTemplate = postTemplate.replaceAll('$user-image', encodeHTML(this.getUser().getIcon()));
        postTemplate = postTemplate.replaceAll('$content', encodeHTML(this.getContent()));
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
