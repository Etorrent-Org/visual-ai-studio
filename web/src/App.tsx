import {
  Archive,
  ArrowLeft,
  Check,
  ChevronLeft,
  ChevronRight,
  Clipboard,
  Copy,
  Download,
  ExternalLink,
  FileArchive,
  FileImage,
  Folder,
  FolderOpen,
  Image as ImageIcon,
  KeyRound,
  Layers3,
  Link2,
  Minus,
  Palette,
  PlugZap,
  Plus,
  Search,
  Send,
  Settings,
  SlidersHorizontal,
  Sparkles,
  Timer,
  Upload,
  WandSparkles,
  X,
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import {
  type ChangeEvent,
  type DragEvent,
  type ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { ApiError, api } from "./api";
import type {
  BootstrapData,
  Brief,
  DirectoryListing,
  Project,
  ProjectStatus,
  SubmissionOutcome,
  ValidationReport,
} from "./types";

type View = "projects" | "brief" | "prompt" | "validation" | "export" | "settings";

type ConfirmState = {
  title: string;
  body: ReactNode;
  confirmLabel: string;
  danger?: boolean;
  action: () => Promise<void> | void;
};

type ToastState = {
  tone: "success" | "warning" | "error" | "info";
  message: string;
};

const emptyValidation: ValidationReport = {
  artifacts: [],
  issues: [],
  automatic_checks_passed: false,
  ready: false,
};

const advancedFields: Array<[keyof Brief, string]> = [
  ["intent", "Objectif"],
  ["subject", "Sujet principal"],
  ["setting", "Décor"],
  ["ambience", "Ambiance"],
  ["palette", "Palette"],
  ["lighting", "Lumière"],
  ["materials", "Matières"],
  ["composition", "Composition"],
  ["detail_level", "Niveau de détail"],
  ["required_elements", "Éléments obligatoires"],
  ["forbidden_elements", "Éléments interdits"],
  ["reference_note", "Note de référence"],
];

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (typeof error.detail === "string") return error.detail;
    if (error.detail && typeof error.detail === "object" && "message" in error.detail) {
      return String((error.detail as { message: unknown }).message);
    }
  }
  if (error instanceof Error) return error.message;
  return "Une erreur inattendue est survenue.";
}

function isSimilarCollectionError(error: unknown): error is ApiError {
  return (
    error instanceof ApiError &&
    error.status === 409 &&
    typeof error.detail === "object" &&
    error.detail !== null &&
    "code" in error.detail &&
    (error.detail as { code: unknown }).code === "similar_collection"
  );
}

function projectDate(value: string): string {
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusClass(status: ProjectStatus): string {
  if (status === "Validé") return "status status--valid";
  if (status === "Archivé") return "status status--archived";
  return "status status--brief";
}

function sortProjects(projects: Project[]): Project[] {
  return [...projects].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
  );
}

function IconButton({
  children,
  onClick,
  title,
  disabled,
}: {
  children: ReactNode;
  onClick: () => void;
  title: string;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      className="icon-button"
      onClick={onClick}
      title={title}
      aria-label={title}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

function PageTitle({
  eyebrow,
  title,
  subtitle,
  actions,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  actions?: ReactNode;
}) {
  return (
    <div className="page-title-row">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p className="page-subtitle">{subtitle}</p>
      </div>
      {actions ? <div className="page-actions">{actions}</div> : null}
    </div>
  );
}

function WorkflowRail({ view }: { view: View }) {
  const steps: Array<{ key: View; label: string; icon: ReactNode }> = [
    { key: "brief", label: "Brief", icon: <SlidersHorizontal size={17} /> },
    { key: "prompt", label: "Studio Visuel", icon: <WandSparkles size={17} /> },
    { key: "validation", label: "Validation", icon: <ImageIcon size={17} /> },
    { key: "export", label: "Export", icon: <Send size={17} /> },
  ];
  const current = Math.max(0, steps.findIndex((step) => step.key === view));

  return (
    <div className="workflow-rail" aria-label="Étapes du projet">
      {steps.map((step, index) => (
        <div
          className={`workflow-step ${index <= current ? "workflow-step--active" : ""}`}
          key={step.key}
        >
          <span className="workflow-step__icon">{step.icon}</span>
          <span>{step.label}</span>
          {index < steps.length - 1 ? <i /> : null}
        </div>
      ))}
    </div>
  );
}

function ConfirmModal({
  state,
  onClose,
}: {
  state: ConfirmState | null;
  onClose: () => void;
}) {
  if (!state) return null;
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="modal"
        role="dialog"
        aria-modal="true"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal__head">
          <h2>{state.title}</h2>
          <IconButton onClick={onClose} title="Fermer">
            <X size={18} />
          </IconButton>
        </div>
        <div className="modal__body">{state.body}</div>
        <div className="modal__actions">
          <button type="button" className="button button--ghost" onClick={onClose}>
            Annuler
          </button>
          <button
            type="button"
            className={`button ${state.danger ? "button--danger" : "button--primary"}`}
            onClick={async () => {
              const action = state.action;
              onClose();
              await action();
            }}
          >
            {state.confirmLabel}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function StorageModal({
  listing,
  busy,
  onBrowse,
  onChoose,
  onClose,
}: {
  listing: DirectoryListing | null;
  busy: boolean;
  onBrowse: (path: string) => Promise<void>;
  onChoose: (path: string) => void;
  onClose: () => void;
}) {
  if (!listing) return null;
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.97, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="modal modal--folder"
        role="dialog"
        aria-modal="true"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal__head">
          <div>
            <div className="eyebrow">Volume Docker</div>
            <h2>Choisir le dossier des projets</h2>
          </div>
          <IconButton onClick={onClose} title="Fermer">
            <X size={18} />
          </IconButton>
        </div>
        <div className="folder-current">
          <FolderOpen size={18} />
          <span>{listing.current}</span>
        </div>
        <div className="folder-grid">
          {listing.current !== listing.root ? (
            <button
              type="button"
              className="folder-card folder-card--parent"
              onClick={() => void onBrowse(listing.parent)}
              disabled={busy}
            >
              <ChevronLeft size={20} />
              <span>Dossier parent</span>
            </button>
          ) : null}
          {listing.children.map((child) => (
            <button
              type="button"
              className="folder-card"
              key={child.path}
              onClick={() => void onBrowse(child.path)}
              disabled={busy}
            >
              <Folder size={22} />
              <span>{child.name}</span>
              <ChevronRight size={17} />
            </button>
          ))}
          {!listing.children.length && listing.current === listing.root ? (
            <div className="empty-note">Aucun sous-dossier disponible.</div>
          ) : null}
        </div>
        <div className="modal__actions">
          <button type="button" className="button button--ghost" onClick={onClose}>
            Annuler
          </button>
          <button
            type="button"
            className="button button--primary"
            onClick={() => onChoose(listing.current)}
          >
            Utiliser ce dossier
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default function App() {
  const [bootstrap, setBootstrap] = useState<BootstrapData | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [brief, setBrief] = useState<Brief | null>(null);
  const [view, setView] = useState<View>("projects");
  const [validation, setValidation] = useState<ValidationReport>(emptyValidation);
  const [approved, setApproved] = useState(false);
  const [submission, setSubmission] = useState<SubmissionOutcome | null>(null);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<ToastState | null>(null);
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);
  const [storage, setStorage] = useState<DirectoryListing | null>(null);
  const [storageBusy, setStorageBusy] = useState(false);
  const [settingsDir, setSettingsDir] = useState("");
  const [webhookUrl, setWebhookUrl] = useState("");
  const [authHeaderName, setAuthHeaderName] = useState("X-Visual-AI-Token");
  const [webhookSecret, setWebhookSecret] = useState("");
  const [webhookSecretConfigured, setWebhookSecretConfigured] = useState(false);
  const [timeoutSeconds, setTimeoutSeconds] = useState(300);
  const [connectionTest, setConnectionTest] = useState<SubmissionOutcome | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"" | ProjectStatus>("");
  const [collectionHint, setCollectionHint] = useState<string[]>([]);
  const initialBrief = useRef(true);
  const fileInput = useRef<HTMLInputElement>(null);
  const folderInput = useRef<HTMLInputElement>(null);
  const referenceInput = useRef<HTMLInputElement>(null);

  const showToast = (tone: ToastState["tone"], message: string) => {
    setToast({ tone, message });
  };

  const applyBootstrap = (data: BootstrapData) => {
    setBootstrap(data);
    setProjects(sortProjects(data.projects));
    setSettingsDir(data.settings.projects_dir);
    setWebhookUrl(data.settings.webhook_url);
    setAuthHeaderName(data.settings.auth_header_name);
    setWebhookSecretConfigured(data.settings.webhook_secret_configured);
    setTimeoutSeconds(data.settings.timeout_seconds);
  };

  useEffect(() => {
    void (async () => {
      try {
        const data = await api.bootstrap();
        applyBootstrap(data);
      } catch (error) {
        showToast("error", errorMessage(error));
      }
    })();
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 4200);
    return () => window.clearTimeout(timer);
  }, [toast]);

  useEffect(() => {
    const input = folderInput.current;
    if (input) input.setAttribute("webkitdirectory", "");
  }, [view]);

  const replaceProject = (project: Project) => {
    setProjects((existing) => {
      const rest = existing.filter((item) => item.id !== project.id);
      return sortProjects([project, ...rest]);
    });
    if (currentProject?.id === project.id) setCurrentProject(project);
  };

  const refreshCatalog = async () => {
    const data = await api.bootstrap();
    applyBootstrap(data);
  };

  useEffect(() => {
    if (!currentProject || !brief || view !== "brief") return;
    if (initialBrief.current) {
      initialBrief.current = false;
      return;
    }
    const timer = window.setTimeout(() => {
      void api
        .saveBrief(currentProject.id, brief)
        .then(({ project }) => {
          replaceProject(project);
          setCollectionHint([]);
        })
        .catch((error) => {
          if (isSimilarCollectionError(error)) {
            const detail = error.detail as { similar?: string[] };
            setCollectionHint(detail.similar ?? []);
            return;
          }
          showToast("warning", `Autosauvegarde : ${errorMessage(error)}`);
        });
    }, 800);
    return () => window.clearTimeout(timer);
  }, [brief, currentProject?.id, view]);

  const filteredProjects = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("fr-FR");
    return projects.filter((project) => {
      const statusOk = !statusFilter || project.status === statusFilter;
      const haystack = `${project.title} ${project.brief.collection} ${project.brief.style}`.toLocaleLowerCase(
        "fr-FR",
      );
      const textOk = !needle || haystack.includes(needle);
      return statusOk && textOk;
    });
  }, [projects, search, statusFilter]);

  const metrics = useMemo(
    () => ({
      total: projects.length,
      brief: projects.filter((project) => project.status === "Brief").length,
      valid: projects.filter((project) => project.status === "Validé").length,
      archived: projects.filter((project) => project.status === "Archivé").length,
    }),
    [projects],
  );

  const setProject = (project: Project) => {
    setCurrentProject(project);
    setBrief(structuredClone(project.brief));
    setValidation(emptyValidation);
    setApproved(false);
    setSubmission(null);
    setCollectionHint([]);
    initialBrief.current = true;
  };

  const createProject = async () => {
    setBusy(true);
    try {
      const project = await api.createProject();
      replaceProject(project);
      setProject(project);
      setView("brief");
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const openProject = async (project: Project) => {
    setProject(project);
    setView("brief");
  };

  const duplicateProject = async (project: Project) => {
    setBusy(true);
    try {
      const duplicated = await api.duplicateProject(project.id);
      replaceProject(duplicated);
      showToast("success", `« ${project.title} » a été dupliqué.`);
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const askArchive = (project: Project) => {
    setConfirm({
      title: "Archiver le projet ?",
      body: <p>Le projet « {project.title} » restera disponible dans l’historique.</p>,
      confirmLabel: "Archiver",
      danger: true,
      action: async () => {
        setBusy(true);
        try {
          const archived = await api.archiveProject(project.id);
          replaceProject(archived);
          if (currentProject?.id === project.id) {
            setCurrentProject(null);
            setBrief(null);
            setView("projects");
          }
        } catch (error) {
          showToast("error", errorMessage(error));
        } finally {
          setBusy(false);
        }
      },
    });
  };

  const navigate = (target: "projects" | "brief" | "settings") => {
    if (target === "brief" && !currentProject) {
      showToast("info", "Sélectionnez ou créez d’abord un projet.");
      setView("projects");
      return;
    }
    setView(target);
  };

  const updateBrief = <K extends keyof Brief>(key: K, value: Brief[K]) => {
    setBrief((current) => {
      if (!current) return current;
      return { ...current, [key]: value } as Brief;
    });
  };

  const similarCollectionDialog = (
    error: ApiError,
    action: (confirmCollection: boolean) => Promise<void>,
  ) => {
    const detail = error.detail as { similar?: string[] };
    const similar = detail.similar ?? [];
    setCollectionHint(similar);
    setConfirm({
      title: "Collection proche détectée",
      body: (
        <div>
          <p>Valeur(s) proche(s) : {similar.join(", ") || "—"}</p>
          <p>Créer tout de même cette nouvelle collection ?</p>
        </div>
      ),
      confirmLabel: "Créer la collection",
      action: () => action(true),
    });
  };

  const saveBrief = async (confirmCollection = false) => {
    if (!currentProject || !brief) return;
    setBusy(true);
    try {
      const result = await api.saveBrief(currentProject.id, brief, confirmCollection);
      replaceProject(result.project);
      setProject(result.project);
      setView("brief");
      if (result.prompt_invalidated) {
        showToast("warning", "Le brief a changé : le prompt Studio Visuel doit être régénéré.");
      } else {
        showToast("success", "Brouillon enregistré.");
      }
    } catch (error) {
      if (isSimilarCollectionError(error)) {
        similarCollectionDialog(error, saveBrief);
      } else {
        showToast("error", errorMessage(error));
      }
    } finally {
      setBusy(false);
    }
  };

  const preparePrompt = async (confirmCollection = false) => {
    if (!currentProject || !brief) return;
    setBusy(true);
    try {
      const project = await api.preparePrompt(currentProject.id, brief, confirmCollection);
      replaceProject(project);
      setCurrentProject(project);
      setBrief(structuredClone(project.brief));
      setView("prompt");
    } catch (error) {
      if (isSimilarCollectionError(error)) {
        similarCollectionDialog(error, preparePrompt);
      } else {
        showToast("error", errorMessage(error));
      }
    } finally {
      setBusy(false);
    }
  };

  const markResultReady = async () => {
    if (!currentProject) return;
    setBusy(true);
    try {
      const project = await api.markSent(currentProject.id);
      replaceProject(project);
      setCurrentProject(project);
      setValidation(emptyValidation);
      setApproved(false);
      setView("validation");
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const uploadReference = async (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    if (!selected || !currentProject) return;
    setBusy(true);
    try {
      const result = await api.uploadReference(currentProject.id, selected);
      updateBrief("reference_image", result.path);
      showToast("success", `Image de référence sélectionnée : ${result.filename}`);
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  };

  const importFiles = async (files: File[]) => {
    if (!currentProject || !files.length) return;
    setBusy(true);
    try {
      const report = await api.importArtifacts(currentProject.id, files);
      setValidation(report);
      setApproved(false);
      setSubmission(null);
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const approveResult = async (checked: boolean) => {
    if (!currentProject) return;
    setApproved(checked);
    try {
      const result = await api.approve(currentProject.id, checked);
      replaceProject(result.project);
      setCurrentProject(result.project);
      if (result.ready) setView("export");
    } catch (error) {
      showToast("error", errorMessage(error));
    }
  };

  const exportLocal = async () => {
    if (!currentProject) return;
    setBusy(true);
    try {
      const { blob, filename } = await api.exportProject(currentProject.id, approved);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      showToast("success", "Export local préparé.");
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const submitWebhook = async () => {
    if (!currentProject) return;
    setBusy(true);
    try {
      const outcome = await api.submit(currentProject.id, approved);
      setSubmission(outcome);
      const refreshed = await api.getProject(currentProject.id);
      replaceProject(refreshed);
      setCurrentProject(refreshed);
      showToast(outcome.status === "success" ? "success" : "warning", outcome.message);
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const browseStorage = async (path?: string) => {
    setStorageBusy(true);
    try {
      setStorage(await api.browseStorage(path));
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setStorageBusy(false);
    }
  };

  const saveSettings = async () => {
    setBusy(true);
    try {
      const result = await api.saveSettings({
        projects_dir: settingsDir,
        webhook_url: webhookUrl.trim(),
        auth_header_name: authHeaderName.trim(),
        webhook_secret: webhookSecret,
        timeout_seconds: Number(timeoutSeconds),
      });
      setSettingsDir(result.projects_dir);
      setWebhookSecret("");
      setConnectionTest(null);
      await refreshCatalog();
      showToast("success", "Paramètres enregistrés.");
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  const testWebhook = async () => {
    setBusy(true);
    setConnectionTest(null);
    try {
      const outcome = await api.testWebhook();
      setConnectionTest(outcome);
      showToast(
        outcome.status === "success" ? "success" : "warning",
        outcome.message || "Test n8n terminé.",
      );
    } catch (error) {
      showToast("error", errorMessage(error));
    } finally {
      setBusy(false);
    }
  };

  if (!bootstrap) {
    return (
      <div className="loading-screen">
        <div className="brand-orb"><Sparkles size={28} /></div>
        <strong>Visual AI Studio</strong>
        <span>Chargement de l’atelier visuel…</span>
      </div>
    );
  }

  const referenceName = brief?.reference_image
    ? brief.reference_image.split(/[\\/]/).at(-1)
    : "";

  return (
    <div className="app-shell">
      <div className="ambient ambient--one" />
      <div className="ambient ambient--two" />

      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark"><Sparkles size={22} /></div>
          <div>
            <strong>VISUAL AI</strong>
            <span>STUDIO</span>
          </div>
        </div>

        <nav>
          <button
            type="button"
            className={view === "projects" ? "nav-item nav-item--active" : "nav-item"}
            onClick={() => navigate("projects")}
          >
            <Layers3 size={19} />
            <span>Projets</span>
          </button>
          <button
            type="button"
            className={["brief", "prompt", "validation", "export"].includes(view) ? "nav-item nav-item--active" : "nav-item"}
            onClick={() => navigate("brief")}
          >
            <Palette size={19} />
            <span>Créer</span>
          </button>
          <button
            type="button"
            className={view === "settings" ? "nav-item nav-item--active" : "nav-item"}
            onClick={() => navigate("settings")}
          >
            <Settings size={19} />
            <span>Administration</span>
          </button>
        </nav>

        <div className="sidebar-foot">
          <span className="sidebar-foot__dot" />
          <div>
            <strong>Docker Web</strong>
            <span>v0.3.0</span>
          </div>
        </div>
      </aside>

      <main className="workspace">
        {currentProject && ["brief", "prompt", "validation", "export"].includes(view) ? (
          <div className="project-context">
            <div>
              <span>Projet actif</span>
              <strong>{currentProject.title}</strong>
            </div>
            <WorkflowRail view={view} />
          </div>
        ) : null}

        <AnimatePresence mode="wait">
          <motion.section
            key={view}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22 }}
            className="page"
          >
            {view === "projects" ? (
              <>
                <PageTitle
                  eyebrow="Bibliothèque"
                  title="Projets"
                  subtitle="Brief → Studio Visuel → validation → export"
                  actions={
                    <button
                      type="button"
                      className="button button--primary"
                      onClick={() => void createProject()}
                      disabled={busy}
                    >
                      <Plus size={18} /> Nouveau projet
                    </button>
                  }
                />

                <div className="metric-grid">
                  {[
                    ["Projets", metrics.total, "Total", "metric-card--violet"],
                    ["Brief", metrics.brief, "À préparer", "metric-card--blue"],
                    ["Validé", metrics.valid, "Prêts ou exportés", "metric-card--green"],
                    ["Archivé", metrics.archived, "Historique", "metric-card--slate"],
                  ].map(([label, value, hint, className]) => (
                    <motion.div
                      whileHover={{ y: -3 }}
                      className={`metric-card ${className}`}
                      key={String(label)}
                    >
                      <span className="metric-card__glow" />
                      <strong>{value}</strong>
                      <b>{label}</b>
                      <small>{hint}</small>
                    </motion.div>
                  ))}
                </div>

                <div className="panel projects-panel">
                  <div className="panel-head">
                    <div>
                      <span className="eyebrow">Collection de travail</span>
                      <h2>Liste des projets</h2>
                    </div>
                    <div className="project-filters">
                      <label className="search-box">
                        <Search size={17} />
                        <input
                          value={search}
                          onChange={(event) => setSearch(event.target.value)}
                          placeholder="Rechercher par nom, collection ou style…"
                        />
                      </label>
                      <select
                        value={statusFilter}
                        onChange={(event) => setStatusFilter(event.target.value as "" | ProjectStatus)}
                      >
                        <option value="">Tous les statuts</option>
                        {bootstrap.statuses.map((status) => (
                          <option value={status} key={status}>{status}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="project-table-wrap">
                    <table className="project-table">
                      <thead>
                        <tr>
                          <th>Projet</th>
                          <th>Collection</th>
                          <th>Style</th>
                          <th>Statut</th>
                          <th>Dernière modification</th>
                          <th aria-label="Actions" />
                        </tr>
                      </thead>
                      <tbody>
                        {filteredProjects.map((project) => (
                          <tr key={project.id} onDoubleClick={() => void openProject(project)}>
                            <td>
                              <button
                                type="button"
                                className="project-title-button"
                                onClick={() => void openProject(project)}
                              >
                                {project.title}
                              </button>
                            </td>
                            <td>{project.brief.collection || "—"}</td>
                            <td>{project.brief.style || "—"}</td>
                            <td><span className={statusClass(project.status)}>{project.status}</span></td>
                            <td>{projectDate(project.updated_at)}</td>
                            <td>
                              <div className="table-actions">
                                <IconButton onClick={() => void openProject(project)} title="Ouvrir">
                                  <ExternalLink size={16} />
                                </IconButton>
                                <IconButton onClick={() => void duplicateProject(project)} title="Dupliquer">
                                  <Copy size={16} />
                                </IconButton>
                                <IconButton onClick={() => askArchive(project)} title="Archiver">
                                  <Archive size={16} />
                                </IconButton>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {!filteredProjects.length ? (
                      <div className="empty-state">
                        <Layers3 size={28} />
                        <strong>Aucun projet à afficher</strong>
                        <span>Modifiez la recherche ou créez un nouveau projet.</span>
                      </div>
                    ) : null}
                  </div>
                </div>
              </>
            ) : null}

            {view === "brief" && brief && currentProject ? (
              <>
                <PageTitle
                  eyebrow="Création"
                  title="Brief créatif"
                  subtitle="Structurez précisément la demande avant le passage dans Studio Visuel."
                />

                <div className="format-banner">
                  <div className="format-banner__icon"><ImageIcon size={22} /></div>
                  <div>
                    <strong>Instagram Feed</strong>
                    <span>
                      canal IA-Art • 1080 × 1350 • 4:5
                    </span>
                  </div>
                  <span className="format-pill">{brief.post_image_count} visuel{brief.post_image_count > 1 ? "s" : ""}</span>
                </div>

                <div className="brief-grid">
                  <div className="panel form-panel">
                    <div className="panel-head panel-head--compact">
                      <div>
                        <span className="eyebrow">Essentiel</span>
                        <h2>Demande</h2>
                      </div>
                    </div>

                    <div className="field-grid field-grid--two">
                      <label className="field">
                        <span>Sortie *</span>
                        <input value="Instagram Feed" readOnly />
                      </label>
                      <label className="field">
                        <span>Nom du projet *</span>
                        <input
                          value={brief.title}
                          onChange={(event) => updateBrief("title", event.target.value)}
                        />
                      </label>
                      <label className="field">
                        <span>Collection / campagne</span>
                        <input
                          list="collection-list"
                          value={brief.collection}
                          onChange={(event) => updateBrief("collection", event.target.value)}
                        />
                        <datalist id="collection-list">
                          {bootstrap.collections.map((item) => (
                            <option value={item.value} key={item.id} />
                          ))}
                        </datalist>
                        {collectionHint.length ? (
                          <small className="field-warning">Proche : {collectionHint.join(", ")}</small>
                        ) : null}
                      </label>
                      <label className="field">
                        <span>Style</span>
                        <input
                          list="style-list"
                          value={brief.style}
                          onChange={(event) => updateBrief("style", event.target.value)}
                        />
                        <datalist id="style-list">
                          {bootstrap.styles.map((style) => <option value={style} key={style} />)}
                        </datalist>
                      </label>
                    </div>

                    <label className="field">
                      <span>Idée / demande *</span>
                      <textarea
                        rows={6}
                        value={brief.raw_idea}
                        onChange={(event) => updateBrief("raw_idea", event.target.value)}
                        placeholder="Décrivez le visuel à créer, son objectif et le résultat attendu…"
                      />
                    </label>

                    <div className="field-grid field-grid--two">
                      <label className="field">
                        <span>Audience</span>
                        <input value={brief.audience} onChange={(event) => updateBrief("audience", event.target.value)} />
                      </label>
                      <div className="field">
                        <span>Visuels dans le post</span>
                        <div className="image-count-control">
                          <button
                            type="button"
                            onClick={() => updateBrief("post_image_count", Math.max(1, brief.post_image_count - 1))}
                            disabled={brief.post_image_count <= 1}
                          ><Minus size={18} /></button>
                          <strong>{brief.post_image_count}</strong>
                          <button
                            type="button"
                            onClick={() => updateBrief("post_image_count", Math.min(10, brief.post_image_count + 1))}
                            disabled={brief.post_image_count >= 10}
                          ><Plus size={18} /></button>
                          <span>image(s)</span>
                        </div>
                      </div>
                    </div>

                    <label className="field">
                      <span>Texte dans l’image</span>
                      <input
                        value={brief.text_overlay}
                        onChange={(event) => updateBrief("text_overlay", event.target.value)}
                        placeholder="Laisser vide pour aucun texte dans l'image"
                      />
                    </label>

                    <label className="field">
                      <span>Notes</span>
                      <textarea rows={4} value={brief.notes} onChange={(event) => updateBrief("notes", event.target.value)} />
                    </label>
                  </div>

                  <div className="side-stack">
                    <div className="panel compact-panel">
                      <span className="eyebrow">Format</span>
                      <h2>Cadre de sortie</h2>
                      <div className="field-grid field-grid--three">
                        <label className="field">
                          <span>Largeur</span>
                          <input type="number" value={1080} readOnly />
                        </label>
                        <label className="field">
                          <span>Hauteur</span>
                          <input type="number" value={1350} readOnly />
                        </label>
                        <label className="field">
                          <span>Ratio</span>
                          <input value="4:5" readOnly />
                        </label>
                      </div>
                    </div>

                    <div className="panel compact-panel reference-panel">
                      <span className="eyebrow">Référence</span>
                      <h2>Image de référence</h2>
                      <div className="reference-box">
                        <FileImage size={28} />
                        <div>
                          <strong>{referenceName || "Aucune image"}</strong>
                          <span>{referenceName ? "Référence attachée au brief" : "PNG, JPG ou WebP"}</span>
                        </div>
                        <button type="button" className="button button--soft" onClick={() => referenceInput.current?.click()}>
                          Choisir…
                        </button>
                        <input
                          ref={referenceInput}
                          type="file"
                          accept=".png,.jpg,.jpeg,.webp"
                          hidden
                          onChange={(event) => void uploadReference(event)}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <details className="panel advanced-panel">
                  <summary>
                    <div>
                      <span className="eyebrow">Direction créative</span>
                      <strong>Paramètres avancés</strong>
                    </div>
                    <ChevronRight size={20} />
                  </summary>
                  <div className="advanced-grid">
                    {advancedFields.map(([key, label]) => (
                      <label className="field" key={key}>
                        <span>{label}</span>
                        <input
                          value={String(brief[key] ?? "")}
                          onChange={(event) => updateBrief(key, event.target.value as never)}
                        />
                      </label>
                    ))}
                  </div>
                </details>

                <div className="sticky-actions">
                  <button type="button" className="button button--ghost" onClick={() => void saveBrief()} disabled={busy}>
                    Enregistrer le brouillon
                  </button>
                  <button type="button" className="button button--primary" onClick={() => void preparePrompt()} disabled={busy}>
                    <WandSparkles size={18} /> Préparer pour Studio Visuel
                  </button>
                </div>
              </>
            ) : null}

            {view === "prompt" && currentProject ? (
              <>
                <PageTitle
                  eyebrow="Étape 2"
                  title="Préparation Studio Visuel"
                  subtitle="Le prompt de lancement est prêt. Copiez-le dans l’agent Studio Visuel."
                />
                <div className="prompt-layout">
                  <div className="panel prompt-panel">
                    <div className="panel-head">
                      <div>
                        <span className="eyebrow">Prompt à copier</span>
                        <h2>Version {currentProject.version}</h2>
                      </div>
                      {currentProject.prompt_hash ? (
                        <span className="hash-pill" title={currentProject.prompt_hash}>SHA-256</span>
                      ) : null}
                    </div>
                    <pre className="prompt-preview">{currentProject.prompt_text}</pre>
                    <div className="prompt-actions">
                      <button type="button" className="button button--soft" onClick={() => {
                        void navigator.clipboard.writeText(currentProject.prompt_text);
                        showToast("success", "Prompt copié.");
                      }}>
                        <Clipboard size={17} /> Copier le prompt
                      </button>
                      {bootstrap.settings.agent_url ? (
                        <button type="button" className="button button--soft" onClick={() => window.open(bootstrap.settings.agent_url, "_blank", "noopener,noreferrer")}>
                          <ExternalLink size={17} /> Ouvrir Studio Visuel
                        </button>
                      ) : null}
                    </div>
                  </div>

                  <div className="panel guide-panel">
                    <span className="eyebrow">Mode d’emploi</span>
                    <h2>Passage dans ChatGPT</h2>
                    <ol className="guide-list">
                      <li><span>1</span><p>Copiez le prompt.</p></li>
                      <li><span>2</span><p>Ouvrez Studio Visuel dans ChatGPT.</p></li>
                      <li><span>3</span><p>Collez le prompt dans la conversation.</p></li>
                      <li><span>4</span><p>Suivez les étapes proposées et validez-les une par une.</p></li>
                      <li><span>5</span><p>Lorsque le résultat est terminé, revenez ici pour importer les fichiers.</p></li>
                    </ol>
                  </div>
                </div>
                <div className="sticky-actions sticky-actions--spread">
                  <button type="button" className="button button--ghost" onClick={() => setView("brief")}>
                    <ArrowLeft size={17} /> Retour au brief
                  </button>
                  <button type="button" className="button button--primary" onClick={() => void markResultReady()} disabled={busy || !currentProject.prompt_text}>
                    Résultat prêt — importer les fichiers <ChevronRight size={17} />
                  </button>
                </div>
              </>
            ) : null}

            {view === "validation" && currentProject ? (
              <>
                <PageTitle
                  eyebrow="Étape 3"
                  title="Validation du résultat"
                  subtitle="Importez les fichiers générés puis contrôlez le résultat avant validation."
                />

                <div
                  className="drop-zone"
                  onDragOver={(event: DragEvent<HTMLDivElement>) => event.preventDefault()}
                  onDrop={(event: DragEvent<HTMLDivElement>) => {
                    event.preventDefault();
                    void importFiles(Array.from(event.dataTransfer.files));
                  }}
                >
                  <div className="drop-zone__icon"><Upload size={28} /></div>
                  <div>
                    <strong>Déposez ici les fichiers générés</strong>
                    <span>PNG, JPG, WebP, Markdown, TXT et JSON</span>
                  </div>
                  <div className="drop-zone__actions">
                    <button type="button" className="button button--soft" onClick={() => fileInput.current?.click()}>
                      Choisir des fichiers…
                    </button>
                    <button type="button" className="button button--soft" onClick={() => folderInput.current?.click()}>
                      Choisir un dossier…
                    </button>
                  </div>
                  <input
                    ref={fileInput}
                    type="file"
                    multiple
                    accept=".png,.jpg,.jpeg,.webp,.md,.txt,.json"
                    hidden
                    onChange={(event) => {
                      void importFiles(Array.from(event.target.files ?? []));
                      event.target.value = "";
                    }}
                  />
                  <input
                    ref={folderInput}
                    type="file"
                    multiple
                    hidden
                    onChange={(event) => {
                      void importFiles(Array.from(event.target.files ?? []));
                      event.target.value = "";
                    }}
                  />
                </div>

                {validation.artifacts.length || validation.issues.length ? (
                  <>
                    <div className="validation-grid">
                      <div className="panel validation-list-panel">
                        <div className="panel-head panel-head--compact">
                          <div>
                            <span className="eyebrow">Contrôles</span>
                            <h2>Rapport</h2>
                          </div>
                          <span className={validation.automatic_checks_passed ? "check-pill check-pill--ok" : "check-pill check-pill--error"}>
                            {validation.automatic_checks_passed ? <Check size={15} /> : <X size={15} />}
                            {validation.automatic_checks_passed ? "Conforme" : "À corriger"}
                          </span>
                        </div>
                        <div className="validation-lines">
                          {validation.automatic_checks_passed ? (
                            <div className="validation-line validation-line--ok"><Check size={16} /> Contrôles automatiques conformes.</div>
                          ) : null}
                          {validation.issues.map((issue, index) => (
                            <div className={`validation-line ${issue.blocking ? "validation-line--error" : "validation-line--warning"}`} key={`${issue.code}-${index}`}>
                              {issue.blocking ? <X size={16} /> : <span>!</span>}
                              {issue.message}
                            </div>
                          ))}
                          {validation.artifacts.map((artifact) => (
                            <div className="artifact-line" key={artifact.id}>
                              {artifact.artifact_type === "image" ? <FileImage size={16} /> : <FileArchive size={16} />}
                              <span>{artifact.filename}</span>
                              {artifact.width && artifact.height ? <small>{artifact.width} × {artifact.height}</small> : null}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="panel approval-panel">
                        <span className="eyebrow">Validation humaine</span>
                        <h2>Décision finale</h2>
                        <p>La validation reste volontairement explicite avant export ou envoi n8n.</p>
                        <label className={`approval-toggle ${approved ? "approval-toggle--checked" : ""}`}>
                          <input
                            type="checkbox"
                            checked={approved}
                            onChange={(event) => void approveResult(event.target.checked)}
                          />
                          <span className="approval-check">{approved ? <Check size={18} /> : null}</span>
                          <strong>Je valide ce résultat</strong>
                        </label>
                      </div>
                    </div>

                    <div className="gallery-section">
                      <div className="section-heading">
                        <span className="eyebrow">Galerie</span>
                        <h2>Aperçu des images</h2>
                      </div>
                      <div className="gallery-grid">
                        {validation.artifacts.filter((item) => item.artifact_type === "image").map((artifact) => (
                          <motion.figure whileHover={{ y: -4 }} className="image-card" key={artifact.id}>
                            <img src={artifact.preview_url} alt={artifact.filename} />
                            <figcaption>{artifact.filename}</figcaption>
                          </motion.figure>
                        ))}
                        {!validation.artifacts.some((item) => item.artifact_type === "image") ? (
                          <div className="empty-state"><ImageIcon size={28} /><strong>Aucune image disponible</strong></div>
                        ) : null}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="empty-canvas">
                    <ImageIcon size={34} />
                    <strong>Aucun résultat importé</strong>
                    <span>Déposez le paquet généré par IA-Art pour commencer le contrôle.</span>
                  </div>
                )}
              </>
            ) : null}

            {view === "export" && currentProject ? (
              <>
                <PageTitle
                  eyebrow="Étape 4"
                  title="Export"
                  subtitle="Exportez le résultat localement ou utilisez le webhook n8n existant."
                />
                <div className="export-grid">
                  <div className="panel export-panel">
                    <div className="export-hero">
                      <div className="export-hero__icon"><Check size={26} /></div>
                      <div>
                        <span className="eyebrow">Projet validé</span>
                        <h2>{currentProject.title}</h2>
                        <p>Version {currentProject.version}</p>
                      </div>
                    </div>
                    <div className="export-files">
                      {validation.artifacts.map((artifact) => (
                        <div key={artifact.id}>
                          {artifact.artifact_type === "image" ? <FileImage size={17} /> : <FileArchive size={17} />}
                          <span>{artifact.filename}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="panel delivery-panel">
                    <span className="eyebrow">Livraison</span>
                    <h2>Destination</h2>
                    <button type="button" className="delivery-action" onClick={() => void exportLocal()} disabled={busy || !approved}>
                      <span className="delivery-action__icon"><Download size={21} /></span>
                      <span><strong>Exporter localement</strong><small>Télécharger le paquet complet</small></span>
                      <ChevronRight size={18} />
                    </button>
                    <button
                      type="button"
                      className="delivery-action"
                      onClick={() => void submitWebhook()}
                      disabled={busy || !approved || !bootstrap.settings.webhook_configured}
                    >
                      <span className="delivery-action__icon delivery-action__icon--n8n"><Send size={21} /></span>
                      <span>
                        <strong>Envoyer au webhook</strong>
                        <small>{bootstrap.settings.webhook_configured ? "n8n configuré" : "Webhook non configuré"}</small>
                      </span>
                      <ChevronRight size={18} />
                    </button>
                  </div>
                </div>

                {submission ? (
                  <div className={`submission-result ${submission.status === "success" ? "submission-result--ok" : "submission-result--error"}`}>
                    <strong>{submission.message}</strong>
                    {submission.execution_id ? <span>Exécution distante : {submission.execution_id}</span> : null}
                    {submission.remote_url ? <a href={submission.remote_url} target="_blank" rel="noreferrer">{submission.remote_url}</a> : null}
                    {submission.unknown ? <span>Le statut distant est inconnu.</span> : null}
                  </div>
                ) : null}
              </>
            ) : null}

            {view === "settings" ? (
              <>
                <PageTitle
                  eyebrow="Administration"
                  title="Paramètres"
                  subtitle="Gérez le stockage local et la connexion n8n sans modifier le fichier .env."
                />
                <div className="settings-wrap">
                  <div className="panel settings-card">
                    <div className="settings-icon"><FolderOpen size={26} /></div>
                    <div className="settings-copy">
                      <span className="eyebrow">Stockage local</span>
                      <h2>Dossier des projets</h2>
                      <p>Emplacement utilisé par Visual AI Studio pour conserver les projets et leurs fichiers.</p>
                    </div>
                    <div className="settings-field">
                      <input value={settingsDir} readOnly />
                      <button type="button" className="button button--soft" onClick={() => void browseStorage(settingsDir)}>
                        <Folder size={17} /> Choisir…
                      </button>
                    </div>
                    <div className="settings-hint">
                      Les données restent dans le volume Docker monté sous {bootstrap.settings.storage_root}.
                    </div>
                  </div>

                  <div className="panel settings-card settings-card--admin">
                    <div className="settings-icon settings-icon--cyan"><PlugZap size={26} /></div>
                    <div className="settings-copy">
                      <span className="eyebrow">Automatisation</span>
                      <h2>Connexion n8n → Notion</h2>
                      <p>Visual AI Studio envoie ici le paquet Instagram. Les flux suivants démarrent ensuite depuis Notion.</p>
                    </div>
                    <span className={`settings-status ${bootstrap.settings.webhook_configured ? "settings-status--ok" : "settings-status--off"}`}>
                      <span />
                      {bootstrap.settings.webhook_configured ? "Webhook configuré" : "Webhook non configuré"}
                    </span>

                    <div className="settings-form-grid">
                      <label className="field">
                        <span><Link2 size={13} /> URL du webhook n8n</span>
                        <input
                          type="url"
                          value={webhookUrl}
                          onChange={(event) => setWebhookUrl(event.target.value)}
                          placeholder="http://192.168.x.x:5678/webhook/ia-art-import-notion-hub"
                          autoComplete="url"
                        />
                      </label>
                      <label className="field">
                        <span><KeyRound size={13} /> Nom du header d’authentification</span>
                        <input
                          value={authHeaderName}
                          onChange={(event) => setAuthHeaderName(event.target.value)}
                          placeholder="X-Visual-AI-Token"
                          autoComplete="off"
                        />
                      </label>
                      <label className="field">
                        <span><KeyRound size={13} /> Secret du webhook</span>
                        <input
                          type="password"
                          value={webhookSecret}
                          onChange={(event) => setWebhookSecret(event.target.value)}
                          placeholder={webhookSecretConfigured ? "Laisser vide pour conserver le secret" : "Saisir le secret n8n"}
                          autoComplete="new-password"
                        />
                        <small className="settings-field-note">
                          {webhookSecret ? "Nouveau secret prêt à être enregistré." : webhookSecretConfigured ? "Un secret est déjà enregistré. Il n’est jamais affiché." : "Aucun secret enregistré."}
                        </small>
                      </label>
                      <label className="field">
                        <span><Timer size={13} /> Délai maximal (secondes)</span>
                        <input
                          type="number"
                          min={1}
                          max={300}
                          step={1}
                          value={timeoutSeconds}
                          onChange={(event) => setTimeoutSeconds(Number(event.target.value))}
                        />
                      </label>
                    </div>

                    {connectionTest ? (
                      <div className={`submission-result ${connectionTest.status === "success" ? "submission-result--ok" : "submission-result--error"}`}>
                        <strong>{connectionTest.status === "success" ? "Connexion n8n opérationnelle" : "Connexion n8n en échec"}</strong>
                        <span>{connectionTest.message}</span>
                        {connectionTest.http_status ? <span>HTTP {connectionTest.http_status}</span> : null}
                      </div>
                    ) : null}

                    <div className="settings-hint">
                      Enregistrez les valeurs avant de lancer le test. Elles sont conservées dans le volume de l’application, pas dans le fichier .env.
                    </div>
                    <div className="settings-actions settings-actions--inline">
                      <button type="button" className="button button--soft" onClick={() => void testWebhook()} disabled={busy || !bootstrap.settings.webhook_configured}>
                        <PlugZap size={17} /> Tester la connexion
                      </button>
                      <button type="button" className="button button--primary" onClick={() => void saveSettings()} disabled={busy}>
                        Enregistrer la configuration
                      </button>
                    </div>
                  </div>

                </div>
              </>
            ) : null}
          </motion.section>
        </AnimatePresence>
      </main>

      {busy ? <div className="busy-indicator"><span /><small>Traitement…</small></div> : null}

      <AnimatePresence>
        {toast ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className={`toast toast--${toast.tone}`}
          >
            {toast.message}
          </motion.div>
        ) : null}
      </AnimatePresence>

      <ConfirmModal state={confirm} onClose={() => setConfirm(null)} />
      <StorageModal
        listing={storage}
        busy={storageBusy}
        onBrowse={browseStorage}
        onChoose={(path) => {
          setSettingsDir(path);
          setStorage(null);
        }}
        onClose={() => setStorage(null)}
      />
    </div>
  );
}
