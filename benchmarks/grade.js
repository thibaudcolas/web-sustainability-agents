import { readFile, mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { isDeepStrictEqual } from "node:util";

export function grade(report, reference) {
  const errors = [];
  if (
    !report ||
    report.schemaVersion !== "0.1.0" ||
    !Array.isArray(report.answers)
  )
    return { reward: 0, errors: ["Invalid report structure"] };
  if (report.answers.some((answer) => !answer || typeof answer !== "object"))
    return { reward: 0, errors: ["Invalid answer structure"] };
  if (report.answers.length !== reference.answers.length)
    errors.push("Wrong number of answers");
  if (
    new Set(report.answers.map((answer) => answer.id)).size !==
    report.answers.length
  )
    errors.push("Duplicate answer IDs");
  for (const expected of reference.answers) {
    const actual = report.answers.find((answer) => answer?.id === expected.id);
    if (!actual || actual.outcome !== expected.outcome)
      errors.push(`${expected.id}: incorrect or missing outcome`);
    if (
      !actual ||
      !Array.isArray(actual.evidenceIds) ||
      !expected.evidenceIds.every((id) => actual.evidenceIds.includes(id)) ||
      !(expected.evidenceGroups ?? []).every((group) =>
        group.some((id) => actual.evidenceIds.includes(id)),
      ) ||
      !actual.evidenceIds.every((id) =>
        reference.allowedEvidenceIds.includes(id),
      )
    )
      errors.push(`${expected.id}: missing or fabricated evidence ID`);
    if (
      typeof actual?.explanation !== "string" ||
      actual.explanation.trim().length < 20
    )
      errors.push(`${expected.id}: explanation missing`);
  }
  if (!report.rating || !isDeepStrictEqual(report.rating, reference.rating))
    errors.push("Rating differs from supplied deterministic result");
  return { reward: errors.length ? 0 : 1, errors };
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(resolve(process.argv[1])).href
) {
  // Reference/JSON errors are infrastructure errors. Only a missing or malformed
  // agent report becomes a zero reward; verifier failure must remain visible.
  const reference = JSON.parse(await readFile("/tests/reference.json", "utf8"));
  let report;
  try {
    const raw = await readFile("/app/output/report.json", "utf8");
    if (raw.length > 100000) throw new SyntaxError("Oversized report");
    report = JSON.parse(raw);
  } catch (error) {
    if (error.code !== "ENOENT" && !(error instanceof SyntaxError)) throw error;
    report = null;
  }
  const result = grade(report, reference);
  await mkdir("/logs/verifier", { recursive: true });
  await writeFile("/logs/verifier/reward.txt", String(result.reward));
  await writeFile(
    "/logs/verifier/diagnostics.json",
    JSON.stringify(result, null, 2),
  );
}
