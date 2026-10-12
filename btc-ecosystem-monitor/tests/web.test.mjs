import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  esc,
  safeUrl,
  format,
  percent,
  inWindow,
  filterProjects,
  readStored,
  chartPath,
  validateConfig,
} from "../web/lib.js";
test("untrusted text and non-HTTPS links are inert", () => {
  assert.equal(esc('<img onerror="x">'), "&lt;img onerror=&quot;x&quot;&gt;");
  assert.equal(safeUrl("javascript:alert(1)"), "#");
  assert.equal(safeUrl("data:text/html,evil"), "#");
});
test("missing numbers remain N/A, zero is real", () => {
  assert.equal(format(null), "N/A");
  assert.equal(percent(undefined), "N/A");
  assert.equal(percent(0), "0.00%");
});
test("window excludes start and future", () => {
  const t = "2026-10-12T06:00:00Z";
  assert.equal(inWindow("2026-10-11T06:00:00Z", t, 1), false);
  assert.equal(inWindow("2026-10-12T06:00:01Z", t, 1), false);
  assert.equal(inWindow(t, t, 1), true);
});
test("configuration, ecosystem and favorites filters", async () => {
  const c = JSON.parse(
    await readFile(new URL("../config.json", import.meta.url)),
  );
  validateConfig(c);
  assert.equal(filterProjects(c.projects, { ecosystem: "RGB" }).length, 2);
  assert.equal(
    filterProjects(c.projects, { starred: true, favorites: ["rgb"] })[0].id,
    "rgb",
  );
  assert.equal(
    filterProjects(c.projects, { query: "LIGHT" })[0].id,
    "bitlight",
  );
});
test("malformed local storage falls back", () =>
  assert.deepEqual(readStored({ getItem: () => "{bad" }, "x", []), []));
test("chart omits missing series and rejects nonnumeric injection", () => {
  assert.equal(chartPath([]), "");
  assert.equal(chartPath([[1, "<script>"]]), "");
  assert.match(
    chartPath([
      [1, 10],
      [2, 20],
    ]),
    /^M[\d.,]+ L?[\d.,]*|^M/,
  );
});
test("identity gate prevents CRC20 ticker-only pricing", async () => {
  const c = JSON.parse(
    await readFile(new URL("../config.json", import.meta.url)),
  );
  c.projects.find((p) => p.id === "crc-garden").assets[0].marketEnabled = true;
  assert.throws(() => validateConfig(c), /启用行情前/);
});
