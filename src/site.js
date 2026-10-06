// Supplier enquiry form: opens the visitor's email app with the message filled in.
(function () {
  var form = document.getElementById('enquiry-form');
  if (!form) return;
  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var v = function (n) { return form.elements[n].value.trim(); };
    var subject = 'Supplier enquiry: ' + v('company');
    var body = v('message') + '\n\n' + v('name') + '\n' + v('company');
    window.location.href = 'mailto:' + form.dataset.to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    document.getElementById('f-hint').textContent = 'Your email app should now be open. If nothing happened, write to ' + form.dataset.to + '.';
  });
})();
