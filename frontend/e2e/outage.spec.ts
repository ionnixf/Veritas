import { test, expect } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import { once } from "node:events";
import { createServer } from "node:net";
import { resolve } from "node:path";

test("real server stop/restart preserves the previous queue and permits recovery", async ({
  page,
}) => {
  test.setTimeout(60000);
  const socket = createServer();
  socket.listen(0, "127.0.0.1");
  await once(socket, "listening");
  const address = socket.address();
  if (!address || typeof address === "string") throw new Error("No local port");
  const port = address.port;
  await new Promise<void>((done) => socket.close(() => done()));
  const url = `http://127.0.0.1:${port}`;
  let child: ChildProcess | undefined;
  const start = async () => {
    child = spawn(
      resolve("../.venv-app/bin/python"),
      [
        "-m",
        "uvicorn",
        "auditlens.backend.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        String(port),
        "--workers",
        "1",
        "--no-access-log",
      ],
      { cwd: resolve(".."), stdio: "ignore" },
    );
    await expect
      .poll(
        async () => {
          try {
            return (await fetch(`${url}/api/v1/health`)).status;
          } catch {
            return 0;
          }
        },
        { timeout: 20000 },
      )
      .toBe(200);
  };
  const stop = async () => {
    if (child && child.exitCode === null && child.signalCode === null) {
      const exited = once(child, "exit");
      child.kill("SIGTERM");
      await exited;
    }
  };
  try {
    await start();
    await page.goto(url);
    await expect(page.getByText("Analysis server connected")).toBeVisible();
    await page.getByRole("button", { name: "Run live demo" }).click();
    await expect(page.locator("tbody tr")).toHaveCount(5);
    await stop();
    await page.getByRole("button", { name: "Reanalyze" }).click();
    await expect(
      page.getByRole("alert").filter({ hasText: "Cannot reach" }),
    ).toBeVisible();
    await expect(page.locator("tbody tr")).toHaveCount(5);
    await expect(
      page
        .getByRole("alert")
        .filter({ hasText: "Analysis server unavailable" }),
    ).toBeVisible();
    await start();
    await page.getByRole("button", { name: "Retry connection" }).click();
    await expect(page.getByText("Analysis server connected")).toBeVisible();
    await page.getByRole("button", { name: "Reanalyze" }).click();
    await expect(page.locator("tbody tr")).toHaveCount(5);
    await expect(
      page.getByRole("button", { name: "own-change-003", exact: true }),
    ).toBeVisible();
  } finally {
    await stop();
  }
});
