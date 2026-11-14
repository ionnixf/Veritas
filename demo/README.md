# ReserveWeek demo

From the repository root, run:

```bash
python3 -m demo.app
```

Open http://127.0.0.1:8000. Stop with Ctrl+C. Python 3 standard library only;
no installation, internet, keys, or API needed. If the port is occupied, use
`python3 -m demo.app --port 8001`.

The server reads `artifacts/validation_replay.csv` at startup. Restart after CSV
updates. The date selector includes only available rows. Recommended reserve is
`model_q80`; the fixed comparison is `training_q80`. All amounts come from the
selected CSV row. The seven-day window includes the selected date and six more days.
Actual amounts and the shortfall or unused reserve appear only after **Reveal next
week**. Changing the date clears the outcome. This is a presentation reveal, not a
security boundary: historical data are embedded locally in the page.

## Record a two-minute English demo

Set the browser viewport to **1280 × 720**, zoom to **100%**, and open the local
URL. Both revealed scenarios fit without scrolling. The footer identifies the
validation weeks (1 January–30 June 2011, derived from the CSV date range plus
six days). No final test data are needed.

Three actions for the operator / participant 3:

1. **0:00–0:45 — 4 April 2011.** Show £22,799.09 recommended and £18,491.18 fixed,
   then click **Reveal next week**: £12,885.66 recorded cancellations and £9,913.43
   unused reserve. Say: “Before buying stock, I choose a reserve for next week's
   cancellations. The fixed comparison keeps the same amount every week, based on
   training data. Here the recommended reserve covers cancellations, with money left.”
2. **0:45–1:30 — 18 January 2011.** Click the quick selector; pause to show the
   outcome is hidden. Reveal £81,851.42 against £24,050.42 reserved, a £57,801.00
   shortfall. Say: “This week, recorded cancellations exceeded the reserve.
   Shortfall means the reserve was not enough; unused reserve means money was left.”
3. **1:30–2:00 — back to 4 April 2011.** Show the result resetting, then optionally
   reveal again. Say: “These are historical recorded order cancellations from the
   validation period, not refund payment dates. Past coverage does not guarantee
   future coverage.” Participant 3 can use these actions independently and report
   any unclear label, clipped amount, or confusing narration before recording.

## Verification

Release verification: both quick selectors, reveal, and resetting with the date
dropdown passed at 1280 × 720. Both outcomes and footer fit without scrolling;
48px reserve and 34px outcome amounts were visually checked. Browser requests
to external hosts were blocked during reload and both scenarios; no external
requests occurred. The standard-library server started with one command.
The initial version also passed a 390px mobile overflow check. Values matched the
existing CLI:

| Date | Model reserve | Fixed reserve | Recorded cancellations | Result |
| --- | ---: | ---: | ---: | ---: |
| 2011-04-04 | £22,799.09 | £18,491.18 | £12,885.66 | £9,913.43 unused |
| 2011-01-18 | £24,050.42 | £18,491.18 | £81,851.42 | £57,801.00 shortfall |

CLI remains available, unchanged:

```bash
python3 -m demo.replay 2011-01-18
python3 -m demo.replay 2011-01-18 --reveal
```

No model evaluation or final ML test was run. Figures describe historical amounts
of recorded cancellations, not refund settlement dates or observed cash needs.
