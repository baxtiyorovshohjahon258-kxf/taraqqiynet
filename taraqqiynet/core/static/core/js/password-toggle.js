(function () {
  var css = '.pw-wrap{position:relative;display:block}' +
    '.pw-wrap input{width:100%;padding-right:46px;box-sizing:border-box}' +
    '.pw-toggle{position:absolute;right:12px;top:50%;transform:translateY(-50%);' +
    'background:none;border:none;cursor:pointer;color:#9aa7c7;padding:4px;display:flex;align-items:center}' +
    '.pw-toggle:hover{color:#3d7fff}';
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">';
  var EYE = svg + '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
  var EYE_OFF = svg + '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';

  document.querySelectorAll('input[type="password"]').forEach(function (input) {
    if (input.parentNode.classList.contains('pw-wrap')) return;
    var wrap = document.createElement('div');
    wrap.className = 'pw-wrap';
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pw-toggle';
    btn.innerHTML = EYE;
    btn.addEventListener('click', function () {
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.innerHTML = show ? EYE_OFF : EYE;
    });
    wrap.appendChild(btn);
  });
})();