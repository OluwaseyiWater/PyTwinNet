(function() {
  function swapLogo(){
    var img = document.querySelector('.wy-side-nav-search img, .sidebar-logo img, .logo img');
    if(!img) return;
    const dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    img.src = dark ? '_static/img/pytwinnet-logo-dark.svg' : '_static/img/pytwinnet-logo.svg';
  }
  swapLogo();
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', swapLogo);
  }
})();
