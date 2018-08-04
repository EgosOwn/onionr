/* write a random post to the page, for testing */

var verbs =
[
    ["go to", "goes to", "going to", "went to", "gone to"],
    ["look at", "looks at", "looking at", "looked at", "looked at"],
    ["choose", "chooses", "choosing", "chose", "chosen"],
    ["torrent", "downloads", "downloading", "torrented", "downloaded"],
    ["detonate", "detonates", "detonating", "detonated", "detonated"],
    ["run", "runs", "running", "ran", "running"],
    ["program", "programs", "programming", "coded", "programmed"],
    ["start", "starts", "starting", "started", "started"]
];
var tenses =
[
    {name:"Present", singular:1, plural:0, format:"%subject %verb %complement"},
    {name:"Present", singular:1, plural:0, format:"%subject %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject just %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject just %verb %complement lol"},
    {name:"Past", singular:3, plural:3, format:"%subject %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject just %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject just %verb %complement lol"},
    {name:"Past", singular:3, plural:3, format:"%subject %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject just %verb %complement"},
    {name:"Past", singular:3, plural:3, format:"%subject just %verb %complement lol"},
    {name:"Present Continues", singular:2, plural:2, format:"%subject %be %verb %complement"}
];
var subjects =
[
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"I", be:"am", singular:0},
    {name:"My cat", be:"is", singular:0},
    {name:"My cat", be:"is", singular:0},
    {name:"My dog", be:"is", singular:0},
    {name:"My dog", be:"is", singular:0},
    {name:"My mom", be:"is", singular:0},
    {name:"My dad", be:"is", singular:0},
    {name:"You", be:"are", singular:0},
    {name:"He", be:"is", singular:1}
];
var complementsForVerbs =
[
    ["the cinema", "Egypt", "the house", "the concert"],
    ["for a map", "them", "the stars", "the lake"],
    ["a book for reading", "a dvd for tonight"],
    ["the virus", "the malware", "that 0day", "Onionr"],
    ["a bomb", "a nuke", "some C4", "some ammonium nitrate"],
    ["the race", "towards someone", "to the stars", "on top of your roof"],
    ["Onionr", "the malware", "some software", "Onionr"],
    ["Onionr", "Onionr", "the race", "the timer"],
]

Array.prototype.random = function(){return this[Math.floor(Math.random() * this.length)];};

function generate(){
    var index = Math.floor(verbs.length * Math.random());
    var tense = tenses.random();
    var subject = subjects.random();
    var verb = verbs[index];
    var complement = complementsForVerbs[index];
    var str = tense.format;
    str = str.replace("%subject", subject.name).replace("%be", subject.be);
    str = str.replace("%verb", verb[subject.singular ? tense.singular : tense.plural]);
    str = str.replace("%complement", complement.random());
    return str;
}

var curDate = new Date()
function addRandomPost() {
    var post = new Post();
    var user = new User();
    var items = ['arinerron', 'beardog108', 'samyk', 'snowden', 'aaronswartz'];
    user.setName(items[Math.floor(Math.random()*items.length)]);
    user.setID('i-eat-waffles-often-its-actually-crazy-like-i-dont-know-wow');
    post.setContent(generate());
    post.setUser(user);

    curDate = new Date(curDate - (Math.random() * 1000000));
    post.setPostDate(curDate);

    document.getElementById('onionr-timeline-posts').innerHTML += post.getHTML();
}

for(var i = 0; i < Math.round(50 * Math.random()); i++)
    addRandomPost();

function viewProfile(id, name) {
    document.getElementById("onionr-profile-username").innerHTML = encodeHTML(decodeURIComponent(name));
}
