/*
    Onionr - Private P2P Communication

    detect for Circles if plaintext insert/storage is enabled

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
plaintext_enabled = null

fetch('/config/get/general.store_plaintext_blocks', {
    method: 'GET',
    headers: {
      "token": webpass
    }})
.then((resp) => resp.text())
.then(function(data) {
    plaintext_enabled = true
    if (data == "false"){
        plaintext_enabled = false
        PNotify.error({
            text: "Plaintext storage is disabled. You will not be able to see new posts or make posts yourself"
        })
    }
})
