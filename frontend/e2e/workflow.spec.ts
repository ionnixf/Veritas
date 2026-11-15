import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import AxeBuilder from "@axe-core/playwright";
import { writeFile } from "node:fs/promises";
import { mkdirSync } from "node:fs";

test("drag and drop uploads both real CSV fixtures", async ({ page }) => {
  await ready(page);
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  for (const name of ["transactions", "history"]) {
    const csv = await readFile(`${assets}/${name}.csv`, "utf8");
    const data = await page.evaluateHandle(
      ({ csv, name }) => {
        const transfer = new DataTransfer();
        transfer.items.add(
          new File([csv], `${name}.csv`, { type: "text/csv" }),
        );
        return transfer;
      },
      { csv, name },
    );
    await page
      .locator(".file-field")
      .nth(name === "transactions" ? 0 : 1)
      .locator(".dropzone")
      .dispatchEvent("drop", { dataTransfer: data });
    await data.dispose();
    await expect(page.getByText(`${name}.csv`, { exact: true })).toBeVisible();
  }
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(5);
});

const assets = resolve("../src/auditlens/backend/assets");
const output = resolve(process.env.E2E_OUTPUT_DIR || "./test-results/evidence");
const screenshots = resolve(output, "screenshots");
mkdirSync(screenshots, { recursive: true });
async function ready(page: Page) {
  await page.goto("/");
  await expect(page.getByText("Analysis server connected")).toBeVisible();
}
async function demo(page: Page) {
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/demo/analyze") && r.status() === 200,
  );
  await page.getByRole("button", { name: "Run live demo" }).click();
  const result = await (await response).json();
  await expect(
    page.getByRole("heading", { name: "A closer look, in the right order." }),
  ).toBeVisible();
  return result;
}

test("landing → real inference → detail → budget → complete CSV export", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await ready(page);
  await expect(
    page.getByRole("heading", {
      name: "Spot suspicious purchases before they become costly.",
    }),
  ).toBeVisible();
  await page.screenshot({
    path: `${screenshots}/desktop-overview.png`,
    fullPage: true,
  });
  const result = await demo(page);
  expect(result.analyzed_count).toBe(5);
  expect(result.history_count).toBe(93);
  expect(result.operations[0].record_id).toBe("own-change-003");
  await expect(page.locator("tbody tr")).toHaveCount(5);
  await expect(page.locator("tbody tr").first()).toContainText(
    result.operations[0].score.toFixed(4),
  );
  await page.screenshot({
    path: `${screenshots}/desktop-queue.png`,
    fullPage: true,
  });
  await page
    .getByRole("button", { name: result.operations[0].record_id, exact: true })
    .click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText(result.operations[0].terminal_id);
  for (const reason of result.operations[0].reasons)
    await expect(dialog.getByText(reason, { exact: true })).toBeVisible();
  await page.screenshot({
    path: `${screenshots}/desktop-detail.png`,
    fullPage: false,
  });
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByRole("button", {
      name: result.operations[0].record_id,
      exact: true,
    }),
  ).toBeFocused();
  await page.getByLabel("Review budget", { exact: true }).fill("1");
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/demo/analyze") && r.status() === 200,
  );
  await page.getByRole("button", { name: "Reanalyze" }).click();
  expect((await (await response).json()).queue_count).toBe(1);
  await expect(page.locator("tbody tr")).toHaveCount(1);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export queue CSV" }).click();
  const csv = await readFile((await (await download).path())!, "utf8");
  expect(csv).toContain(result.operations[0].record_id);
  expect(csv.split("\r\n")).toHaveLength(2);
  expect(csv).toContain(String(result.operations[0].score));
  expect(errors).toEqual([]);
});

test("real CSV, XLSX, cold start, replacement and server validation errors", async ({
  page,
}) => {
  await ready(page);
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  await page
    .locator("#transactions")
    .setInputFiles(`${assets}/transactions.csv`);
  await page.locator("#history").setInputFiles(`${assets}/history.csv`);
  await page.getByLabel("Review budget", { exact: true }).fill("3");
  await page.screenshot({
    path: `${screenshots}/desktop-upload.png`,
    fullPage: true,
  });
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(3);
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  await page
    .locator("#transactions")
    .setInputFiles(resolve("e2e/transactions.xlsx"));
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(3);
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Remove prior customer history" })
    .click();
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.locator(".coverage")).toContainText("No history supplied");
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  await page.locator("#transactions").setInputFiles({
    name: "invalid.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("wrong,columns\n1,2\n"),
  });
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Exactly record_id, timestamp, customer_id, terminal_id, amount required",
  );
  await page.screenshot({
    path: `${screenshots}/desktop-invalid-upload.png`,
    fullPage: true,
  });
  await page.locator("#transactions").setInputFiles({
    name: "notes.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("not a table"),
  });
  await expect(page.getByRole("alert")).toContainText(
    "Choose a CSV or XLSX file",
  );
  await page
    .getByRole("button", { name: "Remove transactions to analyze" })
    .click();
  await expect(
    page.getByText("invalid.csv", { exact: true }),
  ).not.toBeVisible();
});

test("real pagination keeps original ranks; search, filter, full export and template download", async ({
  page,
}) => {
  await ready(page);
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  const csv =
    "record_id,timestamp,customer_id,terminal_id,amount\n" +
    Array.from(
      { length: 25 },
      (_, i) =>
        `${i === 0 ? "=1+1" : `test-${i}`},2026-02-01T12:00:00,shop-alex,checkout-01,${195 + i}`,
    ).join("\n");
  await page.locator("#transactions").setInputFiles({
    name: "pagination.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(csv),
  });
  await page.locator("#history").setInputFiles(`${assets}/history.csv`);
  await page.getByLabel("Review budget", { exact: true }).fill("25");
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await expect(page.locator("tbody tr")).toHaveCount(10);
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(
    page.locator("tbody tr").first().locator("td").first(),
  ).toHaveText("11");
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.locator("tbody tr")).toHaveCount(5);
  await expect(
    page.locator("tbody tr").first().locator("td").first(),
  ).toHaveText("21");
  await page.getByLabel("Search review queue").fill("=1+1");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export queue CSV" }).click();
  const exported = await readFile((await (await download).path())!, "utf8");
  expect(exported.split("\r\n")).toHaveLength(26);
  expect(exported).toContain('"\'=1+1"');
  await page.getByLabel("Search review queue").fill("not-present");
  await expect(
    page.getByRole("heading", { name: "No queued transactions match." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await expect(page.locator("tbody tr")).toHaveCount(10);
  await page.getByLabel("Filter review queue").selectOption("cold");
  await expect(
    page.getByRole("heading", { name: "No queued transactions match." }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  const templateDownload = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Transactions CSV", exact: true })
    .click();
  expect(await readFile((await (await templateDownload).path())!, "utf8")).toBe(
    await readFile(`${assets}/transactions.csv`, "utf8"),
  );
});

test("model evidence uses live metadata and discloses corrected test and failure case", async ({
  page,
  request,
}) => {
  await ready(page);
  await page.getByRole("link", { name: "Model evidence", exact: true }).click();
  const model = await (await request.get("/api/v1/model")).json();
  await expect(
    page.getByText(model.benchmark.test.average_precision.toFixed(4), {
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.getByText("2018-05-01 — 2018-07-31")).toBeVisible();
  await expect(
    page.getByText("The test is not a new, untouched holdout."),
  ).toBeVisible();
  await expect(
    page.getByText("Random terminal compromise is largely missed."),
  ).toBeVisible();
  await page.screenshot({
    path: `${screenshots}/desktop-evidence.png`,
    fullPage: true,
  });
});

test("mobile layouts and keyboard access through live demo", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  await page.screenshot({
    path: `${screenshots}/mobile-overview.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await demo(page);
  await page.screenshot({
    path: `${screenshots}/mobile-queue.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page
    .getByRole("button", { name: "own-change-003", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.screenshot({
    path: `${screenshots}/mobile-detail.png`,
    fullPage: false,
  });
  await page.keyboard.press("Escape");
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  await page.screenshot({
    path: `${screenshots}/mobile-upload.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("link", { name: "Model evidence", exact: true }).click();
  await page.screenshot({
    path: `${screenshots}/mobile-evidence.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("fault injection: unavailable server, empty result, indeterminate loading and recoverable analysis error", async ({
  page,
}) => {
  await page.route("**/api/v1/health", (r) => r.abort("failed"));
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText(
    "Analysis server unavailable",
  );
  await expect(
    page.getByRole("button", { name: "Run live demo" }),
  ).toBeDisabled();
  await page.unroute("**/api/v1/health");
  await page.getByRole("button", { name: "Retry connection" }).click();
  await expect(page.getByText("Analysis server connected")).toBeVisible();
  await page.route("**/api/v1/demo/analyze", async (route) => {
    const actual = await route.fetch();
    const body = await actual.json();
    await route.fulfill({ json: { ...body, operations: [], queue_count: 0 } });
  });
  await page.getByRole("button", { name: "Run live demo" }).click();
  await expect(
    page.getByRole("heading", { name: "No transactions returned." }),
  ).toBeVisible();
  await page.unroute("**/api/v1/demo/analyze");
  let release: () => void = () => {};
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/v1/demo/analyze", async (route) => {
    await gate;
    await route.fulfill({
      status: 429,
      json: {
        error: {
          code: "analysis_busy",
          message: "Analysis capacity is busy; retry shortly.",
        },
      },
    });
  });
  await page.getByRole("button", { name: "Reanalyze" }).click();
  await expect(
    page.getByText("Analyzing behavioral history", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("progressbar")).toHaveCount(0);
  release();
  await expect(page.getByRole("alert")).toContainText(
    "Analysis capacity is busy; retry shortly.",
  );
  await expect(page.getByRole("button", { name: "Reanalyze" })).toBeEnabled();
});

test("retrying a template download clears the previous error", async ({
  page,
}) => {
  await ready(page);
  await page
    .getByRole("link", { name: "Analyze transactions", exact: true })
    .click();
  await page.route("**/api/v1/templates/transactions.csv", (route) =>
    route.abort("failed"),
  );
  await page
    .getByRole("button", { name: "Transactions CSV", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("Cannot reach");

  await page.unroute("**/api/v1/templates/transactions.csv");
  const download = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Transactions CSV", exact: true })
    .click();
  expect((await download).suggestedFilename()).toBe("transactions.csv");
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.locator(".notice")).toHaveText(
    "Transactions template downloaded.",
  );
});

test("successful reanalysis clears the connection warning after an interrupted request", async ({
  page,
}) => {
  await ready(page);
  await demo(page);
  await page.route("**/api/v1/demo/analyze", (route) => route.abort("failed"));
  await page.getByRole("button", { name: "Reanalyze" }).click();
  await expect(page.locator(".connection-banner")).toContainText(
    "Analysis server unavailable",
  );
  await expect(page.locator("tbody tr")).toHaveCount(5);

  await page.unroute("**/api/v1/demo/analyze");
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/demo/analyze") && r.status() === 200,
  );
  await page.getByRole("button", { name: "Reanalyze" }).click();
  await response;
  await expect(page.getByText("Analysis server connected")).toBeVisible();
  await expect(page.locator(".connection-banner")).toHaveCount(0);
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.locator("tbody tr")).toHaveCount(5);
});

test("automated accessibility checks on desktop and mobile, including transaction dialog", async ({
  page,
}) => {
  const reports: object[] = [];
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    await ready(page);
    for (const name of [
      "Overview",
      "Analyze transactions",
      "Model evidence",
      "Review queue",
    ]) {
      if (name === "Review queue") {
        await page.getByRole("link", { name: "Overview", exact: true }).click();
        await demo(page);
      } else await page.getByRole("link", { name, exact: true }).click();
      const audit = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze();
      reports.push({
        width,
        page: name,
        violations: audit.violations,
        passes: audit.passes.length,
      });
      await writeFile(
        resolve(output, "accessibility.json"),
        JSON.stringify(reports, null, 2),
      );
      expect(
        audit.violations.map((v) => ({
          id: v.id,
          nodes: v.nodes.map((n) => ({
            target: n.target,
            summary: n.failureSummary,
          })),
        })),
      ).toEqual([]);
    }
    await page
      .getByRole("button", { name: "own-change-003", exact: true })
      .click();
    const audit = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    reports.push({
      width,
      page: "Transaction dialog",
      violations: audit.violations,
      passes: audit.passes.length,
    });
    await writeFile(
      resolve(output, "accessibility.json"),
      JSON.stringify(reports, null, 2),
    );
    expect(
      audit.violations.map((v) => ({
        id: v.id,
        nodes: v.nodes.map((n) => ({
          target: n.target,
          summary: n.failureSummary,
        })),
      })),
    ).toEqual([]);
    await page.keyboard.press("Escape");
  }
});

test("compact phone, tablet and desktop keep table overflow inside its scroll region", async ({
  page,
}) => {
  await ready(page);
  await demo(page);
  for (const width of [320, 768, 1024, 1920]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page
      .getByRole("link", { name: "Analyze transactions", exact: true })
      .click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page
      .getByRole("link", { name: "Model evidence", exact: true })
      .click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.getByRole("link", { name: /^Review queue/ }).click();
  }
});
