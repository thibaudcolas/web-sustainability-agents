import assert from "node:assert/strict";
import test from "node:test";
import { grade } from "../benchmarks/grade.js";

const reference = {
  answers: [{ id: "cache", outcome: "inconclusive", evidenceIds: ["capture"] }],
  rating: { status: "not_calculated", band: null },
  allowedEvidenceIds: ["capture"],
};
const valid = () => ({
  schemaVersion: "0.1.0",
  answers: [
    {
      ...reference.answers[0],
      explanation:
        "The capture is incomplete, so cache effectiveness remains unknown.",
    },
  ],
  rating: { band: null, status: "not_calculated" },
});

test("reference passes and JSON key order is immaterial", () => {
  assert.equal(grade(valid(), reference).reward, 1);
});

test("nested multi-page rating traces are preserved regardless of key order", () => {
  const report = valid();
  const expected = structuredClone(reference);
  expected.rating = {
    guide: { status: "calculated", trace: { grams: 0.034, band: "A+" } },
    wagtail: { status: "not_calculated", reason: "Incomplete" },
  };
  report.rating = {
    wagtail: { reason: "Incomplete", status: "not_calculated" },
    guide: { trace: { band: "A+", grams: 0.034 }, status: "calculated" },
  };
  assert.equal(grade(report, expected).reward, 1);
  report.rating.guide.trace.grams = 0.03;
  assert.equal(grade(report, expected).reward, 0);
  report.rating = structuredClone(expected.rating);
  delete report.rating.wagtail.reason;
  assert.equal(grade(report, expected).reward, 0);
  report.rating = structuredClone(expected.rating);
  report.rating.guide.unverifiedClaim = "Whole site passes";
  assert.equal(grade(report, expected).reward, 0);
});

test("equivalent evidence is accepted but every required group needs support", () => {
  const expected = structuredClone(reference);
  expected.allowedEvidenceIds.push(
    "home-cold",
    "home-scroll",
    "article-cold",
    "article-scroll",
  );
  expected.answers[0].evidenceGroups = [
    ["home-cold", "home-scroll"],
    ["article-cold", "article-scroll"],
  ];
  const report = valid();
  report.answers[0].evidenceIds = ["capture", "home-scroll", "article-cold"];
  assert.equal(grade(report, expected).reward, 1);
  report.answers[0].evidenceIds = ["capture", "home-cold"];
  assert.equal(grade(report, expected).reward, 0);
  report.answers[0].evidenceIds = ["capture", "home-scroll", "invented"];
  assert.equal(grade(report, expected).reward, 0);
});

test("missing, malformed, duplicate, fabricated and overconfident results fail", () => {
  for (const invalid of [
    null,
    {},
    { ...valid(), answers: [null] },
    { ...valid(), answers: [] },
    { ...valid(), answers: [...valid().answers, ...valid().answers] },
  ])
    assert.equal(grade(invalid, reference).reward, 0);
  for (const patch of [
    { outcome: "pass" },
    { evidenceIds: ["invented"] },
    { evidenceIds: ["capture", "invented"] },
    { explanation: "" },
  ]) {
    const report = valid();
    Object.assign(report.answers[0], patch);
    assert.equal(grade(report, reference).reward, 0);
  }
  const report = valid();
  report.rating = { status: "calculated", band: "A+" };
  assert.equal(grade(report, reference).reward, 0);
});
