let skipConsentBtns = function(){
    var skipBtn = document.getElementsByClassName('skipToConsent')[0]
    var sections = document.getElementsByClassName('step-item')
    var content = document.getElementsByClassName('step-content')
    skipBtn.onclick = function(e){
        e.preventDefault()
        for (el of document.querySelectorAll('.steps-action a')){
            el.classList.add('is-hidden')
        }
        for (el of content){
            el.classList.remove('is-active')
            var last = el
        }
        last.classList.add('is-active')
        for (el = 0; el <= sections.length; el++){
            sections[el].classList.add('is-completed')
            sections[el].classList.remove('is-active')
            var last = sections[el]
        }
        last.classList.add('is-active')

        //is-completed
    }
}()