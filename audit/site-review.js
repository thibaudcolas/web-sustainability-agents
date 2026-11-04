import { createHash } from "node:crypto";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "playwright";
import { collectPage, protocol } from "./collect.js";

// A bounded owner-selected sample, not a crawler or a complete WSG test suite.
const targets = [
  ["guide-home", "https://guide.wagtail.org/en/"],
  ["guide-images", "https://guide.wagtail.org/en/how-to-guides/manage-images/"],
  ["wagtail-home", "https://wagtail.org/"],
  ["wagtail-sustainability", "https://wagtail.org/sustainability/"],
];
const output = process.argv[2] ?? ".audit-work/site-review.json";
const browser = await chromium.launch();
const evidence = {
  schemaVersion: "0.1.0",
  startedAt: new Date().toISOString(),
  browser: browser.version(),
  protocol,
  scope:
    "Four pages; desktop cold/warm; fresh desktop/mobile scroll; desktop without JavaScript; two bounded navigation journeys. No form submissions, video playback, authenticated pages, or whole-site crawl.",
  captures: [],
  reviews: [],
  journeys: [],
};

async function snapshot(page) {
  return page.evaluate(() => {
    const visible = (element) => Boolean(element.getClientRects().length);
    return {
      viewport: {
        width: innerWidth,
        height: innerHeight,
        deviceScaleFactor: devicePixelRatio,
      },
      title: document.title,
      lang: document.documentElement.lang,
      h1: [...document.querySelectorAll("h1")].map((el) =>
        el.textContent.trim(),
      ),
      mainTextLength: document.querySelector("main")?.innerText.length ?? 0,
      horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
      documentHeight: document.documentElement.scrollHeight,
      images: [...document.images].map((el) => ({
        src: el.currentSrc || el.src,
        alt: el.getAttribute("alt"),
        loading: el.loading,
        srcset: el.srcset,
        sizes: el.sizes,
        naturalWidth: el.naturalWidth,
        renderedWidth: Math.round(el.getBoundingClientRect().width),
        top: Math.round(el.getBoundingClientRect().top + scrollY),
        complete: el.complete,
      })),
      media: [...document.querySelectorAll("video,audio,iframe")].map((el) => ({
        tag: el.tagName,
        src: el.currentSrc || el.src || el.querySelector("source")?.src || "",
        preload: el.getAttribute("preload"),
        autoplay: el.hasAttribute("autoplay"),
        controls: el.hasAttribute("controls"),
        title: el.getAttribute("title"),
      })),
      scripts: [...document.scripts].filter((el) => el.src).map((el) => el.src),
      links: [...document.querySelectorAll("a[href]")]
        .filter(visible)
        .map((el) => ({
          text: el.innerText.trim().slice(0, 160),
          href: el.href,
        })),
      forms: [...document.forms].map((el) => ({
        action: el.action,
        method: el.method,
      })),
      searchControls: [
        ...document.querySelectorAll(
          'input[type="search"],input[name="query"],[data-search-icon-button]',
        ),
      ].map((el) => ({
        tag: el.tagName,
        visible: visible(el),
        name: el.getAttribute("aria-label"),
      })),
      resourceTiming: performance.getEntriesByType("resource").map((el) => ({
        url: el.name,
        type: el.initiatorType,
        transferSize: el.transferSize,
        encodedBodySize: el.encodedBodySize,
      })),
    };
  });
}

try {
  for (const [id, url] of targets) {
    const captures = await collectPage(browser, url);
    evidence.captures.push(
      ...captures.map((capture) => ({
        id: `${id}-${capture.cache}`,
        ...capture,
      })),
    );
    for (const profile of ["desktop", "mobile", "no-js"]) {
      const context = await browser.newContext({
        viewport:
          profile === "mobile"
            ? { width: 390, height: 844 }
            : protocol.viewport,
        locale: protocol.locale,
        timezoneId: protocol.timezoneId,
        javaScriptEnabled: profile !== "no-js",
        serviceWorkers: "block",
      });
      const page = await context.newPage();
      let phase = "initial";
      const requests = [];
      const errors = [];
      page.on("request", (request) =>
        requests.push({
          url: request.url(),
          type: request.resourceType(),
          phase,
        }),
      );
      page.on("pageerror", (error) => errors.push(error.message));
      const review = {
        id: `${id}-${profile}`,
        url,
        profile,
        startedAt: new Date().toISOString(),
        requests,
        errors,
      };
      try {
        const response = await page.goto(url, {
          waitUntil: "load",
          timeout: 30000,
        });
        review.status = response?.status();
        await page.waitForTimeout(3000);
        review.initial = await snapshot(page);
        phase = "scroll";
        // Scroll incrementally so lazy loading and intersection observers run.
        let steps = 0;
        for (; steps < 40; steps++) {
          const atEnd = await page.evaluate(() => {
            window.scrollBy(0, innerHeight * 0.8);
            return (
              scrollY + innerHeight >= document.documentElement.scrollHeight
            );
          });
          await page.waitForTimeout(150);
          if (atEnd) break;
        }
        await page.waitForTimeout(1500);
        review.scrollLimitReached = steps === 40;
        review.afterScroll = await snapshot(page);
      } catch (error) {
        review.error = error.message;
      }
      evidence.reviews.push(review);
      await context.close();
    }
    console.log(`Collected ${id}`);
  }

  for (const journey of [
    "guide-search-images",
    "wagtail-find-sustainability",
  ]) {
    const context = await browser.newContext({
      viewport: protocol.viewport,
      locale: protocol.locale,
      serviceWorkers: "block",
    });
    const page = await context.newPage();
    const result = {
      id: journey,
      startedAt: new Date().toISOString(),
      steps: [],
      requests: [],
    };
    page.on("request", (request) =>
      result.requests.push({
        url: request.url(),
        type: request.resourceType(),
      }),
    );
    try {
      if (journey === "guide-search-images") {
        await page.goto(targets[0][1], { waitUntil: "load" });
        await page.locator("[data-search-icon-button]").click();
        result.steps.push("Open search using the visible search control");
        const input = page.locator("[data-search-input]");
        await input.pressSequentially("images", { delay: 80 });
        await page.waitForTimeout(1200);
        result.searchResults = await page
          .locator("#search-modal a")
          .evaluateAll((links) =>
            links.map((el) => ({ text: el.innerText, href: el.href })),
          );
        await page
          .locator('#search-modal a[href*="/manage-images/"]')
          .first()
          .click();
        result.steps.push("Type images and follow the Manage images result");
        await page.waitForURL(targets[1][1]);
      } else {
        await page.goto(targets[2][1], { waitUntil: "load" });
        const link = page.locator('a[href="/sustainability/"]').last();
        await link.scrollIntoViewIfNeeded();
        await link.click();
        result.steps.push(
          "Follow the sustainability link in the homepage footer",
        );
        await page.waitForURL(targets[3][1]);
      }
      result.finalUrl = page.url();
      result.h1 = await page.locator("h1").allTextContents();
      result.completed = true;
    } catch (error) {
      result.completed = false;
      result.error = error.message;
      result.finalUrl = page.url();
    }
    evidence.journeys.push(result);
    await context.close();
  }
} finally {
  await browser.close();
  evidence.finishedAt = new Date().toISOString();
  evidence.sha256 = createHash("sha256")
    .update(JSON.stringify(evidence))
    .digest("hex");
  await mkdir(resolve(output, ".."), { recursive: true });
  await writeFile(output, JSON.stringify(evidence, null, 2) + "\n", {
    mode: 0o600,
  });
}
console.log(`Saved bounded review evidence to ${output}`);
