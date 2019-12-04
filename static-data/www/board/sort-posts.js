/*
    Onionr - Private P2P Communication

    Sort post entries

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

function sortEntries(){
    var entries = document.getElementsByClassName('entry')

    var timestamp = 0;
    if (entries.length > 0){
        timestamp = entries[0].getAttribute('timestamp')
    }

    for (i = 0; i < entries.length; i++){
        console.log(i)
        if (entries[i].getAttribute('timestamp') > timestamp){
            if(entries[i].previousElementSibling){
                entries[i].parentNode.insertBefore(entries[i], entries[i].previousElementSibling)
            }
        }
    }

}