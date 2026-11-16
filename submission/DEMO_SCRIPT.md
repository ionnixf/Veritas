# Two-minute demo

Start with `docker compose up`, wait for health, and open http://127.0.0.1:8088.
Record the application window with a voice-over. Use only the bundled fictional
examples; keep personal information out of the recording.

| Time | Show | Suggested narration |
| --- | --- | --- |
| 0:00–0:15 | App landing page | Small merchants cannot manually inspect every purchase. AuditLens AI turns transaction files into a review queue with spending context. |
| 0:15–0:40 | Click **Run live demo**; show the five transactions | This demo runs the bundled XGBoost model on CPU. These are fictional examples, not test-set results. The application also accepts CSV/XLSX transactions and optional preceding history. |
| 0:40–1:00 | Inspect a transaction and its history | Reviewers can inspect the customer's spending context. The score sets review priority; it is not a calibrated fraud probability or an automatic blocking decision. |
| 1:00–1:15 | Change review budget and export CSV | A merchant chooses how many transactions to inspect and exports the review queue. Uploaded files stay in server memory. |
| 1:15–1:40 | Open the Results section of the write-up | We use 32 past-only features. Historical synthetic test average precision was 0.3428 versus 0.2444 for amount ranking. Top-1000 precision was 0.794 versus 0.569. |
| 1:40–2:00 | Limitations in write-up | The corrected test had already been inspected, and terminal-compromise recall is weak. Next we need an untouched chronological evaluation and merchant feedback. This is a prototype, not financial advice. |

Export a video of at most two minutes. Share via unlisted YouTube or a Drive link
that opens without sign-in. Never present localhost as a public hosted demo URL.
