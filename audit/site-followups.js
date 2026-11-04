import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";

// Bounded diagnostic follow-ups; these do not produce carbon ratings.
await mkdir(".audit-work", { recursive: true });
const browser = await chromium.launch();
try {
  const results = [];
  for (const [id, url, width, javaScriptEnabled] of [
    ["wagtail-mobile", "https://wagtail.org/", 390, true],
    ["wagtail-desktop", "https://wagtail.org/", 1280, true],
    ["guide-no-js", "https://guide.wagtail.org/en/", 1280, false],
  ]) {
    const context = await browser.newContext({
      viewport: { width, height: 844 },
      javaScriptEnabled,
    });
    const page = await context.newPage();
    await page.goto(url, { waitUntil: "load" });
    await page.waitForTimeout(1500);
    const observation = await page.evaluate(() => ({
      width: innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
      bodyOverflow: getComputedStyle(document.body).overflowX,
      htmlOverflow: getComputedStyle(document.documentElement).overflowX,
      overflowElements: [...document.querySelectorAll("body *")]
        .filter((el) => {
          const rect = el.getBoundingClientRect();
          return (
            rect.width > 0 && (rect.right > innerWidth + 5 || rect.left < -5)
          );
        })
        .slice(0, 20)
        .map((el) => ({
          tag: el.tagName,
          class: el.className,
          ariaHidden: el.getAttribute("aria-hidden"),
          position: getComputedStyle(el).position,
          visibility: getComputedStyle(el).visibility,
          rect: {
            left: el.getBoundingClientRect().left,
            right: el.getBoundingClientRect().right,
          },
        })),
    }));
    await page.evaluate(() => window.scrollTo(200, 0));
    observation.scrollX = await page.evaluate(() => scrollX);
    if (!javaScriptEnabled) {
      await page.locator("[data-search-icon-button]").click();
      observation.searchVisibleAfterClick = await page
        .locator("[data-search-input]")
        .isVisible();
      observation.manageImagesNavigation = await page
        .locator('a[href="/en/how-to-guides/manage-images/"]')
        .first()
        .isVisible();
    }
    await page.screenshot({ path: `.audit-work/${id}.png` });
    results.push({
      id,
      url,
      startedAt: new Date().toISOString(),
      ...observation,
    });
    await context.close();
  }
  await writeFile(
    ".audit-work/site-followups.json",
    JSON.stringify(results, null, 2) + "\n",
  );

  const context = await browser.newContext();
  const page = await context.newPage();
  let phase = "before-choice";
  const requests = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (/googletagmanager|google-analytics|plausible/.test(url.host))
      requests.push({
        phase,
        url: url.origin + url.pathname,
        type: request.resourceType(),
      });
  });
  await page.goto("https://wagtail.org/", { waitUntil: "load" });
  await page.waitForTimeout(3000);
  const fonts = await page.evaluate(() =>
    [...document.styleSheets].flatMap((sheet) => {
      try {
        return [...sheet.cssRules]
          .filter((rule) => rule.type === CSSRule.FONT_FACE_RULE)
          .map((rule) => ({
            family: rule.style.fontFamily,
            weight: rule.style.fontWeight,
            display: rule.style.fontDisplay,
            src: rule.style.src,
          }));
      } catch {
        return [];
      }
    }),
  );
  await writeFile(
    ".audit-work/site-fonts.json",
    JSON.stringify(
      {
        id: "wagtail-font-css",
        capturedAt: new Date().toISOString(),
        url: page.url(),
        fonts,
      },
      null,
      2,
    ) + "\n",
  );
  const optOutVisibleBefore = await page
    .locator("[data-cookie-opt-out]")
    .isVisible();
  phase = "opt-out";
  await page.locator("[data-cookie-opt-out]").click();
  await page.waitForTimeout(1000);
  phase = "reload-after-opt-out";
  await page.reload({ waitUntil: "load" });
  await page.waitForTimeout(3000);
  await writeFile(
    ".audit-work/site-consent.json",
    JSON.stringify(
      {
        id: "wagtail-opt-out",
        capturedAt: new Date().toISOString(),
        url: page.url(),
        optOutVisibleBefore,
        optOutVisibleAfterReload: await page
          .locator("[data-cookie-opt-out]")
          .isVisible(),
        requests,
      },
      null,
      2,
    ) + "\n",
  );
  await context.close();
} finally {
  await browser.close();
}
console.log("Saved overflow, JavaScript fallback, and opt-out observations");
