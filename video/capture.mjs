import {chromium} from "playwright";
import {mkdir} from "node:fs/promises";
import {resolve} from "node:path";

const outputDir = resolve("public/screens");
await mkdir(outputDir, {recursive: true});

const browser = await chromium.launch({headless: true});
const page = await browser.newPage({viewport: {width: 1440, height: 900}, deviceScaleFactor: 1});
await page.goto("http://127.0.0.1:8501", {waitUntil: "load"});
await page.waitForTimeout(15000);

const shots = [
  ["Overview", "01-overview.png"],
  ["Demand Forecast", "02-forecast.png"],
  ["Customer Intelligence", "03-customers.png"],
  ["Churn Risk", "04-churn.png"],
  ["Inventory Control", "05-inventory.png"],
  ["Export Center", "06-exports.png"]
];

for (const [tabName, filename] of shots) {
  await page.getByRole("tab", {name: tabName, exact: true}).click();
  await page.waitForTimeout(1200);
  await page.screenshot({path: resolve(outputDir, filename), fullPage: false});
}

await browser.close();
