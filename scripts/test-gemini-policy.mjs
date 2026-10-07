#!/usr/bin/env node
// Load the Gemini reviewer network-deny policy example through Gemini CLI's
// own policy loader and policy engine, then assert real deny/allow decisions.
//
// Why a real-engine test: Gemini silently drops rules it considers unsafe
// (e.g. a commandRegex that looks like a nested quantifier). Structural
// checks on the TOML text cannot see that; only the real loader can.
//
// Usage:
//   node scripts/test-gemini-policy.mjs [policy.toml]
//
// Locating Gemini CLI (first match wins):
//   1. GEMINI_CLI_DIR=/path/to/node_modules/@google/gemini-cli
//   2. `npm root -g`/@google/gemini-cli
//
// If Gemini CLI is not installed the test is skipped (exit 0), unless
// REQUIRE_GEMINI_POLICY_TEST=1 is set (CI sets it).

import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const EXPECTED_GEMINI_VERSION = "0.62.0";
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const POLICY = resolve(process.argv[2] ?? join(ROOT, "examples/gemini-user-policies/reviewer-network-deny.toml"));
const REQUIRED = process.env.REQUIRE_GEMINI_POLICY_TEST === "1";
const REVIEWERS = ["reviewer", "security-reviewer", "uiux-reviewer"];

// Commands every reviewer role must be denied, in every approval mode.
const MUST_DENY = [
  "curl https://example.invalid/?d=x",
  "wget -q https://example.invalid/",
  "/usr/bin/curl https://example.invalid/",
  "./wget https://example.invalid/",
  "env curl https://example.invalid/",
  "env FOO=1 /usr/bin/wget https://example.invalid/",
  "FOO=1 curl https://example.invalid/",
  "A=1 B=2 /usr/bin/curl https://example.invalid/",
  "git status && /usr/bin/curl https://example.invalid/",
  "bash -c 'curl https://example.invalid/'",
];

// Ordinary review commands that these rules must NOT deny.
const MUST_NOT_DENY = [
  "git diff HEAD~1",
  "git -C /tmp/wt status",
  "echo curling",
  "grep -r curl src/",
  "rg wget scripts/",
  "cat docs/curl.md",
  "ls /usr/bin/curl",
  "FOO=1 make test",
];

// Gemini's internal debug logger traces every policy check via console.debug.
// Silence it so failures are readable; set GEMINI_POLICY_TEST_DEBUG=1 to keep it.
if (process.env.GEMINI_POLICY_TEST_DEBUG !== "1") console.debug = () => {};

function fail(message) {
  console.error(`[fail] ${message}`);
  process.exitCode = 1;
}

function findGeminiCli() {
  const candidates = [];
  if (process.env.GEMINI_CLI_DIR) candidates.push(process.env.GEMINI_CLI_DIR);
  try {
    const globalRoot = execFileSync("npm", ["root", "-g"], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
    candidates.push(join(globalRoot, "@google/gemini-cli"));
  } catch {
    // npm not available; rely on GEMINI_CLI_DIR only.
  }
  return candidates.find((dir) => existsSync(join(dir, "bundle")) && existsSync(join(dir, "package.json")));
}

async function loadPolicyApi(bundleDir) {
  // Bundle chunk names are content hashes, so discover the chunk that
  // exports the policy API instead of hard-coding a filename.
  const needed = ["loadPoliciesFromToml", "createPolicyEngineConfig", "PolicyEngine", "ApprovalMode"];
  const files = readdirSync(bundleDir).filter((f) => f.endsWith(".js")).sort();
  for (const file of files) {
    const text = readFileSync(join(bundleDir, file), "utf8");
    if (!needed.every((name) => text.includes(`${name},`) || text.includes(`${name}\n`))) continue;
    const mod = await import(pathToFileURL(join(bundleDir, file)).href);
    if (needed.every((name) => name in mod)) return mod;
  }
  return undefined;
}

const cliDir = findGeminiCli();
if (!cliDir) {
  const msg = "Gemini CLI not found (set GEMINI_CLI_DIR or install @google/gemini-cli globally)";
  if (REQUIRED) {
    fail(msg);
    process.exit(1);
  }
  console.log(`[skip] ${msg}; CI runs this test against Gemini CLI ${EXPECTED_GEMINI_VERSION}.`);
  process.exit(0);
}

const version = JSON.parse(readFileSync(join(cliDir, "package.json"), "utf8")).version;
if (version !== EXPECTED_GEMINI_VERSION) {
  const msg = `Gemini CLI ${version} found; policy example is verified for ${EXPECTED_GEMINI_VERSION}`;
  if (REQUIRED) fail(msg);
  else console.log(`[warn] ${msg}`);
}

const bundleDir = join(cliDir, "bundle");
const api = await loadPolicyApi(bundleDir);
if (!api) {
  fail(`could not locate the policy API exports in ${bundleDir}`);
  process.exit(1);
}

// 1. The loader must accept every rule. Gemini reports dropped rules (for
//    example "Unsafe regex pattern (potential ReDoS)") only in `errors`.
const declaredRules = (readFileSync(POLICY, "utf8").match(/^\[\[rule\]\]/gm) ?? []).length;
const loaded = await api.loadPoliciesFromToml([POLICY], () => 4);
for (const error of loaded.errors ?? []) {
  fail(`Gemini policy loader reported ${error.errorType}: ${error.message} (${error.details ?? ""})`);
}

// One TOML rule can expand to several engine rules (one per commandPrefix
// entry), so engine rules must be at least the number of TOML rules.
if (declaredRules === 0) fail(`${POLICY} declares no [[rule]] entries`);
if ((loaded.errors ?? []).length === 0 && (loaded.rules ?? []).length < declaredRules) {
  fail(`only ${(loaded.rules ?? []).length} engine rules loaded from ${declaredRules} declared rules`);
}

// 2. Install the policy as a user-tier policy in an isolated HOME and ask
//    the real engine for decisions, in YOLO (no prompts) and default modes.
const home = mkdtempSync(join(tmpdir(), "gemini-policy-test-"));
const realHome = process.env.HOME;
try {
  mkdirSync(join(home, ".gemini", "policies"), { recursive: true });
  copyFileSync(POLICY, join(home, ".gemini", "policies", "reviewer-network-deny.toml"));
  process.env.HOME = home;

  for (const modeName of ["YOLO", "DEFAULT"]) {
    const mode = api.ApprovalMode[modeName];
    const config = await api.createPolicyEngineConfig({}, mode, join(bundleDir, "policies"));
    const engine = new api.PolicyEngine(config);
    const decide = async (command, subagent) =>
      String((await engine.check({ name: "run_shell_command", args: { command } }, undefined, undefined, subagent)).decision);

    for (const subagent of REVIEWERS) {
      for (const command of MUST_DENY) {
        const decision = await decide(command, subagent);
        if (decision !== "deny") fail(`${modeName} ${subagent}: expected deny, got ${decision}: ${command}`);
      }
      for (const command of MUST_NOT_DENY) {
        const decision = await decide(command, subagent);
        if (decision === "deny") fail(`${modeName} ${subagent}: false positive deny: ${command}`);
      }
    }

    // Scoping: the rules must apply to reviewer subagents only.
    for (const subagent of ["implementer", undefined]) {
      const decision = await decide("curl https://example.invalid/", subagent);
      if (decision === "deny") fail(`${modeName} ${subagent ?? "main session"}: reviewer rule leaked to non-reviewer`);
    }
  }
} finally {
  process.env.HOME = realHome;
  rmSync(home, { recursive: true, force: true });
}

if (process.exitCode) {
  console.error("Gemini policy engine test failed.");
} else {
  console.log(
    `[ok] Gemini ${version} loaded ${declaredRules} policy rules with no errors; ` +
      `${MUST_DENY.length} wrapped/direct curl/wget forms denied and ` +
      `${MUST_NOT_DENY.length} benign commands not denied for ${REVIEWERS.length} reviewer roles in YOLO and default modes.`,
  );
  console.log("Gemini policy engine test passed.");
}
