import type { ReviewItem } from "./types";

export type QueueFilter = "all" | "threshold" | "cold";
export function filterQueue(
  items: ReviewItem[],
  query: string,
  filter: QueueFilter,
) {
  const q = query.trim().toLocaleLowerCase();
  return items
    .filter(
      (item) =>
        (!q ||
          [
            item.record_id,
            item.customer_id,
            item.terminal_id,
            item.timestamp,
            ...item.reasons,
          ]
            .join(" ")
            .toLocaleLowerCase()
            .includes(q)) &&
        (filter !== "threshold" || item.review_required) &&
        (filter !== "cold" || item.warnings.some((w) => /cold start/i.test(w))),
    )
    .sort((a, b) => a.rank - b.rank);
}

// Quote every cell and neutralize formulas even after leading whitespace/control characters.
export function csvCell(value: unknown) {
  let text = String(value ?? "");
  if (/^[\s\u0000-\u001f]*[=+\-@]/.test(text) || /^[\t\r\n]/.test(text))
    text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}
export function queueCSV(items: ReviewItem[]) {
  const header = [
    "rank",
    "record_id",
    "customer_id",
    "terminal_id",
    "timestamp_utc",
    "amount",
    "review_priority_score",
    "above_research_threshold",
    "observed_history",
    "warnings",
    "model_version",
  ];
  return (
    "\uFEFF" +
    [
      header,
      ...items.map((i) => [
        i.rank,
        i.record_id,
        i.customer_id,
        i.terminal_id,
        i.timestamp,
        i.amount,
        i.score,
        i.review_required,
        i.reasons.join(" | "),
        i.warnings.join(" | "),
        i.model_version,
      ]),
    ]
      .map((row) => row.map(csvCell).join(","))
      .join("\r\n")
  );
}
