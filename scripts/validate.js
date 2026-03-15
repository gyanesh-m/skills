#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

let exitCode = 0;

function error(msg) {
  console.error(`  ❌ ${msg}`);
  exitCode = 1;
}

function success(msg) {
  console.log(`  ✅ ${msg}`);
}

function validateFrontmatter(content, skillName) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) {
    error(`${skillName}: SKILL.md missing YAML frontmatter`);
    return false;
  }

  const frontmatter = match[1];

  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  if (!nameMatch) {
    error(`${skillName}: SKILL.md frontmatter missing 'name' field`);
    return false;
  }

  const name = nameMatch[1].trim();
  if (name !== skillName) {
    error(
      `${skillName}: SKILL.md frontmatter name '${name}' does not match directory '${skillName}'`
    );
    return false;
  }

  const descMatch = frontmatter.match(/^description:\s*(.+)$/m);
  if (!descMatch) {
    error(`${skillName}: SKILL.md frontmatter missing 'description' field`);
    return false;
  }

  return true;
}

function main() {
  console.log("\n  Galileo Skills Validator\n");

  const manifestPath = path.join(__dirname, "..", "skills.json");
  if (!fs.existsSync(manifestPath)) {
    error("skills.json not found");
    process.exit(1);
  }

  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
  } catch (e) {
    error(`skills.json is not valid JSON: ${e.message}`);
    process.exit(1);
  }

  success("skills.json is valid JSON");

  if (!manifest.skills || !Array.isArray(manifest.skills)) {
    error('skills.json missing "skills" array');
    process.exit(1);
  }

  success(`skills.json contains ${manifest.skills.length} skill(s)`);

  for (const skill of manifest.skills) {
    const skillDir = path.join(__dirname, "..", skill.path);
    const skillMd = path.join(skillDir, "SKILL.md");

    if (!fs.existsSync(skillDir)) {
      error(`${skill.name}: directory '${skill.path}' does not exist`);
      continue;
    }

    success(`${skill.name}: directory exists`);

    if (!fs.existsSync(skillMd)) {
      error(`${skill.name}: SKILL.md not found`);
      continue;
    }

    success(`${skill.name}: SKILL.md exists`);

    const content = fs.readFileSync(skillMd, "utf-8");

    if (validateFrontmatter(content, skill.name)) {
      success(`${skill.name}: frontmatter is valid`);
    }

    const refsDir = path.join(skillDir, "references");
    if (fs.existsSync(refsDir)) {
      const refFiles = fs.readdirSync(refsDir).filter((f) => f.endsWith(".md"));
      success(`${skill.name}: ${refFiles.length} reference file(s) found`);
    }
  }

  console.log();

  if (exitCode === 0) {
    console.log("  All checks passed!\n");
  } else {
    console.log("  Some checks failed.\n");
  }

  process.exit(exitCode);
}

main();
