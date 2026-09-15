export type ProjectStatus = "Brief" | "Validé" | "Archivé";
export type OutputMode = "instagram" | "custom";

export interface Brief {
  title: string;
  mode: OutputMode;
  post_image_count: number;
  audience: string;
  target_width: number | null;
  target_height: number | null;
  aspect_ratio: string;
  text_overlay: string;
  collection: string;
  collection_is_new: boolean;
  style: string;
  raw_idea: string;
  intent: string;
  subject: string;
  setting: string;
  ambience: string;
  palette: string;
  lighting: string;
  materials: string;
  composition: string;
  detail_level: string;
  required_elements: string;
  forbidden_elements: string;
  reference_image: string;
  reference_note: string;
  board: string;
  notes: string;
}

export interface Project {
  id: string;
  title: string;
  slug: string;
  status: ProjectStatus;
  brief: Brief;
  prompt_text: string;
  prompt_hash: string;
  prompt_brief_hash: string;
  version: number;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
  remote_url: string;
}

export interface ReferenceValue {
  id: string;
  type: string;
  value: string;
  normalized_value: string;
  source: string;
  is_new: boolean;
  sync_status: string;
  updated_at: string;
}

export interface Artifact {
  id: string;
  project_id: string;
  artifact_type: "image" | "text" | "metadata" | "manifest";
  filename: string;
  sha256: string;
  width: number | null;
  height: number | null;
  validation_status: string;
  preview_url: string;
}

export interface ValidationIssue {
  code: string;
  message: string;
  blocking: boolean;
  artifact: string | null;
}

export interface ValidationReport {
  artifacts: Artifact[];
  issues: ValidationIssue[];
  automatic_checks_passed: boolean;
  ready: boolean;
}

export interface ModePreset {
  value: OutputMode;
  label: string;
  width: number | null;
  height: number | null;
  aspect_ratio: string;
}

export interface BootstrapData {
  projects: Project[];
  collections: ReferenceValue[];
  styles: string[];
  settings: {
    projects_dir: string;
    webhook_configured: boolean;
    agent_url: string;
    max_file_size_mb: number;
    storage_root: string;
  };
  statuses: ProjectStatus[];
  modes: ModePreset[];
}

export interface SubmissionOutcome {
  status: string;
  retryable: boolean;
  unknown: boolean;
  execution_id: string;
  remote_url: string;
  message: string;
  http_status: number | null;
  duplicate_avoided: boolean;
}

export interface DirectoryListing {
  root: string;
  current: string;
  parent: string;
  children: Array<{ name: string; path: string }>;
}
