import assert from "node:assert/strict";
import test from "node:test";
import { chromium } from "playwright";
import { co2 } from "@tgwf/co2";
import { collectPage } from "../audit/collect.js";
import { startFixture } from "../audit/fixture.js";
import { rateCapture } from "../audit/rating.js";

test("cold/warm captures distinguish reusable assets and private no-store data", async () => {
  const browser = await chromium.launch();
  try {
    for (const broken of [false, true]) {
      const fixture = await startFixture({ broken });
      try {
        const [cold, warm] = await collectPage(browser, fixture.url, {
          observationMs: 500,
        });
        assert.equal(cold.complete, true, JSON.stringify(cold.limitations));
        assert.equal(warm.complete, true, JSON.stringify(warm.limitations));
        const asset = warm.resources.find((r) => r.url.endsWith("/asset.js"));
        assert.equal(asset.fromCache, !broken);
        assert.equal(
          fixture.hits.filter((p) => p === "/asset.js").length,
          broken ? 2 : 1,
        );
        assert.equal(fixture.hits.filter((p) => p === "/private").length, 2);
        assert.equal(
          cold.resources.some((r) => r.url.endsWith("/illustration.svg")),
          broken,
        );
        assert.equal(cold.rating.status, "calculated");
        assert.equal(warm.rating.status, "not_calculated");
        if (!broken) assert.ok(warm.receivedBytes < cold.receivedBytes / 2);
      } finally {
        await fixture.close();
      }
    }
  } finally {
    await browser.close();
  }
});

test("keyboard intent loads deferred illustration and announces it", async () => {
  const fixture = await startFixture();
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto(fixture.url);
    assert.equal(fixture.hits.includes("/illustration.svg"), false);
    await page.keyboard.press("Tab");
    assert.equal(await page.locator(":focus").getAttribute("href"), "#main");
    await page.keyboard.press("Enter");
    assert.equal(await page.locator(":focus").getAttribute("id"), "main");
    await page.keyboard.press("Tab");
    assert.equal(await page.locator(":focus").getAttribute("id"), "show");
    await page.keyboard.press("Enter");
    await page.waitForFunction(
      () => document.querySelector("img").naturalWidth > 0,
    );
    assert.ok(fixture.hits.includes("/illustration.svg"));
    assert.equal(
      await page.getByRole("button").getAttribute("aria-expanded"),
      "true",
    );
    assert.equal(
      await page.getByRole("status").textContent(),
      "Illustration shown.",
    );
  } finally {
    await browser.close();
    await fixture.close();
  }
});

test("unavailable, warm, zero and invalid measurements do not receive ratings", () => {
  for (const overrides of [
    { complete: false },
    { cache: "warm" },
    { receivedBytes: 0 },
    { receivedBytes: -1 },
    { receivedBytes: NaN },
    { receivedBytes: Infinity },
  ]) {
    assert.equal(
      rateCapture({
        complete: true,
        cache: "cold",
        receivedBytes: 5000,
        ...overrides,
      }).status,
      "not_calculated",
    );
  }
});

test("HTTP error pages cannot masquerade as low-carbon successful loads", async () => {
  const fixture = await startFixture();
  const browser = await chromium.launch();
  try {
    const captures = await collectPage(browser, `${fixture.url}missing`, {
      observationMs: 100,
    });
    for (const capture of captures) {
      assert.equal(capture.complete, false);
      assert.equal(capture.rating.status, "not_calculated");
    }
  } finally {
    await browser.close();
    await fixture.close();
  }
});

test("pinned CO2.js uses unrounded inclusive SWDM v4 boundaries", () => {
  const model = new co2({ model: "swd", version: 4, rating: true });
  // Exercise the installed library's rating helper, not a copied threshold implementation.
  for (const [grams, rating] of [
    [0.04, "A+"],
    [0.0401, "A"],
    [0.079, "A"],
    [0.0791, "B"],
    [0.145, "B"],
    [0.209, "C"],
    [0.278, "D"],
    [0.359, "E"],
    [0.3591, "F"],
  ]) {
    assert.equal(model.model.ratingScale(grams), rating);
  }
});
