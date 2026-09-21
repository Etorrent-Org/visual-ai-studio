import type {
  BootstrapData,
  Brief,
  DirectoryListing,
  Project,
  SettingsUpdate,
  SubmissionOutcome,
  ValidationReport,
} from "./types";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : "Erreur API");
    this.status = status;
    this.detail = detail;
  }
}

async function parseError(response: Response): Promise<never> {
  let detail: unknown = `Erreur HTTP ${response.status}`;
  try {
    const payload = await response.json();
    detail = payload.detail ?? detail;
  } catch {
    // Réponse non JSON : on conserve le message HTTP.
  }
  throw new ApiError(response.status, detail);
}

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) return parseError(response);
  return (await response.json()) as T;
}

export const api = {
  bootstrap: () => json<BootstrapData>("/api/bootstrap"),

  createProject: () =>
    json<Project>("/api/projects", {
      method: "POST",
      body: "{}",
    }),

  getProject: (projectId: string) => json<Project>(`/api/projects/${projectId}`),

  duplicateProject: (projectId: string) =>
    json<Project>(`/api/projects/${projectId}/duplicate`, {
      method: "POST",
      body: "{}",
    }),

  archiveProject: (projectId: string) =>
    json<Project>(`/api/projects/${projectId}/archive`, {
      method: "POST",
      body: "{}",
    }),

  saveBrief: (
    projectId: string,
    brief: Brief,
    confirmNewCollection = false,
  ) =>
    json<{ project: Project; prompt_invalidated: boolean }>(
      `/api/projects/${projectId}/brief`,
      {
        method: "PUT",
        body: JSON.stringify({
          brief,
          confirm_new_collection: confirmNewCollection,
        }),
      },
    ),

  preparePrompt: (
    projectId: string,
    brief: Brief,
    confirmNewCollection = false,
  ) =>
    json<Project>(`/api/projects/${projectId}/prompt`, {
      method: "POST",
      body: JSON.stringify({
        brief,
        confirm_new_collection: confirmNewCollection,
      }),
    }),

  markSent: (projectId: string) =>
    json<Project>(`/api/projects/${projectId}/mark-sent`, {
      method: "POST",
      body: "{}",
    }),

  uploadReference: async (projectId: string, file: File) => {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch(`/api/projects/${projectId}/reference`, {
      method: "POST",
      body,
    });
    if (!response.ok) return parseError(response);
    return (await response.json()) as { path: string; filename: string };
  },

  importArtifacts: async (projectId: string, files: File[]) => {
    const body = new FormData();
    files.forEach((file) => body.append("files", file, file.name));
    const response = await fetch(`/api/projects/${projectId}/artifacts`, {
      method: "POST",
      body,
    });
    if (!response.ok) return parseError(response);
    return (await response.json()) as ValidationReport;
  },

  getValidation: (projectId: string) =>
    json<ValidationReport>(`/api/projects/${projectId}/validation`),

  approve: (projectId: string, approved: boolean) =>
    json<{ project: Project; ready: boolean }>(`/api/projects/${projectId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved }),
    }),

  exportProject: async (projectId: string, approved: boolean) => {
    const response = await fetch(`/api/projects/${projectId}/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approved }),
    });
    if (!response.ok) return parseError(response);
    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") ?? "";
    const match = disposition.match(/filename="?([^";]+)"?/i);
    return { blob, filename: match?.[1] ?? "visual-ai-studio-export.zip" };
  },

  submit: (projectId: string, approved: boolean) =>
    json<SubmissionOutcome>(`/api/projects/${projectId}/submit`, {
      method: "POST",
      body: JSON.stringify({ approved }),
    }),

  browseStorage: (path?: string) =>
    json<DirectoryListing>(
      `/api/storage/directories${path ? `?path=${encodeURIComponent(path)}` : ""}`,
    ),

  saveSettings: (settings: SettingsUpdate) =>
    json<{ projects_dir: string; settings: BootstrapData["settings"] }>("/api/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    }),

  testWebhook: () =>
    json<SubmissionOutcome>("/api/settings/test-webhook", {
      method: "POST",
      body: "{}",
    }),
};
