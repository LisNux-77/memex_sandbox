function docReady(fn) {
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(fn, 1);
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

docReady(function() {
  var coll = document.getElementsByClassName('collapsible');
  var i;
  console.log(coll.length);
  for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener('click', function() {
      this.classList.toggle('active');
      var content = this.nextElementSibling;
      if (content.style.maxHeight) {
        content.style.maxHeight = null;
      } else {
        content.style.maxHeight = content.scrollHeight + 'px';
      }
    });
  }
});

function getPath() {
  let href = document.location.href;
  // create a tml element to use in copy process!
  let tempElem = document.createElement('textarea');
  tempElem.value = "[MEMEX_TO_OBSIDIAN](<" + href + ">)";
  document.body.appendChild(tempElem);
  tempElem.select();
  document.execCommand('copy');
  document.body.removeChild(tempElem);
};

function getPathOld() {
  let href = document.location.href;
  // create a tml element to use in copy process!
  let tempElem = document.createElement('textarea');
  if (href.startsWith('file://'))
    href = href.replace('file://', '');
  tempElem.value = href;
  document.body.appendChild(tempElem);
  tempElem.select();
  document.execCommand('copy');
  document.body.removeChild(tempElem);
};
