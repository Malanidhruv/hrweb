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

  // Contact form: formats enquiry and sends directly to WhatsApp (+91-7067000393)
  var form = document.querySelector('form[data-contact-form]');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var hp = form.querySelector('input[name="botcheck"]');
      if (hp && (hp.checked || hp.value)) {
        return;
      }
      var name = ((form.querySelector('[name="name"]') || {}).value || '').trim();
      var email = ((form.querySelector('[name="email"]') || {}).value || '').trim();
      var subject = ((form.querySelector('[name="subject"]') || {}).value || 'Website Enquiry').trim();
      var message = ((form.querySelector('[name="message"]') || {}).value || '').trim();

      var waText =
        '*New Website Enquiry — Harion Research*\n\n' +
        '*Name:* ' + name + '\n' +
        '*Email:* ' + email + '\n' +
        '*Topic:* ' + subject + '\n\n' +
        '*Message:*\n' + message;

      var waUrl = 'https://wa.me/917067000393?text=' + encodeURIComponent(waText);
      window.open(waUrl, '_blank', 'noopener,noreferrer');
    });
  }
})();
