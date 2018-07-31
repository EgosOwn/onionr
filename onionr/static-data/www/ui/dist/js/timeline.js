/* write a random post to the page, for testing */
function addRandomPost() {
    var post = new Post();
    var user = new User();
    var items = ['arinerron', 'beardog108', 'samyk', 'snowden', 'aaronswartz'];
    user.setName(items[Math.floor(Math.random()*items.length)]);
    user.setID('i-eat-waffles-often-its-actually-crazy-like-i-dont-know-wow');
    post.setContent('spammm ' + btoa(Math.random() + ' wow'));
    post.setUser(user);
    post.setPostDate(new Date(new Date() - (Math.random() * 1000000)));
    
    document.getElementById('onionr-timeline-posts').innerHTML += post.getHTML();
}

for(var i = 0; i < Math.round(50 * Math.random()); i++)
    addRandomPost();
    
function viewProfile(id, name) {
    document.getElementById("onionr-profile-username").innerHTML = encodeHTML(decodeURIComponent(name));
}
