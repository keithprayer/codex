import { cp, mkdir, rm, readFile } from "node:fs/promises";
const config = JSON.parse(await readFile("config.json", "utf8"));
const snapshot = JSON.parse(await readFile("web/data/snapshot.json", "utf8"));
if (config.schemaVersion !== 1 || snapshot.schemaVersion !== 1)
  throw new Error("Unsupported schema");
await rm("dist", { recursive: true, force: true });
await mkdir("dist", { recursive: true });
await cp("web", "dist", { recursive: true });
await cp("config.json", "dist/data/config.json");
console.log("Built dist/ — no credentials or collector source included.");
