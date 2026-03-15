#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const REPO_URL = "https://github.com/gyanesh-m/skills";
const RAW_BASE =
  "https://raw.githubusercontent.com/gyanesh-m/skills/master";

const SKILLS_MANIFEST = {
  "galileo-python-sdk": {
    path: "skills/galileo-python-sdk",
    files: [
      "SKILL.md",
      "references/INTEGRATIONS.md",
      "references/METRICS.md",
      "references/EVALUATION.md",
    ],
  },
  "galileo-typescript-sdk": {
    path: "skills/galileo-typescript-sdk",
    files: [
      "SKILL.md",
      "references/INTEGRATIONS.md",
      "references/METRICS.md",
      "references/EVALUATION.md",
    ],
  },
};

const AGENT_DIRS = {
  claude: ".claude/skills",
  cursor: ".cursor/skills",
  copilot: ".github/skills",
  codex: ".agents/skills",
  amp: ".amp/skills",
  roo: ".roo/skills",
  opencode: ".opencode/skills",
  gemini: ".gemini/skills",
};

function parseArgs(args) {
  const parsed = { skills: [], agent: null, list: false, help: false };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--list" || arg === "-l") {
      parsed.list = true;
    } else if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--skill" || arg === "-s") {
      if (args[i + 1]) {
        parsed.skills.push(args[++i]);
      }
    } else if (arg === "--agent" || arg === "-a") {
      if (args[i + 1]) {
        parsed.agent = args[++i].toLowerCase();
      }
    }
  }

  return parsed;
}

function printHelp() {
  console.log(`
  Galileo Skills Installer

  Usage:
    npx add-skill gyanesh-m/skills [options]

  Options:
    --skill, -s <name>   Install a specific skill (can be used multiple times)
    --agent, -a <name>   Target a specific AI assistant (claude, cursor, copilot, codex, amp, roo, opencode, gemini)
    --list,  -l          List available skills
    --help,  -h          Show this help message

  Examples:
    npx add-skill gyanesh-m/skills                          Install all skills
    npx add-skill gyanesh-m/skills --skill galileo-python-sdk   Install Python SDK skill only
    npx add-skill gyanesh-m/skills --agent cursor            Install for Cursor only
  `);
}

function listSkills() {
  console.log("\n  Available Galileo Skills:\n");
  for (const [name, info] of Object.entries(SKILLS_MANIFEST)) {
    console.log(`    ${name}`);
    console.log(`      Path: ${info.path}`);
    console.log(`      Files: ${info.files.join(", ")}`);
    console.log();
  }
}

function detectAgents(cwd) {
  const detected = [];
  for (const [agent, dir] of Object.entries(AGENT_DIRS)) {
    const agentParent = path.join(cwd, dir.split("/")[0]);
    if (fs.existsSync(agentParent) || agent === "cursor" || agent === "claude") {
      detected.push(agent);
    }
  }
  return detected.length > 0 ? detected : ["claude"];
}

function downloadFile(url) {
  try {
    const result = execSync(`curl -fsSL "${url}"`, {
      encoding: "utf-8",
      timeout: 30000,
    });
    return result;
  } catch {
    return null;
  }
}

function installSkill(skillName, skillInfo, targetDir) {
  const skillDir = path.join(targetDir, skillName);

  for (const file of skillInfo.files) {
    const filePath = path.join(skillDir, file);
    const fileDir = path.dirname(filePath);
    const url = `${RAW_BASE}/${skillInfo.path}/${file}`;

    fs.mkdirSync(fileDir, { recursive: true });

    const localPath = path.join(__dirname, "..", skillInfo.path, file);
    let content;

    if (fs.existsSync(localPath)) {
      content = fs.readFileSync(localPath, "utf-8");
    } else {
      content = downloadFile(url);
    }

    if (content) {
      fs.writeFileSync(filePath, content);
      console.log(`    Wrote ${path.relative(process.cwd(), filePath)}`);
    } else {
      console.error(`    Failed to fetch ${file}`);
    }
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printHelp();
    process.exit(0);
  }

  if (args.list) {
    listSkills();
    process.exit(0);
  }

  const cwd = process.cwd();
  const skillNames =
    args.skills.length > 0 ? args.skills : Object.keys(SKILLS_MANIFEST);
  const agents = args.agent ? [args.agent] : detectAgents(cwd);

  const invalidSkills = skillNames.filter((s) => !SKILLS_MANIFEST[s]);
  if (invalidSkills.length > 0) {
    console.error(`\n  Unknown skill(s): ${invalidSkills.join(", ")}`);
    console.error("  Use --list to see available skills.\n");
    process.exit(1);
  }

  if (args.agent && !AGENT_DIRS[args.agent]) {
    console.error(`\n  Unknown agent: ${args.agent}`);
    console.error(
      `  Supported agents: ${Object.keys(AGENT_DIRS).join(", ")}\n`
    );
    process.exit(1);
  }

  console.log("\n  Galileo Skills Installer\n");

  for (const agent of agents) {
    const targetDir = path.join(cwd, AGENT_DIRS[agent]);
    console.log(`  Installing for ${agent} (${AGENT_DIRS[agent]}):`);

    for (const skillName of skillNames) {
      console.log(`\n  Skill: ${skillName}`);
      installSkill(skillName, SKILLS_MANIFEST[skillName], targetDir);
    }

    console.log();
  }

  console.log("  Done! Skills installed successfully.\n");
}

main();
