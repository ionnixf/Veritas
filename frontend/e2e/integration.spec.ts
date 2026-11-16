import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { request as httpRequest } from "node:http";

const assets = resolve("../src/auditlens/backend/assets");
const header = "record_id,timestamp,customer_id,terminal_id,amount\n";

test("real validation: missing field, wrong type, empty and oversized files; limited history", async ({
  page,
}) => {
  await page.goto("/#analyze");
  await expect(page.getByText("Analysis server connected")).toBeVisible();
  let analyses = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/analyze")) analyses++;
  });

  // Empty/large files are blocked by the UI before sending sensitive bytes.
  for (const [name, buffer, message] of [
    ["empty.csv", Buffer.alloc(0), "This file is empty"],
    [
      "oversized.csv",
      Buffer.alloc(8 * 1024 * 1024 + 1, 32),
      "Each file must be no larger than 8 MiB",
    ],
  ] as const) {
    await page
      .locator("#transactions")
      .setInputFiles({ name, mimeType: "text/csv", buffer });
    await expect(page.getByRole("alert")).toContainText(message);
  }
  expect(analyses).toBe(0);

  for (const [csv, message] of [
    [
      "record_id,timestamp,customer_id,amount\nr,2026-02-01T12:00:00,c,20\n",
      "Exactly record_id, timestamp, customer_id, terminal_id, amount required",
    ],
    [
      header + "r,2026-02-01T12:00:00,c,t,not-a-number\n",
      "Values violate the Handbook schema",
    ],
    [header, "Table must contain at least one transaction"],
  ]) {
    await page.locator("#transactions").setInputFiles({
      name: "invalid.csv",
      mimeType: "text/csv",
      buffer: Buffer.from(csv),
    });
    const response = page.waitForResponse((r) => r.url().endsWith("/analyze"));
    await page
      .getByRole("button", { name: "Run analysis", exact: true })
      .click();
    expect((await response).status()).toBe(422);
    await expect(page.getByRole("alert")).toContainText(message);
  }

  await page
    .locator("#transactions")
    .setInputFiles(`${assets}/transactions.csv`);
  const history = (await readFile(`${assets}/history.csv`, "utf8"))
    .trim()
    .split("\n");
  await page.locator("#history").setInputFiles({
    name: "short-history.csv",
    mimeType: "text/csv",
    buffer: Buffer.from([history[0], ...history.slice(-3)].join("\n") + "\n"),
  });
  await page.getByLabel("Review budget", { exact: true }).fill("2");
  const response = page.waitForResponse((r) => r.url().endsWith("/analyze"));
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  const result = await (await response).json();
  expect(result.history_count).toBe(3);
  expect(result.queue_count).toBe(2);
  expect(result.operations[0].score).toBeGreaterThanOrEqual(
    result.operations[1].score,
  );
  await expect(page.locator("tbody tr")).toHaveCount(2);
  await expect(page.locator(".coverage")).toContainText(
    "Insufficient history coverage",
  );
});

test("actual HTTP byte limits reject both an oversized multipart file and chunked body", async ({
  request,
  baseURL,
}) => {
  const file = await request.post("/api/v1/analyze", {
    multipart: {
      transactions: {
        name: "large.csv",
        mimeType: "text/csv",
        buffer: Buffer.alloc(8 * 1024 * 1024 + 1, 32),
      },
      top_k: "1",
    },
  });
  expect(file.status()).toBe(413);
  expect((await file.json()).error.code).toBe("file_too_large");
  const body = await new Promise<{ status: number; body: string }>(
    (resolve, reject) => {
      // No Content-Length: Node sends real HTTP/1.1 chunked transfer encoding.
      const upload = httpRequest(
        new URL("/api/v1/analyze", baseURL),
        { method: "POST" },
        (response) => {
          let text = "";
          response.on("data", (chunk) => {
            text += chunk;
          });
          response.on("end", () =>
            resolve({ status: response.statusCode!, body: text }),
          );
        },
      );
      upload.on("error", reject);
      const chunk = Buffer.alloc(1024 * 1024, 32);
      for (let i = 0; i < 17; i++) upload.write(chunk);
      upload.end(Buffer.from(" "));
    },
  );
  expect(body.status).toBe(413);
  expect(JSON.parse(body.body).error.code).toBe("request_too_large");
  expect((await request.get("/api/v1/health")).status()).toBe(200);
});
