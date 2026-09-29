"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { ErrorBox, errorText, formatDate, Loading, RequireAuth } from "@/components/ui";
import {
  ApiError,
  createMatterNote,
  createMatterTask,
  deleteMatter,
  deleteMatterFile,
  deleteMatterNote,
  deleteMatterTask,
  getMatter,
  getMatterFileUrl,
  listMatterFiles,
  listMatterNotes,
  listMatterTasks,
  Matter,
  MATTER_FILE_MAX_BYTES,
  MatterFile,
  MatterNote,
  MatterTask,
  updateMatter,
  updateMatterTask,
  uploadMatterFile,
} from "@/lib/api";
import { useLang } from "@/lib/LangContext";

type Tab = "overview" | "notes" | "tasks" | "files";

export default function MatterDetailPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div className="page">
      <div className="content">
        <MatterBackLink />
        <RequireAuth>{(session) => <MatterDetail id={id} token={session.access_token} />}</RequireAuth>
      </div>
    </div>
  );
}

function MatterBackLink() {
  const { t } = useLang();
  return (
    <Link className="back-link" href="/matters">
      {t.mattersBack}
    </Link>
  );
}

function MatterDetail({ id, token }: { id: string; token: string }) {
  const { t } = useLang();
  const [matter, setMatter] = useState<Matter | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);
  const [tab, setTab] = useState<Tab>("overview");

  const load = useCallback(() => {
    setError(null);
    getMatter(token, id)
      .then(setMatter)
      .catch((e) => setError({ e }));
  }, [token, id]);
  useEffect(load, [load]);

  if (error) {
    if (error.e instanceof ApiError && error.e.status === 404) return <div className="notice">{t.mattersNotFound}</div>;
    return <ErrorBox message={errorText(error.e, t)} onRetry={load} />;
  }
  if (!matter) return <Loading />;

  const tabs: [Tab, string][] = [
    ["overview", t.tabOverview],
    ["notes", t.tabNotes],
    ["tasks", t.tabTasks],
    ["files", t.tabFiles],
  ];

  return (
    <>
      <div className="row row-between">
        <h2 style={{ overflowWrap: "anywhere" }}>{matter.client_name}</h2>
        <span className={`pill ${matter.status === "closed" ? "" : "ok"}`}>
          {matter.status === "closed" ? t.mattersStatusClosed : t.mattersStatusOpen}
        </span>
      </div>

      <div className="tabs" role="tablist">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            className={`tab${tab === key ? " active" : ""}`}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "overview" && <OverviewTab matter={matter} token={token} onChange={setMatter} />}
      {tab === "notes" && <NotesTab matterId={id} token={token} />}
      {tab === "tasks" && <TasksTab matterId={id} token={token} />}
      {tab === "files" && <FilesTab matterId={id} token={token} />}
    </>
  );
}

// ---------------------------------------------------------------- overview

function OverviewTab({ matter, token, onChange }: { matter: Matter; token: string; onChange: (m: Matter) => void }) {
  const { lang, t } = useLang();
  const router = useRouter();
  const [name, setName] = useState(matter.client_name);
  const [facts, setFacts] = useState(matter.facts ?? "");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: "success" | "error"; text: string } | null>(null);

  async function save(patch: { client_name?: string; facts?: string; status?: "open" | "closed" }) {
    setBusy(true);
    setMsg(null);
    try {
      const m = await updateMatter(token, matter.id, patch);
      onChange(m);
      setMsg({ kind: "success", text: t.saveChanges + " ✓" });
    } catch (e) {
      setMsg({ kind: "error", text: errorText(e, t) });
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm(t.mattersDeleteConfirm)) return;
    setBusy(true);
    try {
      await deleteMatter(token, matter.id);
      router.push("/matters");
    } catch (e) {
      setMsg({ kind: "error", text: errorText(e, t) });
      setBusy(false);
    }
  }

  const dirty = name.trim() !== matter.client_name || facts !== (matter.facts ?? "");

  return (
    <div className="card form">
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (name.trim()) save({ client_name: name.trim(), facts });
        }}
      >
        <div className="field">
          <label htmlFor="o-name">{t.mattersClientName}</label>
          <input id="o-name" className="input" value={name} maxLength={200} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div className="field">
          <label htmlFor="o-facts">{t.mattersFacts}</label>
          <textarea id="o-facts" className="textarea" style={{ minHeight: 140 }} value={facts} onChange={(e) => setFacts(e.target.value)} />
        </div>
        <div className="muted">
          {t.mattersCreated} {formatDate(matter.created_at, lang)} · {t.mattersUpdated} {formatDate(matter.updated_at, lang)}
        </div>
        {msg && (
          <div className={`notice ${msg.kind}`} role={msg.kind === "error" ? "alert" : "status"}>
            {msg.text}
          </div>
        )}
        <div className="row">
          <button className="btn btn-primary" type="submit" disabled={busy || !dirty || !name.trim()}>
            {busy ? t.saving : t.saveChanges}
          </button>
          <button
            className="btn"
            type="button"
            disabled={busy}
            onClick={() => save({ status: matter.status === "closed" ? "open" : "closed" })}
          >
            {matter.status === "closed" ? t.mattersReopen : t.mattersClose}
          </button>
          <button className="btn btn-danger" type="button" disabled={busy} onClick={handleDelete}>
            {t.mattersDelete}
          </button>
        </div>
      </form>
    </div>
  );
}

// ------------------------------------------------------------------- notes

function NotesTab({ matterId, token }: { matterId: string; token: string }) {
  const { lang, t } = useLang();
  const [notes, setNotes] = useState<MatterNote[] | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<{ e: unknown } | null>(null);

  const load = useCallback(() => {
    setError(null);
    listMatterNotes(token, matterId)
      .then(setNotes)
      .catch((e) => setError({ e }));
  }, [token, matterId]);
  useEffect(load, [load]);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    setBusy(true);
    setActionError(null);
    try {
      const n = await createMatterNote(token, matterId, body.trim());
      setNotes((prev) => [n, ...(prev ?? [])]);
      setBody("");
    } catch (err) {
      setActionError({ e: err });
    } finally {
      setBusy(false);
    }
  }

  async function remove(n: MatterNote) {
    if (!window.confirm(t.notesDeleteConfirm)) return;
    try {
      await deleteMatterNote(token, matterId, n.id);
      setNotes((prev) => prev?.filter((x) => x.id !== n.id) ?? null);
    } catch (err) {
      setActionError({ e: err });
    }
  }

  return (
    <>
      <form className="card form" onSubmit={add}>
        <div className="field">
          <label htmlFor="note-body">{t.tabNotes}</label>
          <textarea id="note-body" className="textarea" value={body} maxLength={10000} placeholder={t.notesPlaceholder} onChange={(e) => setBody(e.target.value)} />
        </div>
        <div>
          <button className="btn btn-primary" type="submit" disabled={busy || !body.trim()}>
            {busy ? t.saving : t.notesAdd}
          </button>
        </div>
      </form>
      {actionError && <ErrorBox message={errorText(actionError.e, t)} />}
      {error && <ErrorBox message={errorText(error.e, t)} onRetry={load} />}
      {!error && notes === null && <Loading />}
      {notes && notes.length === 0 && <div className="muted">{t.notesEmpty}</div>}
      {notes && notes.length > 0 && (
        <ul className="list">
          {notes.map((n) => (
            <li className="list-item" key={n.id} style={{ alignItems: "flex-start" }}>
              <div className="grow">
                <div className="pre">{n.body}</div>
                <div className="muted" style={{ marginTop: 4 }}>
                  {formatDate(n.created_at, lang)}
                </div>
              </div>
              <button className="btn btn-small btn-danger" onClick={() => remove(n)}>
                {t.remove}
              </button>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

// ------------------------------------------------------------------- tasks

function todayIso(): string {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mm}-${dd}`;
}

function TasksTab({ matterId, token }: { matterId: string; token: string }) {
  const { t } = useLang();
  const [tasks, setTasks] = useState<MatterTask[] | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<{ e: unknown } | null>(null);

  const load = useCallback(() => {
    setError(null);
    listMatterTasks(token, matterId)
      .then(setTasks)
      .catch((e) => setError({ e }));
  }, [token, matterId]);
  useEffect(load, [load]);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setBusy(true);
    setActionError(null);
    try {
      const task = await createMatterTask(token, matterId, { title: title.trim(), due_date: due || null });
      setTasks((prev) => [...(prev ?? []), task]);
      setTitle("");
      setDue("");
    } catch (err) {
      setActionError({ e: err });
    } finally {
      setBusy(false);
    }
  }

  async function patch(task: MatterTask, p: { done?: boolean; due_date?: string }) {
    setActionError(null);
    // show the change straight away (a checkbox that waits for the server feels broken), undo on failure
    setTasks((prev) => prev?.map((x) => (x.id === task.id ? { ...x, ...p } : x)) ?? null);
    try {
      const updated = await updateMatterTask(token, matterId, task.id, p);
      setTasks((prev) => prev?.map((x) => (x.id === task.id ? updated : x)) ?? null);
    } catch (err) {
      setTasks((prev) => prev?.map((x) => (x.id === task.id ? task : x)) ?? null);
      setActionError({ e: err });
    }
  }

  async function remove(task: MatterTask) {
    if (!window.confirm(t.tasksDeleteConfirm)) return;
    try {
      await deleteMatterTask(token, matterId, task.id);
      setTasks((prev) => prev?.filter((x) => x.id !== task.id) ?? null);
    } catch (err) {
      setActionError({ e: err });
    }
  }

  const today = todayIso();
  const sorted = tasks
    ? [...tasks].sort((a, b) => {
        if (a.done !== b.done) return a.done ? 1 : -1;
        return (a.due_date || "9999").localeCompare(b.due_date || "9999");
      })
    : null;

  return (
    <>
      <form className="card form" onSubmit={add}>
        <div className="field">
          <label htmlFor="task-title">{t.tasksAdd}</label>
          <input id="task-title" className="input" value={title} maxLength={500} placeholder={t.tasksPlaceholder} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="task-due">
            {t.tasksDue} <span className="muted">({t.optional})</span>
          </label>
          <input id="task-due" className="input" type="date" value={due} onChange={(e) => setDue(e.target.value)} />
        </div>
        <div>
          <button className="btn btn-primary" type="submit" disabled={busy || !title.trim()}>
            {busy ? t.saving : t.tasksAdd}
          </button>
        </div>
      </form>
      {actionError && <ErrorBox message={errorText(actionError.e, t)} />}
      {error && <ErrorBox message={errorText(error.e, t)} onRetry={load} />}
      {!error && sorted === null && <Loading />}
      {sorted && sorted.length === 0 && <div className="muted">{t.tasksEmpty}</div>}
      {sorted && sorted.length > 0 && (
        <ul className="list">
          {sorted.map((task) => {
            const overdue = !task.done && !!task.due_date && task.due_date < today;
            return (
              <li className="list-item" key={task.id}>
                <label className="check grow">
                  <input type="checkbox" checked={task.done} onChange={(e) => patch(task, { done: e.target.checked })} />
                  <span style={{ textDecoration: task.done ? "line-through" : "none", opacity: task.done ? 0.6 : 1 }}>{task.title}</span>
                </label>
                <div className="row">
                  {overdue && <span className="pill bad">{t.tasksOverdue}</span>}
                  <input
                    className="input"
                    style={{ width: 150 }}
                    type="date"
                    aria-label={t.tasksDue}
                    value={task.due_date ? task.due_date.slice(0, 10) : ""}
                    onChange={(e) => e.target.value && patch(task, { due_date: e.target.value })}
                  />
                  <button className="btn btn-small btn-danger" onClick={() => remove(task)}>
                    {t.remove}
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}

// ------------------------------------------------------------------- files

function formatSize(n: number | null): string {
  if (n == null) return "";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

function FilesTab({ matterId, token }: { matterId: string; token: string }) {
  const { lang, t } = useLang();
  const [files, setFiles] = useState<MatterFile[] | null>(null);
  const [error, setError] = useState<{ e: unknown } | null>(null);
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState<{ kind: "error" | "warn"; text: string } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const load = useCallback(() => {
    setError(null);
    listMatterFiles(token, matterId)
      .then(setFiles)
      .catch((e) => setError({ e }));
  }, [token, matterId]);
  useEffect(load, [load]);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setMsg(null);
    // check the size here first: no point sending 100 MB just to be told 413
    if (file.size > MATTER_FILE_MAX_BYTES) {
      setMsg({ kind: "warn", text: t.filesTooBig });
      if (inputRef.current) inputRef.current.value = "";
      return;
    }
    setUploading(true);
    try {
      const f = await uploadMatterFile(token, matterId, file);
      setFiles((prev) => [f, ...(prev ?? [])]);
    } catch (err) {
      setMsg({ kind: "error", text: err instanceof ApiError && err.status === 413 ? t.filesTooBig : errorText(err, t) });
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function download(f: MatterFile) {
    setMsg(null);
    try {
      const url = await getMatterFileUrl(token, matterId, f.id);
      const a = document.createElement("a");
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.download = f.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      setMsg({ kind: "error", text: errorText(err, t) });
    }
  }

  async function remove(f: MatterFile) {
    if (!window.confirm(t.filesDeleteConfirm)) return;
    try {
      await deleteMatterFile(token, matterId, f.id);
      setFiles((prev) => prev?.filter((x) => x.id !== f.id) ?? null);
    } catch (err) {
      setMsg({ kind: "error", text: errorText(err, t) });
    }
  }

  return (
    <>
      <div className="card form">
        <div className="field">
          <label htmlFor="file-input">{t.filesChoose}</label>
          <input id="file-input" ref={inputRef} className="input" type="file" disabled={uploading} onChange={handleFile} />
        </div>
        {uploading && <div className="muted" role="status">{t.filesUploading}</div>}
      </div>
      {msg && (
        <div className={`notice ${msg.kind}`} role="alert">
          {msg.text}
        </div>
      )}
      {error && <ErrorBox message={errorText(error.e, t)} onRetry={load} />}
      {!error && files === null && <Loading />}
      {files && files.length === 0 && <div className="muted">{t.filesEmpty}</div>}
      {files && files.length > 0 && (
        <ul className="list">
          {files.map((f) => (
            <li className="list-item" key={f.id}>
              <div className="grow">
                <div className="card-title">{f.filename}</div>
                <div className="muted">
                  {formatSize(f.size_bytes)} {formatSize(f.size_bytes) && "· "}
                  {formatDate(f.created_at, lang)}
                </div>
              </div>
              <div className="row">
                <button className="btn btn-small" onClick={() => download(f)}>
                  {t.filesDownload}
                </button>
                <button className="btn btn-small btn-danger" onClick={() => remove(f)}>
                  {t.remove}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
