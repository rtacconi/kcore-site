/**
 * Stripe Payment Links for kcore subscriptions.
 * Paste live Payment Link URLs from Stripe Dashboard when ready.
 * Empty strings fall back to mailto:team@tacconiconsulting.com
 */
window.KCORE_COMMERCE = {
  email: "team@tacconiconsulting.com",
  stripe: {
    standard: "https://buy.stripe.com/aFa7sL2Cn1zG0dZ4BTefC02",
    premium: "https://buy.stripe.com/4gMdR95OzdiobWH7O5efC01",
    enterprise: "https://buy.stripe.com/5kQ9AT7WHa6c3qb3xPefC00",
  },
};

(function () {
  function buyHref(tier, label) {
    var cfg = window.KCORE_COMMERCE || {};
    var stripe = (cfg.stripe && cfg.stripe[tier]) || "";
    if (stripe) return stripe;
    var email = cfg.email || "team@tacconiconsulting.com";
    var subject = encodeURIComponent("kcore " + label + " — buy / subscribe");
    var body = encodeURIComponent(
      "Hello,\n\nI would like to purchase kcore " +
        label +
        ".\n\nNumber of CPU sockets:\nCompany:\nCluster size:\n\nThanks"
    );
    return "mailto:" + email + "?subject=" + subject + "&body=" + body;
  }

  document.querySelectorAll("[data-kcore-buy]").forEach(function (el) {
    var tier = el.getAttribute("data-kcore-buy");
    var label = el.getAttribute("data-kcore-buy-label") || tier;
    el.setAttribute("href", buyHref(tier, label));
    if ((window.KCORE_COMMERCE.stripe || {})[tier]) {
      el.setAttribute("target", "_blank");
      el.setAttribute("rel", "noopener noreferrer");
    }
  });
})();
