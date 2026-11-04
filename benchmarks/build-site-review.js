import { readFile, writeFile, mkdir, cp, copyFile } from "node:fs/promises";
import { join } from "node:path";

// A public development set, with provisional expectations for owner review.
// This is frozen-evidence review, not autonomous browsing or repository search.
const evidence = JSON.parse(
  await readFile(
    "docs/initial-implementation/assets/wagtail-review-evidence.json",
    "utf8",
  ),
);
const root = process.argv[2] ?? ".audit-work/site-tasks";
const writeJSON = (path, value) =>
  writeFile(path, JSON.stringify(value, null, 2) + "\n");
const questions = [
  [
    "analytics-deferral",
    "Do the sampled Wagtail pages defer Google analytics scripts until a visitor chooses to activate them?",
    "fail",
    ["scope"],
  ],
  [
    "analytics-necessity",
    "Does the evidence establish that every Google analytics integration is unnecessary for the owner's needs?",
    "inconclusive",
    ["scope"],
  ],
  [
    "guide-media-deferral",
    "Are the guide image-management screenshots deferred until scrolling in the mobile observation?",
    "fail",
    ["guide-images-mobile"],
  ],
  [
    "guide-image-format",
    "Are the four guide screenshots delivered as PNG image bodies, as their filename extensions suggest?",
    "fail",
    ["guide-images-cold"],
  ],
  [
    "cache-reuse",
    "Does the sampled guide image page reuse its public static JavaScript on the warm navigation?",
    "pass",
    ["guide-images-warm"],
  ],
  [
    "video-deferral",
    "Does the homepage video avoid media requests during the desktop initial load and scroll observation, before playback? This does not ask whether playback works.",
    "pass",
    ["wagtail-home-desktop"],
  ],
  [
    "claim-arithmetic",
    "Is the stated 12 tonnes/site/year the arithmetic mean of the published 5173 tonnes/year and 6431 sites, assuming the same population?",
    "fail",
    ["average-check"],
  ],
  [
    "source-match",
    "Has a local checkout been established as exactly the deployed revision? If source is available, identify useful candidate fix locations in the explanation without asserting a deployment match.",
    "inconclusive",
    ["source"],
  ],
  [
    "organizational-wsg",
    "Does this sample establish that unobserved organizational processes meet all organizational WSG requirements?",
    "inconclusive",
    ["scope"],
  ],
];
for (const mode of ["public", "source"]) {
  const directory = join(root, `wagtail-${mode}`);
  await mkdir(join(directory, "environment"), { recursive: true });
  await mkdir(join(directory, "tests"), { recursive: true });
  await mkdir(join(directory, "solution"), { recursive: true });
  const facts = [
    {
      id: "scope",
      kind: "collector",
      value: {
        scope: evidence.scope,
        protocol: evidence.protocol,
        observationLimit:
          "No organization records, traffic denominators, or deployment attestation; no video playback test.",
      },
    },
    ...evidence.captures.map(({ id, ...value }) => ({
      id,
      kind: "collector",
      value,
    })),
    ...evidence.reviews.map(({ id, ...value }) => ({
      id,
      kind: "collector",
      value,
    })),
    ...evidence.content.map(({ id, ...value }) => ({
      id,
      kind: "public-content",
      value,
    })),
    ...evidence.calculations.map(({ id, ...value }) => ({
      id,
      kind: "calculation",
      value,
    })),
    {
      id: "source",
      kind: "source",
      value: mode === "source" ? evidence.sources : null,
    },
  ];
  const rating = Object.fromEntries(
    evidence.captures
      .filter((c) => c.cache === "cold")
      .map((c) => [c.id, c.rating]),
  );
  const input = {
    schemaVersion: "0.1.0",
    mode,
    facts,
    questions: questions.map(([id, text]) => ({ id, text })),
    rating,
  };
  const reference = {
    answers: questions.map(([id, , outcome, evidenceIds]) => ({
      id,
      outcome,
      evidenceIds,
    })),
    allowedEvidenceIds: facts.map((fact) => fact.id),
    rating,
  };
  reference.answers[0].evidenceGroups = [
    ["wagtail-home-cold", "wagtail-home-desktop", "wagtail-home-mobile"],
    [
      "wagtail-sustainability-cold",
      "wagtail-sustainability-desktop",
      "wagtail-sustainability-mobile",
    ],
  ];
  await writeJSON(join(directory, "environment/input.json"), input);
  await writeJSON(join(directory, "tests/reference.json"), reference);
  await writeJSON(join(directory, "solution/report.json"), {
    schemaVersion: "0.1.0",
    answers: reference.answers.map((answer) => ({
      ...answer,
      evidenceIds: [
        ...answer.evidenceIds,
        ...(answer.evidenceGroups ?? []).map((group) => group[0]),
      ],
      explanation:
        "Reference artifact for checking the deterministic grading contract only.",
    })),
    rating,
  });
  await writeFile(
    join(directory, "solution/solve.sh"),
    "#!/bin/sh\nset -eu\nmkdir -p /app/output\ncp /solution/report.json /app/output/report.json\n",
  );
  for (const path of [
    "environment/Dockerfile",
    "tests/Dockerfile",
    "tests/test.sh",
    "instruction.md",
  ])
    await copyFile(
      join(".audit-work/tasks/clean-public", path),
      join(directory, path),
    );
  await copyFile("benchmarks/grade.js", join(directory, "tests/grade.mjs"));
  await cp(
    ".agents/skills/sustainability-evidence-review",
    join(directory, "environment/skills/sustainability-evidence-review"),
    { recursive: true },
  );
  const task = await readFile(
    ".audit-work/tasks/clean-public/task.toml",
    "utf8",
  );
  await writeFile(
    join(directory, "task.toml"),
    task.replace("timeout_sec = 180", "timeout_sec = 300"),
  );
}
console.log(`Built public/source development review tasks in ${root}`);
