/*
    Onionr - Private P2P Communication

    Handles onboarding donations for Onionr

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
*/


let donateFinishedButtons = document.getElementsByClassName('donateFinished')
configInfo = {}

let openDonateModal = function(newConfigInfo){
    fetch('donate-modal.html')
        .then((resp) => resp.text())
        .then(function(resp) {
            document.getElementsByClassName('donateModal')[0].classList.add('is-active')

            // Load the donate modal html and display it
            let donateBody = document.getElementsByClassName('donateBody')[0]

            donateBody.innerHTML = resp

            let donateFinishedButton = document.getElementsByClassName('donateFinished')[0]

            for (i = 0; i < donateFinishedButtons.length; i++){
                donateFinishedButtons[i].onclick = function(){
                    document.getElementsByClassName('donateModal')[0].classList.remove('is-active')
                    sendConfig(configInfo)
                }
            }
            
    })
}
