/**
 * Cloudflare Pages only: runs before static assets.
 *
 * GitHub Pages does not execute this file. To pass agent audits that require
 * Link headers, correct api-catalog Content-Type, Accept: text/markdown on /,
 * deploy this repository to Cloudflare Pages (or put Cloudflare in front with
 * equivalent transforms). See DEPLOYMENT.md.
 */

const LINK_DISCOVERY =
  '</.well-known/api-catalog>; rel="api-catalog", </docs.html>; rel="service-doc"';

const API_CATALOG_TYPE =
  'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"';

const HTTP_SIG_DIR_TYPE = "application/http-message-signatures-directory+json";

function qValue(accept, mediaType) {
  const parts = accept.split(",");
  const needle = mediaType.toLowerCase();
  for (const part of parts) {
    const [rawType, ...params] = part.trim().split(";");
    if (rawType.trim().toLowerCase() !== needle) continue;
    for (const p of params) {
      const [k, v] = p.split("=").map((s) => s.trim());
      if (k.toLowerCase() === "q" && v) return parseFloat(v);
    }
    return 1;
  }
  return 0;
}

function prefersMarkdown(accept) {
  const a = accept.toLowerCase();
  if (!a.includes("text/markdown")) return false;
  if (!a.includes("text/html")) return true;
  return qValue(accept, "text/markdown") > qValue(accept, "text/html");
}

function withHeaders(response, mutator) {
  const h = new Headers(response.headers);
  mutator(h);
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: h,
  });
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const accept = context.request.headers.get("Accept") || "";
  const isGet = context.request.method === "GET";
  const isHome =
    url.pathname === "/" || url.pathname === "/index.html";

  if (isGet && isHome && prefersMarkdown(accept)) {
    let md = "";
    if (context.env && context.env.ASSETS) {
      const assetReq = new Request(new URL("/index.md", url.origin), {
        method: "GET",
      });
      const ar = await context.env.ASSETS.fetch(assetReq);
      if (ar.ok) md = await ar.text();
    }
    if (!md.trim()) {
      md =
        "# kcore hypervisor\n\nMarkdown source missing; see https://kcorehypervisor.com/\n";
    }
    const headers = new Headers({
      "Content-Type": "text/markdown; charset=utf-8",
      "Cache-Control": "public, max-age=300",
      Link: LINK_DISCOVERY,
      Vary: "Accept",
      "Content-Signal": "ai-train=no, search=yes, ai-input=yes",
    });
    const approx = Math.max(1, Math.ceil(md.length / 4));
    headers.set("x-markdown-tokens", String(approx));
    return new Response(md, { status: 200, headers });
  }

  const response = await context.next();

  if (!isGet) return response;

  if (url.pathname === "/.well-known/api-catalog" && response.status === 200) {
    return withHeaders(response, (h) => {
      h.set("Content-Type", API_CATALOG_TYPE);
      if (!h.has("Access-Control-Allow-Origin")) {
        h.set("Access-Control-Allow-Origin", "*");
      }
    });
  }

  if (
    url.pathname === "/.well-known/http-message-signatures-directory" &&
    response.status === 200
  ) {
    return withHeaders(response, (h) => {
      h.set("Content-Type", HTTP_SIG_DIR_TYPE);
      h.set("Cache-Control", "public, max-age=86400");
    });
  }

  if (
    isHome &&
    response.status === 200 &&
    (response.headers.get("Content-Type") || "").includes("text/html")
  ) {
    return withHeaders(response, (h) => {
      const cur = h.get("Link");
      h.set("Link", cur ? `${cur}, ${LINK_DISCOVERY}` : LINK_DISCOVERY);
    });
  }

  return response;
}
