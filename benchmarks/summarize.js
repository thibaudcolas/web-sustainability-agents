import { createHash } from "node:crypto";
import { readFile, writeFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { grade } from "./grade.js";

const readJSON = async (path) => JSON.parse(await readFile(path, "utf8"));
const digest = (value) => createHash("sha256").update(value).digest("hex");
const restoreFlag = process.argv.includes("--restore-codex-auth-flag");
const jobs = process.argv.slice(2).filter((arg) => !arg.startsWith("--"));
if (!jobs.length)
  throw new Error("Usage: node benchmarks/summarize.js JOB_DIRECTORY [...]");
const campaigns = [];
for (const directory of jobs) {
  const result = await readJSON(join(directory, "result.json"));
  if (!result.finished_at) throw new Error(`Campaign unfinished: ${directory}`);
  const trials = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const trialDirectory = join(directory, entry.name);
    let trial;
    let metadataRepair = null;
    try {
      const raw = await readFile(join(trialDirectory, "result.json"), "utf8");
      try {
        trial = JSON.parse(raw);
      } catch (error) {
        if (!restoreFlag || !(error instanceof SyntaxError)) throw error;
        // Historical Harbor 0.23.0 trials registered our literal auth toggle
        // "1" as a secret, replacing digit 1 even inside serialized numbers.
        // This opt-in repairs that known nonsecret value, never API credentials.
        const repaired = JSON.parse(raw.replaceAll("[REDACTED]", "1"));
        const env = repaired.config?.agent?.env;
        if (
          repaired.config?.agent?.name !== "codex" ||
          Object.keys(env ?? {}).join() !== "CODEX_FORCE_AUTH_JSON" ||
          env.CODEX_FORCE_AUTH_JSON !== "****"
        )
          throw new Error(
            "Historical repair only supports the known Codex auth-toggle case",
          );
        trial = repaired;
        metadataRepair =
          "Restored known nonsecret digit 1 redacted by Harbor 0.23.0 in published copies of metadata, reports, and diagnostics. Original files preserved; restored artifacts regraded against original references.";
      }
    } catch (error) {
      if (error.code === "ENOENT") continue;
      throw error;
    }
    let report = null;
    let diagnostics = null;
    for (const [filename, setter] of [
      [
        "artifacts/app/output/report.json",
        (value) => {
          report = value;
        },
      ],
      [
        "verifier/diagnostics.json",
        (value) => {
          diagnostics = value;
        },
      ],
    ]) {
      try {
        const original = await readFile(join(trialDirectory, filename), "utf8");
        const raw = metadataRepair
          ? original.replaceAll("[REDACTED]", "1")
          : original;
        try {
          setter(JSON.parse(raw));
        } catch (error) {
          if (
            !metadataRepair ||
            filename !== "verifier/diagnostics.json" ||
            !(error instanceof SyntaxError)
          )
            throw error;
          setter(JSON.parse(raw.replaceAll("[REDACTED]", "1")));
        }
      } catch (error) {
        if (error.code !== "ENOENT") throw error;
      }
    }
    const input = await readFile(
      join(trial.config.task.path, "environment/input.json"),
      "utf8",
    );
    const instruction = await readFile(
      join(trial.config.task.path, "instruction.md"),
      "utf8",
    );
    const reference = await readJSON(
      join(trial.config.task.path, "tests/reference.json"),
    );
    const artifactRegrade = grade(report, reference);
    const recordedReward = trial.verifier_result?.rewards?.reward ?? null;
    if (recordedReward !== null && artifactRegrade.reward !== recordedReward)
      throw new Error(`Artifact regrade disagrees with Harbor: ${entry.name}`);
    trials.push({
      task: trial.task_name,
      inputSHA256: digest(input),
      instructionSHA256: digest(instruction),
      input: JSON.parse(input),
      requestedModel: trial.config.agent.model_name,
      agent: trial.config.agent.name,
      version: trial.config.agent.kwargs.version ?? null,
      verifierMode: trial.verifier_environment_mode,
      metadataRepair,
      reward: trial.verifier_result?.rewards?.reward ?? null,
      exception: trial.exception_info?.exception_type ?? null,
      startedAt: trial.started_at,
      finishedAt: trial.finished_at,
      usage: trial.agent_result
        ? {
            inputTokens: trial.agent_result.n_input_tokens,
            cachedTokens: trial.agent_result.n_cache_tokens,
            outputTokens: trial.agent_result.n_output_tokens,
            harnessReportedCostUSD: trial.agent_result.cost_usd,
            energyJoules: null,
            energyStatus: "not captured by this harness integration",
          }
        : null,
      diagnostics,
      artifactRegrade,
      report,
    });
  }
  campaigns.push({
    name: directory.split("/").at(-1),
    harborVersion: "0.23.0",
    startedAt: result.started_at,
    finishedAt: result.finished_at,
    completedTrials: result.stats.n_completed_trials,
    erroredTrials: result.stats.n_errored_trials,
    trials: trials.sort((a, b) => a.task.localeCompare(b.task)),
  });
}
const output =
  JSON.stringify(
    {
      schemaVersion: "0.1.0",
      status: "development observations; not an accuracy estimate",
      costStatus:
        "Harness-reported estimates, not reconciled provider invoices",
      campaigns,
    },
    null,
    2,
  ) + "\n";
for (const key of [
  process.env.NEURALWATT_API_KEY,
  process.env.TYPESAFE_API_KEY,
  process.env.OPENAI_API_KEY,
].filter(Boolean)) {
  if (output.includes(key))
    throw new Error("Refusing to publish a credential in the summary");
}
await writeFile(
  "docs/initial-implementation/assets/first-slice-results.json",
  output,
);
console.log(`Published allowlisted results for ${campaigns.length} campaigns`);
