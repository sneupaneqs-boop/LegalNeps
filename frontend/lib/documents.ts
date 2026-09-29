// Typed client for the contract-audit API (backend/app/routes/documents.py).
// Kept separate from lib/api.ts on purpose.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Bi = { en: string; ne: string };

export type ContractType = "employment" | "rent_lease" | "service_agreement" | "nda" | "sale_or_loan";

export const CONTRACT_TYPES: ContractType[] = ["employment", "rent_lease", "service_agreement", "nda", "sale_or_loan"];

export const CONTRACT_TYPE_LABELS: Record<ContractType, Bi> = {
  employment: { en: "Employment contract", ne: "रोजगार सम्झौता" },
  rent_lease: { en: "Rent / lease agreement", ne: "घर बहाल / भाडा सम्झौता" },
  service_agreement: { en: "Service / consultancy agreement", ne: "सेवा / परामर्श सम्झौता" },
  nda: { en: "Non-disclosure agreement (NDA)", ne: "गोपनीयता सम्झौता (एनडीए)" },
  sale_or_loan: { en: "Sale or loan agreement", ne: "बिक्री वा ऋण सम्झौता" },
};

export type FindingStatus = "issue" | "warning" | "missing" | "info" | "ok";
export const STATUS_ORDER: FindingStatus[] = ["issue", "warning", "missing", "info", "ok"];

export type Provision = {
  law_title_ne: string;
  section: string;
  slug: string;
  citation: string;
  citation_en: string;
  url?: string | null;
  status?: string | null;
};

export type Finding = {
  check_id: string;
  status: FindingStatus;
  severity: "issue" | "warning" | "info";
  // "statutory": the cited section itself requires/limits this.
  // "best_practice": the law leaves it to the parties; we only flag silence.
  basis: "statutory" | "best_practice";
  title: Bi;
  recommendation: Bi;
  clause_id?: string | null;
  clause_label?: string | null;
  quote?: string | null;
  facts: Record<string, number | string | boolean>;
  not_stated: boolean;
  provision: Provision;
};

export type AuditResult = {
  contract_type: ContractType;
  contract_type_title: Bi;
  detected_by: "user" | "keywords" | "llm";
  language: "en" | "ne";
  document_language: string;
  filename?: string | null;
  clause_count: number;
  truncated: boolean;
  summary: Partial<Record<FindingStatus, number>>;
  checks_run: number;
  checks_not_applicable: number;
  findings: Finding[];
  extracted_facts: { name: string; value: number | string | boolean | null; clause_id?: string | null }[];
  disclaimer: Bi;
  prompt_version: string;
  saved_file_id?: string | null;
  saved_to_matter: boolean;
};

export type ChecklistCheck = {
  id: string;
  title: Bi;
  severity: "issue" | "warning" | "info";
  basis: "statutory" | "best_practice";
  recommendation: Bi;
  provision: Provision;
  extract: string[];
};

export type ChecklistType = {
  contract_type: ContractType;
  title: Bi;
  checks: ChecklistCheck[];
  not_enforced: { id: string; title: Bi; reason: string }[];
};

export type MatterSummary = { id: string; client_name: string; status: string };

/** Error from the documents API. `code` and the bilingual messages come from
 * the server's `detail` object when it sent one (legacy font, scanned PDF...). */
export class DocumentsApiError extends Error {
  status: number;
  code?: string;
  messageNe?: string;

  constructor(status: number, message: string, code?: string, messageNe?: string) {
    super(message);
    this.status = status;
    this.code = code;
    this.messageNe = messageNe;
  }
}

async function toError(res: Response): Promise<DocumentsApiError> {
  let message = `Request failed with status ${res.status}`;
  let code: string | undefined;
  let messageNe: string | undefined;
  try {
    const body = await res.json();
    const d = body?.detail;
    if (typeof d === "string") message = d;
    else if (d && typeof d === "object") {
      message = d.message || message;
      code = d.code;
      messageNe = d.message_ne;
    }
  } catch {
    // non-JSON error body: keep the generic message
  }
  return new DocumentsApiError(res.status, message, code, messageNe);
}

const AUDIT_TIMEOUT_MS = 150_000; // the extraction call can take a minute on a long contract

export async function auditDocument(
  accessToken: string,
  file: File,
  opts: { contractType?: ContractType | "auto"; language: "en" | "ne"; matterId?: string }
): Promise<AuditResult> {
  const form = new FormData();
  form.append("file", file);
  if (opts.contractType && opts.contractType !== "auto") form.append("contract_type", opts.contractType);
  form.append("language", opts.language);
  if (opts.matterId) form.append("matter_id", opts.matterId);
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), AUDIT_TIMEOUT_MS);
  try {
    const res = await fetch(`${API_URL}/api/documents/audit`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` }, // no Content-Type: the browser sets the multipart boundary
      body: form,
      signal: ctrl.signal,
    });
    if (!res.ok) throw await toError(res);
    return res.json();
  } finally {
    clearTimeout(timer);
  }
}

export async function downloadAuditReport(
  accessToken: string,
  audit: AuditResult,
  language: "en" | "ne"
): Promise<Blob> {
  const res = await fetch(`${API_URL}/api/documents/audit/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify({ audit, language }),
  });
  if (!res.ok) throw await toError(res);
  return res.blob();
}

export async function getChecklists(): Promise<ChecklistType[]> {
  const res = await fetch(`${API_URL}/api/documents/checklists`, { next: { revalidate: 3600 } });
  if (!res.ok) throw await toError(res);
  return res.json();
}

export async function listMatters(accessToken: string): Promise<MatterSummary[]> {
  const res = await fetch(`${API_URL}/api/matters`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!res.ok) throw await toError(res);
  return res.json();
}
