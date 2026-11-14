# ReserveWeek

**Track:** AI + Finance · **Starting point:** Our own idea

**Team:** [Add contributor names before submission.]

**The problem.** Before buying stock, an online shopkeeper chooses how much to reserve for the next seven days of recorded cancellations. We test that decision under a hypothetical 4:1 cost of insufficient versus unused reserve.

**What we built.** An offline demo takes a historical decision date, shows a recommended reserve beside a fixed rule, then reveals the week's recorded cancellations, shortfall or unused reserve. We built the daily aggregation, chronological evaluation, reserve model and replay around this decision.

**How it works.** UCI Online Retail II covers one UK retailer. We aggregate invoices to 737 calendar days. Cancellations are negative-quantity, positive-price lines on C-prefixed invoices; overlapping worksheets and partial boundary dates are handled in the data manifest. Four features summarise sales and cancellations through the previous day. The model blends a linear 80th-percentile regression with the fixed training-period Q80, equally weighted. Training uses 333 decision dates with targets ending in December 2010; validation informed development. The final method and comparison were frozen before the ML owner's test evaluation.

**Held-out results.** The test contains **155 daily decision dates, 1 July–2 December 2011**, each forecasting D…D+6. These targets overlap; they are not 155 independent weeks. Mean q=0.8 pinball loss is in GBP per decision date; lower is better.

| Method | Pinball loss | Coverage |
|---|---:|---:|
| Previous week's cancellations | £4,950.14 | 53.55% |
| Constant train-Q80 | £2,483.98 | 76.13% |
| Frozen 50:50 blend | £2,455.68 | 87.74% |

The blend's loss is **£28.30 lower** than the constant rule, but the paired 95% interval **[−£484.27, +£707.08]** includes zero: **an advantage is not established**. Mean shortfall falls from £1,340.02 to £462.28 while mean unused reserve rises from £7,059.82 to £10,429.27. We did not select a new model after seeing test outcomes. [Full results and provenance](../artifacts/final_results.md).

**Failure and limits.** On **18 January 2011, a validation example**, the model reserved £24,050.42 against £81,851.42 in cancellations, leaving a £57,801.00 shortfall. Recent history failed to anticipate the spike; its cause is not established. One retailer does not establish transfer to other shops. The source records invoice cancellations, not actual refund-payment dates, cash balances or purchasing costs. The 4:1 cost ratio is an assumption, not measured savings. Next, we would test the decision against an actual refund-payment ledger.

**This project is a prototype and is not financial advice.**

**Sources.** Daqing Chen, [Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii), UCI, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Libraries: [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [scikit-learn](https://scikit-learn.org/), [SciPy](https://scipy.org/), [python-calamine](https://github.com/dimastbk/python-calamine). AI assistance: [Codex](https://openai.com/codex/) for implementation/evaluation and editing; [GLM via ZCode](https://zcode.z.ai/en/docs/welcome) supplied text/script drafts adapted for this submission. [Code and demo instructions](../README.md).

Before submitting, enter every contributor's name, email and school in the form, confirm the actual contributions and AI tools used, and check that both code and this write-up open without signing in.
