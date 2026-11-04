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
