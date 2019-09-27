function toHexString(byteArray) {
    // cc-by-sa-4 https://stackoverflow.com/a/44608819 by https://stackoverflow.com/users/1883624/grantpatterson
    var s = '0x';
    byteArray.forEach(function(byte) {
      s += ('0' + (byte & 0xFF).toString(16)).slice(-2);
    });
    return s;
  }

  async function sha256(str) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder("utf-8").encode(str));
    return Array.prototype.map.call(new Uint8Array(buf), x=>(('00'+x.toString(16)).slice(-2))).join('');
  }  

async function userIcon(pubkey, imgSize=64){
    pubkey = await sha256(base32.decode.asBytes(pubkey))
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