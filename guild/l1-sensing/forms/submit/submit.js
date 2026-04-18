// Article submission form — client-side validation + word counts.
(function () {
  'use strict';

  var form      = document.getElementById('submitForm');
  var status    = document.getElementById('formStatus');
  var submitBtn = document.getElementById('submitBtn');
  if (!form) return;

  // Live word counters
  function countWords(s) {
    return (s || '').trim().split(/\s+/).filter(Boolean).length;
  }
  function wireCounter(textareaName, spanId) {
    var ta   = form.querySelector('[name="entry.' + textareaName + '"]');
    var span = document.getElementById(spanId);
    if (!ta || !span) return;
    ta.addEventListener('input', function () {
      span.textContent = countWords(ta.value);
    });
  }
  wireCounter('abstract', 'abstractWords');
  wireCounter('body',     'bodyWords');

  // Minimum word rules from the Article Submission Standard
  function validate() {
    var errors = [];
    var abstractWords = countWords(form.querySelector('[name="entry.abstract"]').value);
    var bodyWords     = countWords(form.querySelector('[name="entry.body"]').value);
    var type          = form.querySelector('[name="entry.type"]').value;

    if (abstractWords < 60 || abstractWords > 400) {
      errors.push('Abstract must be 60–400 words (you have ' + abstractWords + ').');
    }
    var minBody = (type === 'research-note') ? 300 : 800;
    if (bodyWords < minBody) {
      errors.push('Body must be ≥ ' + minBody + ' words for type "' + type + '" (you have ' + bodyWords + ').');
    }
    return errors;
  }

  form.addEventListener('submit', function (e) {
    var errors = validate();
    if (errors.length) {
      e.preventDefault();
      status.className = 'form-status error';
      status.innerHTML = errors.map(function (x) { return '• ' + x; }).join('<br>');
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting…';
    // Success feedback after the iframe round-trip
    setTimeout(function () {
      status.className = 'form-status success';
      status.textContent = 'Thank you. Your submission is queued for review. Expect a response within 7 days.';
      form.reset();
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Article';
      document.getElementById('abstractWords').textContent = '0';
      document.getElementById('bodyWords').textContent = '0';
    }, 1200);
  });
})();
