import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";

const digest = (value) => createHash("sha256").update(value).digest("hex");
const raw = await readFile(".audit-work/site-review.json", "utf8");
const evidence = JSON.parse(raw);
// Strip query strings and fragments, including analytics client identifiers.
const cleanURL = (value) => {
  try {
    const url = new URL(value);
    return url.origin + url.pathname;
  } catch {
    return value;
  }
};
const clean = (value) => {
  if (Array.isArray(value)) return value.map(clean);
  if (value && typeof value === "object")
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, clean(item)]),
    );
  return typeof value === "string" && /^https?:\/\//.test(value)
    ? cleanURL(value)
    : value;
};
const snapshot = (value) => {
  if (!value) return null;
  const { links, resourceTiming, ...retained } = value;
  return retained;
};
const published = clean({
  schemaVersion: "0.1.0",
  rawArtifactSHA256: digest(raw),
  startedAt: evidence.startedAt,
  finishedAt: evidence.finishedAt,
  browser: evidence.browser,
  protocol: evidence.protocol,
  scope: evidence.scope,
  sanitization:
    "URLs omit query strings and fragments. Capture hashes identify original private captures, not the sanitized objects. Resource Timing and full navigation-link inventories omitted. Source excerpts are from the supplied public repositories; no environment files or untracked files are read.",
  captures: evidence.captures,
  reviews: evidence.reviews.map((review) => ({
    ...review,
    initial: snapshot(review.initial),
    afterScroll: snapshot(review.afterScroll),
  })),
  journeys: evidence.journeys,
  followups: JSON.parse(
    await readFile(".audit-work/site-followups.json", "utf8"),
  ),
  consent: JSON.parse(await readFile(".audit-work/site-consent.json", "utf8")),
  fonts: JSON.parse(await readFile(".audit-work/site-fonts.json", "utf8")),
  sources: [],
  content: [],
});
const excerpts = [
  ["guide-image-format", "guide", "apps/custom_media/image_formats.py", 1, 4],
  ["guide-search", "guide", "apps/frontend/static_src/js/main.js", 74, 114],
  [
    "guide-search-template",
    "guide",
    "apps/core/templates/components/search_modal.html",
    1,
    24,
  ],
  ["guide-base", "guide", "apps/core/templates/base.html", 94, 120],
  [
    "wagtail-plausible",
    "wagtail.org",
    "wagtailio/project_styleguide/templates/patterns/base.html",
    30,
    37,
  ],
  [
    "wagtail-gtm",
    "wagtail.org",
    "wagtailio/project_styleguide/templates/patterns/base_page.html",
    65,
    81,
  ],
  [
    "wagtail-video",
    "wagtail.org",
    "wagtailio/project_styleguide/templates/patterns/pages/home/home_page.html",
    50,
    62,
  ],
  [
    "wagtail-fonts",
    "wagtail.org",
    "wagtailio/static/sass/base/_fonts.scss",
    1,
    21,
  ],
  [
    "wagtail-cookie-control",
    "wagtail.org",
    "wagtailio/static/js/components/cookie-message.js",
    30,
    61,
  ],
  [
    "wagtail-highlight-image",
    "wagtail.org",
    "wagtailio/project_styleguide/templates/patterns/components/streamfields/highlight_block/highlight_block.html",
    1,
    10,
  ],
];
for (const [id, repository, path, start, end] of excerpts) {
  const root = `local/${repository}`;
  const revision = execFileSync("git", ["-C", root, "rev-parse", "HEAD"], {
    encoding: "utf8",
  }).trim();
  const file = await readFile(`${root}/${path}`, "utf8");
  const committedFile = execFileSync(
    "git",
    ["-C", root, "show", `HEAD:${path}`],
    { encoding: "utf8" },
  );
  published.sources.push({
    id,
    repository: `https://github.com/wagtail/${repository}`,
    revision,
    path,
    startLine: start,
    endLine: Math.min(end, file.trimEnd().split("\n").length),
    fileSHA256: digest(file),
    matchesCommittedFile: file === committedFile,
    deploymentMatch: "unknown; no deployed revision attestation supplied",
    url: `https://github.com/wagtail/${repository}/blob/${revision}/${path}#L${start}`,
    excerpt: file
      .split("\n")
      .slice(start - 1, end)
      .join("\n"),
  });
}
for (const [id, url, pattern] of [
  [
    "sustainability-average",
    "https://wagtail.org/sustainability/",
    /5173 tons of CO2e\/year for 6431 sites with 12 tCO2e\/year/,
  ],
  [
    "footprint-total",
    "https://wagtail.org/blog/wagtails-2025-carbon-footprint/",
    /5,173 tons of CO2-equivalent emissions per year for 2025, across 6,431 Wagtail sites/,
  ],
]) {
  const response = await fetch(url);
  if (!response.ok)
    throw new Error(`Content capture failed: ${response.status}`);
  const html = await response.text();
  const text = html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");
  const quote = text.match(pattern)?.[0];
  if (!quote)
    throw new Error(`Content changed; review claim extraction for ${id}`);
  published.content.push({
    id,
    url,
    capturedAt: new Date().toISOString(),
    responseSHA256: digest(html),
    quote,
  });
}
published.calculations = [
  {
    id: "average-check",
    evidenceIds: ["sustainability-average", "footprint-total"],
    totalTonnesPerYear: 5173,
    sites: 6431,
    statedTonnesPerSitePerYear: 12,
    arithmeticMeanTonnesPerSitePerYear: 5173 / 6431,
    assumption:
      "Total and count refer to the same population and year; ask the content owner to confirm the intended denominator.",
  },
];
const output = JSON.stringify(published, null, 2) + "\n";
for (const key of [
  process.env.NEURALWATT_API_KEY,
  process.env.TYPESAFE_API_KEY,
  process.env.OPENAI_API_KEY,
].filter(Boolean))
  if (output.includes(key)) throw new Error("Refusing to publish a credential");
await writeFile(
  "docs/initial-implementation/assets/wagtail-review-evidence.json",
  output,
);
console.log("Published sanitized site evidence and pinned source excerpts");
