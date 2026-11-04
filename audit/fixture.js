import http from "node:http";

// Original project-owned fixtures, inspired by STAR's cache and media tests.
// The broken variant changes sustainability behavior, not accessibility.
export async function startFixture({ broken = false } = {}) {
  const hits = [];
  const server = http.createServer((request, response) => {
    const path = new URL(request.url, "http://fixture.test").pathname;
    hits.push(path);
    response.setHeader("Cache-Control", "no-store");
    if (path === "/favicon.ico") {
      response.writeHead(204);
      response.end();
    } else if (path === "/asset.js") {
      response.setHeader("Content-Type", "text/javascript");
      response.setHeader(
        "Cache-Control",
        broken ? "no-store" : "public, max-age=31536000, immutable",
      );
      response.end(`/* ${"A".repeat(16000)} */`);
    } else if (path === "/private") {
      response.setHeader("Content-Type", "application/json");
      response.end(JSON.stringify({ message: "Private account information" }));
    } else if (path === "/illustration.svg") {
      response.setHeader("Content-Type", "image/svg+xml");
      response.end(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100"><rect width="200" height="100" fill="blue"/></svg>',
      );
    } else if (path === "/") {
      response.setHeader("Content-Type", "text/html; charset=utf-8");
      response.end(`<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Illustration - Example guide</title><script src="/asset.js" defer></script></head>
<body><a href="#main">Skip to content</a><main id="main" tabindex="-1">
<h1>Example guide</h1><p>Read the guide, then choose whether to load its optional illustration.</p>
<button type="button" id="show" aria-controls="illustration" aria-expanded="${broken}">Show illustration</button>
<div id="illustration"${broken ? "" : " hidden"}><img width="200" height="100" alt="A solid blue rectangle" ${broken ? 'src="/illustration.svg"' : 'data-src="/illustration.svg"'}></div>
<p role="status" id="status"></p></main>
<script>
fetch('/private').then(response => response.json());
document.getElementById('show').addEventListener('click', () => {
  const container = document.getElementById('illustration');
  const image = container.querySelector('img');
  if (!image.hasAttribute('src')) image.src = image.dataset.src;
  container.hidden = false;
  document.getElementById('show').setAttribute('aria-expanded', 'true');
  document.getElementById('status').textContent = 'Illustration shown.';
});
</script></body></html>`);
    } else {
      response.writeHead(404);
      response.end("Not found");
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  return {
    url: `http://127.0.0.1:${server.address().port}/`,
    hits,
    close: () =>
      new Promise((resolve, reject) =>
        server.close((error) => (error ? reject(error) : resolve())),
      ),
  };
}
