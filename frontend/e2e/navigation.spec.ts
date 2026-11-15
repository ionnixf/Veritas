import { expect, test } from "@playwright/test";

test("skip link focuses the current page without changing its route", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.getByText("Analysis server connected")).toBeVisible();
  for (const [name, title] of [
    ["Analyze transactions", "Bring the history into view."],
    ["Review queue", "A closer look, in the right order."],
    ["Model evidence", "Evidence you can inspect."],
  ]) {
    await page.getByRole("link", { name, exact: true }).click();
    await expect(page.getByRole("heading", { name: title })).toBeFocused();
    const currentURL = page.url();
    await page.getByRole("link", { name: "Skip to content" }).focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("main")).toBeFocused();
    await expect(page).toHaveURL(currentURL);
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
  }
});
