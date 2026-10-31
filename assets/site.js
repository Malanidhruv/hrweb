/**
 * Harion Research — Minimal Progressive Enhancement JS
 * Navigation accessibility, client-side contact form validation,
 * and privacy-friendly analytics event dispatch.
 */
(function () {
  'use strict';

  // Mobile nav Escape key and aria-expanded sync
  var toggle = document.getElementById('nav-toggle');
  var burger = document.querySelector('label.burger');

  if (toggle && burger) {
    toggle.addEventListener('change', function () {
      burger.setAttribute('aria-expanded', toggle.checked ? 'true' : 'false');
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.checked) {
        toggle.checked = false;
        burger.setAttribute('aria-expanded', 'false');
        burger.focus();
      }
    });

    // Close mobile menu when a nav link is tapped
    var nav = document.querySelector('.site-nav');
    if (nav) {
      nav.addEventListener('click', function (e) {
        if (e.target.tagName === 'A' && toggle.checked) {
          toggle.checked = false;
          burger.setAttribute('aria-expanded', 'false');
        }
      });
    }
  }

  // Named Analytics Events (Plausible or GA4 if configured)
  document.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('[data-event]') : null;
    if (!el) return;
    var eventName = el.getAttribute('data-event');
    if (!eventName) return;
    if (typeof window.plausible === 'function') {
      window.plausible(eventName);
    } else if (typeof window.gtag === 'function') {
      window.gtag('event', eventName);
    }
  });

  // Contact form basic client-side validation, honeypot check & mailto fallback
  var form = document.querySelector('form[data-contact-form]');
  if (form) {
    form.addEventListener('submit', function (e) {
      var hp = form.querySelector('input[name="botcheck"]');
      if (hp && hp.value) {
        e.preventDefault();
        return;
      }
      var action = form.getAttribute('action') || '';
      var hasKey = form.querySelector('input[name="access_key"]');
      if (action.indexOf('web3forms.com') !== -1 && !hasKey) {
        e.preventDefault();
        var name = (form.querySelector('[name="name"]') || {}).value || '';
        var email = (form.querySelector('[name="email"]') || {}).value || '';
        var subject = (form.querySelector('[name="subject"]') || {}).value || 'Website Enquiry';
        var message = (form.querySelector('[name="message"]') || {}).value || '';
        var body = 'Name: ' + name + '\nEmail: ' + email + '\n\n' + message;
        window.location.href = 'mailto:info@harionresearch.co.in?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      }
    });
  }
})();
