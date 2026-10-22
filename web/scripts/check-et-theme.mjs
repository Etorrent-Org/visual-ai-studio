import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (relative) => readFileSync(new URL(relative, import.meta.url), "utf8");

test("la charte est chargée après la CSS métier", () => {
  const main = read("../src/main.tsx");
  const i1 = main.indexOf('import "./styles.css"');
  const i2 = main.indexOf('import "./design-system/et-tokens.css"');
  const i3 = main.indexOf('import "./design-system/visual-ai.css"');
  assert.ok(i1 >= 0 && i1 < i2 && i2 < i3);
});

test("la charte est isolée de l'interface et du métier", () => {
  const app = read("../src/App.tsx");
  const theme = read("../src/design-system/visual-ai.css");
  assert.match(app, /className="app-shell et-root"/);
  assert.match(app, /className="et-seal-image"/);
  assert.match(theme, /\.et-root \.sidebar/);
  assert.match(theme, /\.et-root \.panel/);
  assert.match(theme, /\.et-root \.button--primary/);
  assert.doesNotMatch(theme, /\/api\//);
});

test("tokens prélevés sur Life Desk", () => {
  const tokens = read("../src/design-system/et-tokens.css");
  assert.match(tokens, /--et-primary:\s*oklch\(0\.63 0\.17 24\)/);
  assert.match(tokens, /--et-background:\s*oklch\(0\.17 0\.008 255\)/);
  assert.doesNotMatch(tokens, /^\s*(?:body|html|:root)\s*\{/m);
});

test("signature en katakana et SVG rouge", () => {
  const svg = read("../public/brand/erwann-seal.svg");
  const app = read("../src/App.tsx");
  for (const ch of ["エ", "ル", "ワ", "ン"]) assert.ok(svg.includes(ch));
  assert.match(svg, /#AC302B/i);
  assert.match(app, /エルワン/);
});
