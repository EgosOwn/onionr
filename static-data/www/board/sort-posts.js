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

function sortEntries() {
    var entries = document.getElementsByClassName('entry')

    if (entries.length > 1) {
        const sortBy = 'timestamp'
        const parent = entries[0].parentNode

        const sorted = Array.from(entries).sort((a, b) => b.getAttribute(sortBy) - a.getAttribute(sortBy))
        sorted.forEach(element => parent.appendChild(element))
    }
}
