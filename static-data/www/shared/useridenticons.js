/*
    Onionr - Private P2P Communication

    Provides userIcon which generates SVG identicons from a Onionr user pubkey

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/
function toHexString(byteArray) {
    // cc-by-sa-4 https://stackoverflow.com/a/44608819 by https://stackoverflow.com/users/1883624/grantpatterson
    var s = '0x'
    byteArray.forEach(function(byte) {
      s += ('0' + (byte & 0xFF).toString(16)).slice(-2)
    })
    return s
  }

  async function sha256(str) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder("utf-8").encode(str))
    return Array.prototype.map.call(new Uint8Array(buf), x=>(('00'+x.toString(16)).slice(-2))).join('')
  }  

async function userIcon(pubkey, imgSize=64){
    pubkey = await sha256(base32.decode.asBytes(pubkey))
    let options = {
        //foreground: [0,0,0,1],               // rgba black
        background: [0, 0, 0, 0],         // rgba white
        //margin: 0.1,
        size: imgSize,
        format: 'svg'                             // use SVG instead of PNG
        };

    // create a base64 encoded SVG
    let data = new Identicon(pubkey, options).toString();
    return data
}