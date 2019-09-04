fetch('shared/about.html')
  .then(resp=>resp.text())
  .then(function(response) {
      aboutText = response
  })