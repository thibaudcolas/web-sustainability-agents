
const fs = require('node:fs');
const path = require('node:path');
const root = process.argv[2];
const {executeScenarioAndGetContainerStats} = require(path.join(root, 'dist/services/container'));
const {computeScenarioResult} = require(path.join(root, 'dist/services/computeScenarioResult'));
(async () => {
  const raw = await executeScenarioAndGetContainerStats({
    scenario: './scenario.js', url: process.argv[3], samples: Number(process.argv[4]),
    useAdblock: false, ignoreHTTPSErrors: false, containers: [], databaseContainers: []
  });
  fs.writeFileSync('raw-counters.json', JSON.stringify(raw));
  const aggregate = computeScenarioResult({allContainersStats: raw.allContainers, milestones: raw.allMilestones, name: 'initial'});
  const samples = raw.allContainers[0].dockerStats.map((item, index) =>
    computeScenarioResult({allContainersStats: [{...raw.allContainers[0], dockerStats: [item]}], milestones: [raw.allMilestones[index]], name: 'initial'}));
  fs.writeFileSync('model-results.json', JSON.stringify({aggregate, samples}));
})().catch(error => {console.error(error); process.exitCode = 1;});
