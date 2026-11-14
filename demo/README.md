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

## Record the screen

1. Choose **4 April 2011**, show the two reserves, then click **Reveal next week**.
2. Choose **18 January 2011**; show that the outcome is hidden again, then reveal
   the £81,851.42 of cancellations and £57,801.00 shortfall against £24,050.42.
3. Switch back to **4 April 2011** to show the outcome reset.

## Verification

Browser checked both quick selectors, reveal, resetting with the date dropdown,
and a 390px mobile viewport without horizontal overflow. Values matched the
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
