const assert = require("node:assert/strict");
const test = require("node:test");

const { findDuplicateEntries } = require("./validate");

test("accepts unique skill names and paths", () => {
  assert.deepEqual(
    findDuplicateEntries([
      { name: "vendor-one", path: "skills/vendor-one" },
      { name: "vendor-two", path: "skills/vendor-two" },
    ]),
    [],
  );
});

test("rejects duplicate skill names", () => {
  assert.deepEqual(
    findDuplicateEntries([
      { name: "vendor-one", path: "skills/vendor-one" },
      { name: "vendor-one", path: "skills/vendor-two" },
    ]),
    ["skills.json duplicate name 'vendor-one' at entries 1 and 2"],
  );
});

test("rejects duplicate skill paths", () => {
  assert.deepEqual(
    findDuplicateEntries([
      { name: "vendor-one", path: "skills/shared" },
      { name: "vendor-two", path: "skills/shared" },
    ]),
    ["skills.json duplicate path 'skills/shared' at entries 1 and 2"],
  );
});

test("reports repeated duplicates against the first entry", () => {
  assert.deepEqual(
    findDuplicateEntries([
      { name: "vendor-one", path: "skills/vendor-one" },
      { name: "vendor-one", path: "skills/vendor-one" },
      { name: "vendor-one", path: "skills/vendor-one" },
    ]),
    [
      "skills.json duplicate name 'vendor-one' at entries 1 and 2",
      "skills.json duplicate path 'skills/vendor-one' at entries 1 and 2",
      "skills.json duplicate name 'vendor-one' at entries 1 and 3",
      "skills.json duplicate path 'skills/vendor-one' at entries 1 and 3",
    ],
  );
});
