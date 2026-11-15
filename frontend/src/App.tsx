import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import {
  ArrowDownToLine,
  ArrowRight,
  BarChart3,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleAlert,
  CircleCheck,
  FileSpreadsheet,
  FileUp,
  FlaskConical,
  LayoutDashboard,
  ListFilter,
  LoaderCircle,
  Search,
  Shield,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
} from "lucide-react";
import { ApiError, downloadBlob, request } from "./api";
import { filterQueue, queueCSV } from "./review";
import type { QueueFilter } from "./review";
import type { Analysis, Health, Model, ReviewItem, Source } from "./types";

type Page = "overview" | "analyze" | "queue" | "research";
const pages: { id: Page; label: string; icon: typeof Shield }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "analyze", label: "Analyze transactions", icon: FileUp },
  { id: "queue", label: "Review queue", icon: ListFilter },
  { id: "research", label: "Model evidence", icon: FlaskConical },
];
const number = (n: number) => n.toLocaleString("en-US");
const amount = (n: number) =>
  n.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
const percent = (n: number, digits = 2) => `${(n * 100).toFixed(digits)}%`;
const disclaimer = "This project is a prototype and is not financial advice.";
const pageFromHash = (): Page =>
  pages.find((p) => `#${p.id}` === window.location.hash)?.id || "overview";

function Alert({
  children,
  error = false,
}: {
  children: ReactNode;
  error?: boolean;
}) {
  return (
    <div
      className={`alert ${error ? "error" : ""}`}
      role={error ? "alert" : undefined}
    >
      <CircleAlert size={18} />
      <div>{children}</div>
    </div>
  );
}

function Comparison({
  model,
  compact = false,
}: {
  model: Model;
  compact?: boolean;
}) {
  const test = model.benchmark.test,
    baseline = model.baselines.amount;
  return (
    <section
      className={`comparison ${compact ? "compact" : ""}`}
      aria-label="Historical benchmark comparison"
    >
      <div className="section-heading">
        <div>
          <span className="eyebrow">A fixed review budget</span>
          <h3>More relevant cases. Same workload.</h3>
        </div>
        <span className="tag">1,000 reviews</span>
      </div>
      <p>
        Fraud-labeled transactions in the top 1,000, on a historical synthetic
        benchmark.
      </p>
      <div className="bar-row">
        <div>
          <strong>AuditLens model</strong>
          <b>
            {number(test.positives_at_1000)} <small>/ 1,000</small>
          </b>
        </div>
        <div className="bar-track">
          <span style={{ width: `${test.positives_at_1000 / 10}%` }} />
        </div>
      </div>
      <div className="bar-row baseline">
        <div>
          <strong>Amount baseline</strong>
          <b>
            {number(baseline.positives_at_1000)} <small>/ 1,000</small>
          </b>
        </div>
        <div className="bar-track">
          <span style={{ width: `${baseline.positives_at_1000 / 10}%` }} />
        </div>
      </div>
      <p className="fine-print">
        Historical evidence only. These are not results from your transactions.
      </p>
    </section>
  );
}

function FileDrop({
  id,
  title,
  description,
  file,
  onChange,
  onError,
  maxBytes,
  disabled,
}: {
  id: string;
  title: string;
  description: string;
  file: File | null;
  onChange: (f: File | null) => void;
  onError: (s: string) => void;
  maxBytes?: number;
  disabled: boolean;
}) {
  const [dragging, setDragging] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const choose = (files: FileList | null) => {
    if (disabled || !files?.length) return;
    if (files.length !== 1)
      return onError("Choose one file for each upload area.");
    const next = files[0];
    if (!/\.(csv|xlsx)$/i.test(next.name))
      return onError(
        "Choose a CSV or XLSX file. Other formats are not supported.",
      );
    if (!next.size)
      return onError(
        "This file is empty. Choose a file with transaction rows.",
      );
    if (maxBytes && next.size > maxBytes)
      return onError(
        `Each file must be no larger than ${number(maxBytes / 1024 / 1024)} MiB.`,
      );
    onError("");
    onChange(next);
  };
  return (
    <div className="file-field">
      <div className="file-label">
        <label htmlFor={id}>{title}</label>
        <span>{id === "history" ? "Optional, recommended" : "Required"}</span>
      </div>
      <p>{description}</p>
      <div
        className={`dropzone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          choose(e.dataTransfer.files);
        }}
      >
        <input
          ref={input}
          id={id}
          type="file"
          accept=".csv,.xlsx"
          disabled={disabled}
          onChange={(e) => {
            choose(e.target.files);
            e.target.value = "";
          }}
          className="sr-only"
        />
        {file ? (
          <>
            <div className="file-symbol">
              <FileSpreadsheet size={24} />
            </div>
            <strong className="filename">{file.name}</strong>
            <span>{number(file.size)} bytes</span>
            <div className="file-actions">
              <button
                type="button"
                className="text-button"
                disabled={disabled}
                onClick={() => input.current?.click()}
              >
                Replace file
              </button>
              <button
                type="button"
                className="text-button"
                disabled={disabled}
                aria-label={`Remove ${title.toLowerCase()}`}
                onClick={() => onChange(null)}
              >
                <X size={14} />
                Remove
              </button>
            </div>
          </>
        ) : (
          <>
            <Upload size={26} strokeWidth={1.5} />
            <strong>Drop your file here</strong>
            <span>
              or{" "}
              <button
                type="button"
                className="inline-button"
                disabled={disabled}
                onClick={() => input.current?.click()}
              >
                browse files
              </button>
            </span>
            <small>
              CSV or XLSX
              {maxBytes ? ` · up to ${maxBytes / 1024 / 1024} MiB` : ""}
            </small>
          </>
        )}
      </div>
    </div>
  );
}

function Detail({ item, close }: { item: ReviewItem; close: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const origin = document.activeElement;
    const dialog = ref.current;
    dialog?.showModal();
    return () => {
      dialog?.close();
      if (origin instanceof HTMLElement) origin.focus();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className="detail-dialog"
      onCancel={close}
      onClick={(e) => {
        if (e.target === e.currentTarget) close();
      }}
      aria-labelledby="detail-title"
    >
      <div className="dialog-head">
        <span className="eyebrow">Transaction details</span>
        <button
          className="icon-button"
          onClick={close}
          aria-label="Close transaction details"
        >
          <X size={20} />
        </button>
      </div>
      <h2 id="detail-title">{item.record_id}</h2>
      <p className="muted">Rank {item.rank} in this review queue</p>
      <div className="detail-score">
        <div>
          <span>Review priority score</span>
          <strong>{item.score.toFixed(6)}</strong>
        </div>
        <Shield size={28} />
        <p>An uncalibrated ranking score, not a fraud probability.</p>
      </div>
      <h3>Payment information</h3>
      <dl className="detail-fields">
        {[
          ["Customer ID", item.customer_id],
          ["Terminal ID", item.terminal_id],
          ["Timestamp (UTC)", item.timestamp.replace("T", " ")],
          ["Amount (source units)", amount(item.amount)],
          [
            "Research threshold",
            item.review_required
              ? "At or above frozen threshold"
              : "Below frozen threshold",
          ],
          ["Model version", item.model_version],
        ].map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <h3>Observed history</h3>
      <p className="muted">
        Statistics returned by the backend. These are not causal explanations or
        SHAP attributions.
      </p>
      {item.reasons.length ? (
        <ul className="reason-list">
          {item.reasons.map((reason, i) => (
            <li key={i}>{reason}</li>
          ))}
        </ul>
      ) : (
        <p>No observed-history explanation was returned.</p>
      )}
      {item.warnings.length > 0 && (
        <Alert>
          <strong>History & coverage</strong>
          <ul>
            {item.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </Alert>
      )}
      <p className="fine-print">
        {item.validation_status}. A queued transaction is a candidate for manual
        review, not proof of wrongdoing.
      </p>
    </dialog>
  );
}

export default function App() {
  const [page, setPage] = useState<Page>(pageFromHash);
  const [model, setModel] = useState<Model | null>(null);
  const [connection, setConnection] = useState<
    "checking" | "ready" | "unavailable"
  >("checking");
  const [connectionError, setConnectionError] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [transactions, setTransactions] = useState<File | null>(null);
  const [history, setHistory] = useState<File | null>(null);
  const [budget, setBudget] = useState("100");
  const [queueBudget, setQueueBudget] = useState("5");
  const [result, setResult] = useState<Analysis | null>(null);
  const [source, setSource] = useState<Source | null>(null);
  const [selected, setSelected] = useState<ReviewItem | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<QueueFilter>("all");
  const [queuePage, setQueuePage] = useState(1);
  const [notice, setNotice] = useState("");
  const heading = useRef<HTMLHeadingElement>(null);
  const navigating = useRef(false);
  const navigate = (next: Page) => {
    navigating.current = true;
    window.location.hash = next;
    setPage(next);
    setError("");
    setNotice("");
  };
  useEffect(() => {
    const change = () => {
      navigating.current = true;
      setPage(pageFromHash());
      setError("");
    };
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  useEffect(() => {
    if (navigating.current) {
      heading.current?.focus();
      window.scrollTo(0, 0);
      navigating.current = false;
    }
  }, [page]);
  const checkServer = useCallback(async () => {
    setConnection("checking");
    setConnectionError("");
    const [metadata, health] = await Promise.allSettled([
      request<Model>("/model"),
      request<Health>("/health"),
    ]);
    if (metadata.status === "fulfilled") setModel(metadata.value);
    const ready =
      metadata.status === "fulfilled" &&
      metadata.value.available &&
      health.status === "fulfilled" &&
      health.value.model_available;
    setConnection(ready ? "ready" : "unavailable");
    if (!ready)
      setConnectionError(
        metadata.status === "rejected"
          ? String(metadata.reason.message)
          : "The analysis model is unavailable. Start or restart the backend, then retry the connection.",
      );
  }, []);
  useEffect(() => {
    void checkServer();
  }, [checkServer]);

  const run = async (nextSource: Source, value: string) => {
    if (busy) return;
    setError("");
    setNotice("");
    if (!/^[0-9]{1,12}$/.test(value) || Number(value) < 1) {
      setError("Review budget must be a whole number from 1 to 999999999999.");
      return;
    }
    setBusy(true);
    try {
      let response: Analysis;
      if (nextSource.kind === "demo")
        response = await request<Analysis>("/demo/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ top_k: Number(value) }),
        });
      else {
        const form = new FormData();
        form.append("transactions", nextSource.transactions);
        if (nextSource.history) form.append("history", nextSource.history);
        form.append("top_k", String(Number(value)));
        response = await request<Analysis>("/analyze", {
          method: "POST",
          body: form,
        });
      }
      setResult(response);
      setSource(nextSource);
      setQueueBudget(String(response.top_k));
      setQuery("");
      setFilter("all");
      setQueuePage(1);
      setConnection("ready");
      navigate("queue");
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Analysis could not be completed. Please retry.",
      );
      if (e instanceof ApiError && (e.status === 503 || e.status === 0)) {
        setConnection("unavailable");
        setConnectionError(
          "The analysis server is unavailable. Retry the connection to check readiness.",
        );
      }
    } finally {
      setBusy(false);
    }
  };
  const template = async (name: string) => {
    try {
      const blob = await request<Blob>(`/templates/${name}.csv`);
      downloadBlob(blob, `${name}.csv`);
      setNotice(
        `${name === "history" ? "History" : "Transactions"} template downloaded.`,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Template download failed.");
    }
  };
  const exportQueue = () => {
    if (result) {
      downloadBlob(
        new Blob([queueCSV(result.operations)], {
          type: "text/csv;charset=utf-8;",
        }),
        "auditlens-review-queue.csv",
      );
      setNotice(
        `Exported all ${result.queue_count} queued transactions in rank order.`,
      );
    }
  };
  const filtered = result ? filterQueue(result.operations, query, filter) : [];
  const totalPages = Math.max(1, Math.ceil(filtered.length / 10));
  const currentPage = Math.min(queuePage, totalPages);
  const visible = filtered.slice((currentPage - 1) * 10, currentPage * 10);
  const title = pages.find((p) => p.id === page)!.label;
  const demoButton = (
    <button
      className="button primary"
      disabled={busy || connection !== "ready"}
      onClick={() => void run({ kind: "demo" }, "5")}
    >
      <Sparkles size={17} />
      Run live demo
      <ArrowRight size={16} />
    </button>
  );

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <a href="#overview" className="brand" aria-label="AuditLens AI home">
          <span className="brand-icon">
            <ShieldCheck size={25} />
          </span>
          <span>
            AuditLens<span className="brand-ai"> AI</span>
          </span>
        </a>
        <div className="workspace-name">
          <span className="workspace-avatar">A</span>
          <div>
            Review workspace<small>Research prototype</small>
          </div>
        </div>
        <nav aria-label="Main navigation">
          {pages.map(({ id, label, icon: Icon }) => (
            <a
              href={`#${id}`}
              key={id}
              className={page === id ? "active" : ""}
              aria-current={page === id ? "page" : undefined}
            >
              <Icon size={18} />
              <span>{label}</span>
              {id === "queue" && result && (
                <b className="nav-count">{number(result.queue_count)}</b>
              )}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <Shield size={23} />
          <strong>Human judgment comes first.</strong>
          <p>
            Behavioral signals help you decide what to review. You make the
            call.
          </p>
          <span className="sidebar-badge">
            <span />
            Research demo
          </span>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>{title}</strong>
          </div>
          <span className={`connection ${connection}`} role="status">
            <i />
            {connection === "ready"
              ? "Analysis server connected"
              : connection === "checking"
                ? "Connecting to server"
                : "Server unavailable"}
          </span>
        </header>
        <main id="main" tabIndex={-1}>
          {connectionError && (
            <div className="connection-banner">
              <Alert error>
                <strong>Analysis server unavailable.</strong> {connectionError}
                <button
                  className="text-button"
                  disabled={connection === "checking"}
                  onClick={() => void checkServer()}
                >
                  Retry connection
                </button>
              </Alert>
            </div>
          )}
          {error && <Alert error>{error}</Alert>}
          {busy && (
            <div className="loading-banner" role="status">
              <LoaderCircle className="spin" size={20} />
              <div>
                <strong>Analyzing behavioral history</strong>
                <span>
                  Running the model on the server. This may take a moment.
                </span>
              </div>
            </div>
          )}
          <div className="sr-only" role="status">
            {notice}
          </div>
          {notice && (
            <div className="notice">
              <CircleCheck size={16} />
              {notice}
            </div>
          )}

          {page === "overview" && (
            <>
              <section className="hero">
                <div className="hero-copy">
                  <span className="product-label">
                    <span />
                    Behavioral purchase review
                  </span>
                  <h1 ref={heading} tabIndex={-1}>
                    Spot suspicious purchases before they become costly.
                  </h1>
                  <p>
                    See the change behind the transaction. AuditLens analyzes
                    purchase history and prioritizes a focused queue for your
                    manual review.
                  </p>
                  <div className="hero-actions">
                    {demoButton}
                    <button
                      className="button secondary"
                      disabled={busy}
                      onClick={() => navigate("analyze")}
                    >
                      Analyze transactions
                    </button>
                  </div>
                  <div className="hero-foot">
                    <Check size={15} />
                    No account needed
                    <span />
                    No external AI service
                  </div>
                  <div className="mobile-workflow">
                    <span>Upload</span>
                    <ArrowRight size={12} />
                    <span>Behavioral analysis</span>
                    <ArrowRight size={12} />
                    <span>Review queue</span>
                  </div>
                </div>
                <div
                  className="workflow-visual"
                  aria-label="Upload, behavioral analysis, review queue"
                >
                  <div className="visual-heading">
                    <span className="lens-mark">
                      <Search size={25} />
                    </span>
                    <span>
                      A little context.
                      <br />
                      <strong>A clearer review queue.</strong>
                    </span>
                  </div>
                  <div className="flow-item">
                    <span className="flow-icon">
                      <FileSpreadsheet size={21} />
                    </span>
                    <div>
                      <strong>Upload</strong>
                      <small>Transactions + prior history</small>
                    </div>
                    <Check className="flow-check" size={16} />
                  </div>
                  <div className="flow-line" />
                  <div className="flow-item analysis-step">
                    <span className="flow-icon">
                      <BarChart3 size={21} />
                    </span>
                    <div>
                      <strong>Behavioral analysis</strong>
                      <small>Compare with past activity</small>
                    </div>
                    <div className="signal-bars">
                      <i />
                      <i />
                      <i />
                      <i />
                      <i />
                    </div>
                  </div>
                  <div className="flow-line" />
                  <div className="flow-item">
                    <span className="flow-icon">
                      <ListFilter size={21} />
                    </span>
                    <div>
                      <strong>Review queue</strong>
                      <small>Ranked to fit your budget</small>
                    </div>
                    <ArrowRight size={17} />
                  </div>
                  <p>
                    From individual payments to
                    <br />
                    patterns worth a closer look.
                  </p>
                </div>
              </section>
              <div className="overview-lower">
                {model ? (
                  <Comparison model={model} compact />
                ) : (
                  <section className="comparison">
                    <h3>Evidence, with its limits.</h3>
                    <p>
                      Connect to the backend to load the historical synthetic
                      benchmark.
                    </p>
                  </section>
                )}
                <section className="context-panel">
                  <span className="eyebrow">Built for a focused review</span>
                  <h3>Context makes the difference.</h3>
                  <p>
                    A large payment alone tells one story. A change from a
                    customer’s usual spending tells another.
                  </p>
                  <ul>
                    <li>
                      <CircleCheck size={17} />
                      Observed spending history
                    </li>
                    <li>
                      <CircleCheck size={17} />A review budget you control
                    </li>
                    <li>
                      <CircleCheck size={17} />
                      Clear signals, visible limitations
                    </li>
                  </ul>
                  <button
                    className="text-button"
                    onClick={() => navigate("research")}
                  >
                    Explore model evidence
                    <ArrowRight size={16} />
                  </button>
                </section>
              </div>
              <div className="research-note">
                <FlaskConical size={18} />
                <p>
                  A research prototype built on synthetic data. Scores
                  prioritize review; they are not fraud probabilities.
                  Effectiveness on real bank data has not been established.
                </p>
              </div>
            </>
          )}

          {page === "analyze" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">A new analysis</span>
                  <h1 ref={heading} tabIndex={-1}>
                    Bring the history into view.
                  </h1>
                  <p>
                    Upload purchases and preceding customer history to build
                    your review queue.
                  </p>
                </div>
              </div>
              <form
                onSubmit={(e: FormEvent) => {
                  e.preventDefault();
                  if (!transactions) {
                    setError(
                      "Choose a transactions file before running analysis.",
                    );
                    return;
                  }
                  void run({ kind: "upload", transactions, history }, budget);
                }}
              >
                <section className="upload-panel">
                  <div className="section-heading">
                    <h2>Transaction files</h2>
                    <span className="tag">
                      <Shield size={13} />
                      Processed in memory
                    </span>
                  </div>
                  <p className="muted">
                    Exact Handbook format only. Arbitrary bank statements are
                    not supported.
                  </p>
                  <div className="upload-grid">
                    <FileDrop
                      id="transactions"
                      title="Transactions to analyze"
                      description="The batch of purchases you want to review."
                      file={transactions}
                      onChange={setTransactions}
                      onError={setError}
                      maxBytes={model?.limits.max_file_bytes}
                      disabled={busy}
                    />
                    <FileDrop
                      id="history"
                      title="Prior customer history"
                      description="Same fields, with timestamps strictly before the batch."
                      file={history}
                      onChange={setHistory}
                      onError={setError}
                      maxBytes={model?.limits.max_file_bytes}
                      disabled={busy}
                    />
                  </div>
                  {!history && (
                    <Alert>
                      <strong>
                        History gives behavioral signals their context.
                      </strong>{" "}
                      Supply all relevant transactions from the preceding{" "}
                      {model?.history_requirements
                        .customer_pair_complete_calendar_days ?? 30}{" "}
                      complete calendar days (
                      {model?.history_requirements.terminal_days ?? 7} days for
                      terminal windows). Without it, analysis is accepted with
                      cold-start and incomplete-history warnings.
                    </Alert>
                  )}
                  <details className="format-details">
                    <summary>Required fields & file requirements</summary>
                    <div className="schema-fields">
                      {(
                        model?.input_schema.required ?? [
                          "record_id",
                          "timestamp",
                          "customer_id",
                          "terminal_id",
                          "amount",
                        ]
                      ).map((f) => (
                        <code key={f}>{f}</code>
                      ))}
                    </div>
                    <ul>
                      <li>
                        Use all five fields, with no extra columns. Record IDs
                        must be unique text; customer and terminal IDs must be
                        stable text. Keep leading zeros.
                      </li>
                      <li>
                        Timestamp: UTC wall time, e.g.{" "}
                        <code>2026-02-01T12:00:00</code>, without a timezone
                        suffix.
                      </li>
                      <li>
                        Amounts must be finite and nonnegative, in one
                        consistent currency or unit. The app does not infer a
                        currency.
                      </li>
                      <li>
                        CSV: UTF-8 and comma separated. XLSX: active worksheet,
                        text cells for IDs; no formulas, external links or
                        macros.
                      </li>
                      <li>
                        History IDs must not overlap the batch. All history
                        timestamps must be earlier than the earliest batch
                        timestamp. An empty history file is not accepted.
                      </li>
                      {model && (
                        <li>
                          Limits: {number(model.limits.max_transactions)} batch
                          rows; {number(model.limits.max_history)} history rows;{" "}
                          {number(model.limits.max_combined_rows)} combined.
                          Entire request up to{" "}
                          {model.limits.max_request_bytes / 1024 / 1024} MiB.
                        </li>
                      )}
                    </ul>
                  </details>
                  <div className="template-links">
                    <span>Start with a compatible example</span>
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => void template("transactions")}
                    >
                      <ArrowDownToLine size={15} />
                      Transactions CSV
                    </button>
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => void template("history")}
                    >
                      <ArrowDownToLine size={15} />
                      History CSV
                    </button>
                  </div>
                </section>
                <section className="budget-panel">
                  <div>
                    <h2>Set your review budget</h2>
                    <p>
                      Return the highest-ranked purchases, up to the number you
                      can review.
                    </p>
                  </div>
                  <label>
                    Maximum transactions
                    <input
                      aria-label="Review budget"
                      type="number"
                      min="1"
                      max="999999999999"
                      step="1"
                      required
                      value={budget}
                      disabled={busy}
                      onChange={(e) => setBudget(e.target.value)}
                    />
                  </label>
                  <button
                    type="submit"
                    className="button primary"
                    disabled={busy || connection !== "ready"}
                  >
                    {busy ? (
                      <LoaderCircle className="spin" size={17} />
                    ) : (
                      <BarChart3 size={17} />
                    )}
                    Run analysis
                  </button>
                </section>
              </form>
              <p className="privacy-note">
                <Shield size={16} />
                Files are processed in backend memory for this request. No
                uploaded transaction history is retained by the model.
              </p>
            </>
          )}

          {page === "queue" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">Your audit dashboard</span>
                  <h1 ref={heading} tabIndex={-1}>
                    A closer look, in the right order.
                  </h1>
                  <p>
                    {result
                      ? `${source?.kind === "demo" ? "Live demo" : "Uploaded files"} · Ranked by review priority, highest first.`
                      : "Run an analysis to see the purchases worth reviewing first."}
                  </p>
                </div>
                {result && (
                  <button
                    className="button secondary"
                    disabled={busy}
                    onClick={exportQueue}
                  >
                    <ArrowDownToLine size={16} />
                    Export queue CSV
                  </button>
                )}
              </div>
              {!result ? (
                <div className="empty-state">
                  <ListFilter size={35} />
                  <h2>Your review queue starts here.</h2>
                  <p>
                    Analyze your transactions or try the self-authored example
                    with real model inference.
                  </p>
                  <div className="hero-actions">
                    {demoButton}
                    <button
                      className="button secondary"
                      onClick={() => navigate("analyze")}
                    >
                      Analyze transactions
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <section className="run-stats" aria-label="Analysis summary">
                    {[
                      ["Transactions analyzed", number(result.analyzed_count)],
                      ["History records", number(result.history_count)],
                      ["Review queue size", number(result.queue_count)],
                      [
                        "Processing time",
                        `${result.processing_time_ms.toFixed(1)} ms`,
                      ],
                      ["Model version", result.model_version],
                    ].map(([label, value]) => (
                      <div key={label}>
                        <span>{label}</span>
                        <strong
                          className={
                            label === "Model version" ? "version-value" : ""
                          }
                        >
                          {value}
                        </strong>
                      </div>
                    ))}
                  </section>
                  {source?.kind === "demo" && (
                    <div className="demo-note">
                      <FlaskConical size={17} />
                      <span>
                        Self-authored synthetic example. Real inference, no
                        fraud labels or accuracy claim.
                      </span>
                    </div>
                  )}
                  <details className="coverage" open>
                    <summary>
                      <CircleAlert size={17} />
                      History & coverage warnings{" "}
                      <span>{result.warnings.length}</span>
                    </summary>
                    <ul>
                      {result.warnings.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </details>
                  <section className="queue-panel">
                    <div className="queue-heading">
                      <div>
                        <h2>
                          Review queue{" "}
                          <span className="count-badge">
                            {result.queue_count}
                          </span>
                        </h2>
                        <p>
                          Scores are review priorities, not fraud probabilities.
                          Amounts use source units.
                        </p>
                      </div>
                      <form
                        className="queue-budget"
                        onSubmit={(e) => {
                          e.preventDefault();
                          if (source) void run(source, queueBudget);
                        }}
                      >
                        <label htmlFor="queue-budget">Review budget</label>
                        <div>
                          <input
                            id="queue-budget"
                            type="number"
                            min="1"
                            max="999999999999"
                            step="1"
                            required
                            disabled={busy}
                            value={queueBudget}
                            onChange={(e) => setQueueBudget(e.target.value)}
                          />
                          <button
                            type="submit"
                            className="button small secondary"
                            disabled={busy}
                          >
                            Reanalyze
                          </button>
                        </div>
                        <small>
                          Applied: {number(result.top_k)} · reruns the full
                          batch
                        </small>
                      </form>
                    </div>
                    <div className="queue-toolbar">
                      <label className="search-field">
                        <Search size={17} />
                        <input
                          aria-label="Search review queue"
                          placeholder="Search transaction, customer or terminal…"
                          value={query}
                          onChange={(e) => {
                            setQuery(e.target.value);
                            setQueuePage(1);
                          }}
                        />
                      </label>
                      <label className="filter-label">
                        <ListFilter size={16} />
                        <select
                          aria-label="Filter review queue"
                          value={filter}
                          onChange={(e) => {
                            setFilter(e.target.value as QueueFilter);
                            setQueuePage(1);
                          }}
                        >
                          <option value="all">All queued transactions</option>
                          <option value="threshold">
                            At / above research threshold
                          </option>
                          <option value="cold">Cold-start warnings</option>
                        </select>
                      </label>
                    </div>
                    <p className="table-hint">
                      Scroll sideways to see amounts, priority scores and
                      observations.
                    </p>
                    <div
                      className="table-scroll"
                      tabIndex={0}
                      role="region"
                      aria-label="Ranked transactions table"
                    >
                      <table>
                        <thead>
                          <tr>
                            <th scope="col">
                              Rank <span aria-label="Ascending rank">↓</span>
                            </th>
                            <th scope="col">Transaction / customer</th>
                            <th scope="col">Timestamp (UTC)</th>
                            <th scope="col" className="numeric">
                              Amount
                            </th>
                            <th scope="col">Review priority</th>
                            <th scope="col">Observed history</th>
                            <th scope="col">
                              <span className="sr-only">Details</span>
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {visible.map((item) => (
                            <tr key={item.record_id}>
                              <td className="rank">
                                {String(item.rank).padStart(2, "0")}
                              </td>
                              <td>
                                <button
                                  className="record-button"
                                  onClick={() => setSelected(item)}
                                >
                                  {item.record_id}
                                </button>
                                <small>{item.customer_id}</small>
                              </td>
                              <td className="timestamp">
                                {item.timestamp.slice(0, 10)}
                                <small>{item.timestamp.slice(11)}</small>
                              </td>
                              <td className="numeric amount">
                                {amount(item.amount)}
                              </td>
                              <td>
                                <span
                                  className={`score ${item.review_required ? "above" : ""}`}
                                >
                                  {item.score.toFixed(4)}
                                </span>
                                <small>
                                  {item.review_required
                                    ? "Above research threshold"
                                    : "Below research threshold"}
                                </small>
                              </td>
                              <td className="observation">
                                <span>
                                  {item.reasons[0] || "No observation returned"}
                                </span>
                                {item.warnings.some((w) =>
                                  /cold start/i.test(w),
                                ) && (
                                  <small className="cold-label">
                                    Cold-start history
                                  </small>
                                )}
                              </td>
                              <td>
                                <button
                                  className="icon-button"
                                  aria-label={`View transaction ${item.record_id}`}
                                  onClick={() => setSelected(item)}
                                >
                                  <ChevronRight size={17} />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {!filtered.length && (
                      <div className="empty-state small-empty">
                        <Search size={25} />
                        <h3>
                          {result.queue_count
                            ? "No queued transactions match."
                            : "No transactions returned."}
                        </h3>
                        <p>
                          {result.queue_count
                            ? "Try another search or clear the filters."
                            : "The backend returned an empty review queue. Try a new analysis."}
                        </p>
                        {result.queue_count > 0 && (
                          <button
                            className="text-button"
                            onClick={() => {
                              setQuery("");
                              setFilter("all");
                              setQueuePage(1);
                            }}
                          >
                            Clear filters
                          </button>
                        )}
                      </div>
                    )}
                    <div className="table-footer">
                      <span>
                        {filtered.length
                          ? `${(currentPage - 1) * 10 + 1}–${Math.min(currentPage * 10, filtered.length)} of ${number(filtered.length)}`
                          : "0 results"}{" "}
                        · within the returned top-{result.top_k}
                      </span>
                      <div>
                        <button
                          className="icon-button"
                          aria-label="Previous page"
                          disabled={currentPage === 1}
                          onClick={() => setQueuePage(currentPage - 1)}
                        >
                          <ChevronLeft size={17} />
                        </button>
                        <span>
                          {currentPage} / {totalPages}
                        </span>
                        <button
                          className="icon-button"
                          aria-label="Next page"
                          disabled={currentPage === totalPages}
                          onClick={() => setQueuePage(currentPage + 1)}
                        >
                          <ChevronRight size={17} />
                        </button>
                      </div>
                    </div>
                  </section>
                  <p className="fine-print">
                    Filtering keeps original backend ranks. CSV export includes
                    the entire returned queue, independent of filters and
                    pagination. The research threshold is separate from your
                    top-K review budget.
                  </p>
                </>
              )}
            </>
          )}

          {page === "research" && (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">Research, in context</span>
                  <h1 ref={heading} tabIndex={-1}>
                    Evidence you can inspect.
                  </h1>
                  <p>
                    Historical synthetic benchmark. Never a performance claim
                    for your uploaded files.
                  </p>
                </div>
                <span className="tag">
                  <FlaskConical size={14} />
                  Research demo
                </span>
              </div>
              {!model ? (
                <div className="empty-state">
                  <h2>Model metadata is unavailable.</h2>
                  <p>
                    Connect to the backend to load actual benchmark results.
                  </p>
                  <button
                    className="button secondary"
                    disabled={connection === "checking"}
                    onClick={() => void checkServer()}
                  >
                    Retry connection
                  </button>
                </div>
              ) : (
                <>
                  <Comparison model={model} />
                  <section className="evidence-stats">
                    {[
                      [
                        "Average precision",
                        model.benchmark.test.average_precision.toFixed(4),
                        `${model.baselines.amount.average_precision.toFixed(4)} amount baseline`,
                      ],
                      [
                        "Precision",
                        percent(model.benchmark.test.precision),
                        "At the frozen research threshold",
                      ],
                      [
                        "Recall",
                        percent(model.benchmark.test.recall),
                        "At the frozen research threshold",
                      ],
                      [
                        "Precision@1,000",
                        percent(model.benchmark.test.precision_at_1000, 1),
                        "At a budget of 1,000 reviews",
                      ],
                    ].map(([label, value, note]) => (
                      <div key={label}>
                        <span>{label}</span>
                        <strong>{value}</strong>
                        <small>{note}</small>
                      </div>
                    ))}
                  </section>
                  <section className="study-panel">
                    <h2>What was evaluated</h2>
                    <div className="study-grid">
                      <div>
                        <strong>{number(model.benchmark.test.n)}</strong>
                        <span>Transactions in the historical test</span>
                      </div>
                      <div>
                        <strong>
                          {number(model.benchmark.test.positives)}
                        </strong>
                        <span>Fraud-labeled test transactions</span>
                      </div>
                    </div>
                    <dl className="split-dates">
                      {(["train", "validation", "test"] as const).map(
                        (split) => (
                          <div key={split}>
                            <dt>
                              {split === "train"
                                ? "Training"
                                : split === "test"
                                  ? "Test"
                                  : "Validation"}
                            </dt>
                            <dd>
                              {model.benchmark_provenance.split_periods?.[
                                split
                              ]?.replace("..", " — ") ||
                                "Not provided by backend"}
                            </dd>
                          </div>
                        ),
                      )}
                    </dl>
                    <p className="fine-print">
                      Precision and recall use the frozen validation-F1
                      threshold ({model.benchmark.test.threshold.toFixed(6)}).
                      Ranking policy:{" "}
                      {model.benchmark_provenance.ranking_policy}.
                    </p>
                  </section>
                  <section className="limitations-panel">
                    <div className="section-heading">
                      <h2>Where the model falls short</h2>
                      <CircleAlert size={22} />
                    </div>
                    <div className="failure-case">
                      <strong>
                        Random terminal compromise is largely missed.
                      </strong>
                      <p>
                        Scenario-2 recall at the frozen threshold:{" "}
                        {percent(
                          model.benchmark_provenance.terminal_compromise_recall,
                          4,
                        )}
                        . Behavioral review cannot reliably catch this failure
                        case.
                      </p>
                    </div>
                    <Alert>
                      <strong>The test is not a new, untouched holdout.</strong>{" "}
                      The Handbook test was recalculated after a
                      history-alignment bug was fixed. The September test had
                      already been opened before that correction.
                    </Alert>
                    <ul>
                      {model.limitations.map((limit, i) => (
                        <li key={i}>{limit}</li>
                      ))}
                    </ul>
                  </section>
                  <p className="fine-print">
                    Metadata source:{" "}
                    <code>{model.benchmark_provenance.source}</code> · Report
                    date: {model.benchmark_provenance.date} · Model:{" "}
                    {model.version}. No new research is run by this interface.
                  </p>
                </>
              )}
            </>
          )}
        </main>
        <footer>
          <span>{disclaimer}</span>
          <span>
            AuditLens AI <span className="footer-dot">·</span> Behavioral review
          </span>
        </footer>
      </div>
      {selected && (
        <Detail
          key={selected.record_id}
          item={selected}
          close={() => setSelected(null)}
        />
      )}
    </div>
  );
}
