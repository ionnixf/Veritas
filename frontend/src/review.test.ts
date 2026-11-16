import { describe, expect, it } from "vitest";
import { csvCell, filterQueue, queueCSV } from "./review";
import type { ReviewItem } from "./types";

const item = (overrides: Partial<ReviewItem> = {}): ReviewItem => ({
  rank: 1,
  record_id: "001",
  customer_id: "customer",
  terminal_id: "terminal",
  timestamp: "2026-02-01T12:00:00",
  amount: 195,
  score: 0.95926833152771,
  score_kind: "uncalibrated_classifier_score",
  reasons: ["Prior mean=32.13"],
  explanation_kind: "observed_past_history_not_model_attribution",
  warnings: [],
  review_required: true,
  model_version: "handbook-xgboost-v1",
  validation_status: "RESEARCH DEMO",
  ...overrides,
});

describe("safe queue export", () => {
  it.each([
    '=HYPERLINK("example")',
    "+123",
    "-1",
    "@SUM(A1)",
    "  =1",
    "\t=1",
    "\r=1",
    "\n1",
    "\u0000=1",
  ])("neutralizes spreadsheet formula/control prefix %j", (value) => {
    expect(csvCell(value).startsWith("\"'")).toBe(true);
  });
  it("quotes commas, quotes and newlines while preserving ordinary IDs", () => {
    expect(csvCell("001")).toBe('"001"');
    expect(csvCell('a,"b"\nc')).toBe('"a,""b""\nc"');
  });
  it("exports original score precision and all backend fields without a probability label", () => {
    const csv = queueCSV([
      item({ record_id: "=1", warnings: ["Incomplete history"] }),
    ]);
    expect(csv).toContain('"\'=1"');
    expect(csv).toContain('"0.95926833152771"');
    expect(csv).toContain('"Incomplete history"');
    expect(csv).not.toContain("probability");
    expect(csv.split("\r\n")).toHaveLength(2);
  });
});

describe("top-K queue view", () => {
  const items = [
    item({
      rank: 3,
      record_id: "third",
      customer_id: "NEW",
      warnings: ["Customer cold start: no earlier transaction"],
      review_required: false,
    }),
    item({ rank: 1, record_id: "first" }),
    item({ rank: 2, record_id: "second", terminal_id: "OTHER" }),
  ];
  it("preserves original ranks after filtering and orders by backend rank", () => {
    expect(filterQueue(items, "", "all").map((i) => i.rank)).toEqual([1, 2, 3]);
    expect(filterQueue(items, "new", "all").map((i) => i.rank)).toEqual([3]);
    expect(filterQueue(items, " other ", "all").map((i) => i.rank)).toEqual([
      2,
    ]);
    expect(items[0].rank).toBe(3);
  });
  it("uses backend threshold and warnings, not invented score bands", () => {
    expect(filterQueue(items, "", "threshold").map((i) => i.rank)).toEqual([
      1, 2,
    ]);
    expect(filterQueue(items, "", "cold").map((i) => i.rank)).toEqual([3]);
    expect(filterQueue(items, "missing", "all")).toEqual([]);
  });
});
