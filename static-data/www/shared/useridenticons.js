function toHexString(byteArray) {
    // cc-by-sa-4 https://stackoverflow.com/a/44608819 by https://stackoverflow.com/users/1883624/grantpatterson
    var s = '0x';
    byteArray.forEach(function(byte) {
      s += ('0' + (byte & 0xFF).toString(16)).slice(-2);
    });
    return s;
  }

function userIcon(pubkey, imgSize=64){
    pubkey = toHexString(base32.decode.asBytes(pubkey))
    let options = {
        //foreground: [0,0,0,1],               // rgba black
        background: [255, 255, 255, 255],         // rgba white
        //margin: 0.1,
        size: imgSize,
        format: 'svg'                             // use SVG instead of PNG
        };

    // create a base64 encoded SVG
    let data = new Identicon(pubkey, options).toString();
    return data
}