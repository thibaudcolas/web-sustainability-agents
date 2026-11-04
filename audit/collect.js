import { createHash } from "node:crypto";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright";
import { rateCapture } from "./rating.js";

export const protocol = {
  version: "0.1.0",
  viewport: { width: 1280, height: 800 },
  locale: "en-GB",
  timezoneId: "Europe/London",
  observationMs: 3000,
  byteDefinition:
    "Sum of CDP Network.loadingFinished.encodedDataLength plus redirect response encodedDataLength; received network bytes, including protocol-reported overhead",
  warmDefinition:
    "Second navigation in the same browser context, with no cache-disabling routing",
  scope:
    "Main page CDP session; service workers blocked; no scrolling or consent interaction",
};

export async function collectPage(
  browser,
  url,
  { observationMs = protocol.observationMs } = {},
) {
  const context = await browser.newContext({
    viewport: protocol.viewport,
    locale: protocol.locale,
    timezoneId: protocol.timezoneId,
    serviceWorkers: "block",
  });
  try {
    const page = await context.newPage();
    const cdp = await context.newCDPSession(page);
    await cdp.send("Network.enable");
    const captures = [];
    for (const cache of ["cold", "warm"]) {
      const requests = new Map();
      const redirected = [];
      const handlers = {
        "Network.requestWillBeSent": (event) => {
          if (event.redirectResponse) {
            const previous = requests.get(event.requestId);
            if (previous)
              redirected.push({
                ...previous,
                status: event.redirectResponse.status,
                receivedBytes: event.redirectResponse.encodedDataLength,
                finished: true,
              });
          }
          requests.set(event.requestId, {
            id: event.requestId,
            url: event.request.url,
            type: event.type,
            finished: false,
            receivedBytes: null,
            fromCache: false,
          });
        },
        "Network.requestServedFromCache": (event) => {
          const entry = requests.get(event.requestId);
          if (entry) entry.fromCache = true;
        },
        "Network.responseReceived": (event) => {
          const entry = requests.get(event.requestId);
          if (entry)
            Object.assign(entry, {
              status: event.response.status,
              mimeType: event.response.mimeType,
              fromCache:
                entry.fromCache || Boolean(event.response.fromDiskCache),
              fromServiceWorker: Boolean(event.response.fromServiceWorker),
              headers: Object.fromEntries(
                Object.entries(event.response.headers).filter(([name]) =>
                  /^(cache-control|content-encoding|content-length|content-type|etag|vary)$/i.test(
                    name,
                  ),
                ),
              ),
            });
        },
        "Network.loadingFinished": (event) => {
          const entry = requests.get(event.requestId);
          if (entry)
            Object.assign(entry, {
              finished: true,
              receivedBytes: event.encodedDataLength,
            });
        },
        "Network.loadingFailed": (event) => {
          const entry = requests.get(event.requestId);
          if (entry)
            Object.assign(entry, { finished: true, error: event.errorText });
        },
      };
      for (const [name, handler] of Object.entries(handlers))
        cdp.on(name, handler);
      let navigationError = null;
      const startedAt = new Date().toISOString();
      try {
        await page.goto(url, { waitUntil: "load", timeout: 30000 });
      } catch (error) {
        navigationError = error.message;
      }
      await page.waitForTimeout(observationMs);
      const resources = [...redirected, ...requests.values()];
      const status = resources.findLast(
        (entry) => entry.type === "Document",
      )?.status;
      const frames = page.frames().map((frame) => frame.url());
      const limitations = [];
      if (frames.length > 1)
        limitations.push(
          "Child-frame traffic is not fully covered by this collector",
        );
      if (resources.some((entry) => entry.fromServiceWorker))
        limitations.push("Unexpected service-worker response");
      if (
        resources.some(
          (entry) =>
            entry.error || !entry.finished || entry.receivedBytes === null,
        )
      )
        limitations.push("Failed or unfinished resource requests");
      if (resources.some((entry) => entry.status >= 400))
        limitations.push("HTTP resource error");
      if (!status || status >= 400)
        limitations.push("Main document did not successfully load");
      if (navigationError) limitations.push("Navigation error");
      const capture = {
        url,
        finalUrl: page.url(),
        startedAt,
        cache,
        protocol: { ...protocol, observationMs },
        browser: browser.version(),
        complete: limitations.length === 0,
        limitations,
        navigationError,
        frames,
        title: await page.title(),
        receivedBytes: resources.reduce(
          (sum, entry) => sum + (entry.receivedBytes ?? 0),
          0,
        ),
        resources,
      };
      capture.rating = rateCapture(capture);
      capture.sha256 = createHash("sha256")
        .update(JSON.stringify(capture))
        .digest("hex");
      captures.push(capture);
      for (const [name, handler] of Object.entries(handlers))
        cdp.off(name, handler);
    }
    return captures;
  } finally {
    await context.close();
  }
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href
) {
  const [output, ...urls] = process.argv.slice(2);
  if (!output || !urls.length)
    throw new Error("Usage: node audit/collect.js OUTPUT.json URL [URL...]");
  const browser = await chromium.launch();
  try {
    const captures = [];
    for (const url of urls) captures.push(...(await collectPage(browser, url)));
    await mkdir(resolve(output, ".."), { recursive: true });
    await writeFile(output, JSON.stringify(captures, null, 2) + "\n");
    console.log(`Saved ${captures.length} captures to ${output}`);
  } finally {
    await browser.close();
  }
}
