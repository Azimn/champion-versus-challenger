"use strict";

const fs = require("fs");
const path = require("path");

function fail(message) {
  console.error(message);
  process.exit(1);
}

const candidateRoot = path.resolve(process.argv[2] || "external/ensemble");
const builtLibrary = path.join(candidateRoot, "build", "ensemble.js");
const underscorePath = path.join(candidateRoot, "ensemble", "jslib", "underscore-min.js");
const dataRoot = path.join(candidateRoot, "examples", "loversAndRivals", "data");

if (!fs.existsSync(builtLibrary)) {
  fail(`Ensemble build not found: ${builtLibrary}`);
}

// ENVIRONMENT COMPATIBILITY SHIM ONLY.
// Ensemble's standalone browser bundle expects Underscore to exist as the
// global `_` symbol. Node loads the bundled Underscore through CommonJS, so
// provide the same global binding before evaluating the unmodified build.
const underscoreModule = require(underscorePath);
global._ = underscoreModule._ || underscoreModule;

require(builtLibrary);
const api = global.ensemble;
if (!api) {
  fail("Ensemble standalone build did not expose global.ensemble");
}

function loadJson(name) {
  return JSON.parse(fs.readFileSync(path.join(dataRoot, name), "utf8"));
}

api.reset();
api.loadBaseBlueprints(loadJson("schema.json"));
const cast = api.addCharacters(loadJson("cast.json"));
api.addRules(loadJson("triggerRules.json"));
api.addRules(loadJson("volitionRules.json"));
api.addActions(loadJson("actions.json"));
api.addHistory(loadJson("history.json"));

const before = api.calculateVolition(cast);
const heroToLove = api.getActions("hero", "love", before, cast, 2, 5);
const loveToHero = api.getActions("love", "hero", before, cast, 2, 5);
const heroToRival = api.getActions("hero", "rival", before, cast, 2, 5);

if (!Array.isArray(heroToLove) || heroToLove.length === 0) {
  fail("Original Lovers and Rivals domain produced no hero-to-love actions");
}
if (!Array.isArray(loveToHero) || loveToHero.length === 0) {
  fail("Original Lovers and Rivals domain produced no love-to-hero actions");
}

const selected = heroToLove[0];
api.doAction(selected);
api.runTriggerRules(cast);
api.setupNextTimeStep();

const after = api.calculateVolition(cast);
const heroToLoveAfter = api.getActions("hero", "love", after, cast, 2, 5);

const closenessQuery = {
  category: "feeling",
  type: "closeness",
  first: "hero",
  second: "love"
};
const closeness = api.get(closenessQuery);

const result = {
  candidate_id: "PC-001",
  candidate: "Ensemble",
  upstream_commit: "8b74bdec4ba2ef4e14795b7591df3b5d73f283e3",
  upstream_domain: "examples/loversAndRivals",
  execution_type: "ORIGINAL DOMAIN SMOKE",
  adapter_used: false,
  architecture_modified: false,
  environment_compatibility_shims: ["Provide browser-global `_` in Node host"],
  cast,
  initial_action_counts: {
    hero_to_love: heroToLove.length,
    love_to_hero: loveToHero.length,
    hero_to_rival: heroToRival.length
  },
  selected_native_action: {
    name: selected.name,
    displayName: selected.displayName,
    weight: selected.weight
  },
  post_action_hero_to_love_count: heroToLoveAfter.length,
  hero_to_love_closeness: closeness,
  status: "EXECUTED"
};

fs.mkdirSync("qualification-results", { recursive: true });
fs.writeFileSync(
  path.join("qualification-results", "ensemble-smoke.json"),
  JSON.stringify(result, null, 2) + "\n",
  "utf8"
);

console.log(JSON.stringify(result, null, 2));
