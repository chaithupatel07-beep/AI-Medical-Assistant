export interface UserProfile {
  date_of_birth: string | null;
  age: number | null;
  gender: string | null;
  blood_type: string | null;
  allergies: string | null;
  chronic_conditions: string | null;
  emergency_contact: string | null;
  preferred_units: "metric" | "imperial";
  preferred_language?: "en" | "te" | "hi";
  updated_at?: string | null;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
  profile: UserProfile | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type AiMode = "cloud_ai" | "ollama_local" | "built_in_offline";

export interface HealthStatus {
  status: string;
  app: string;
  ai_configured: boolean;
  ai_ready?: boolean;
  ai_mode?: AiMode;
  ollama_model?: string | null;
  ai_provider: string;
  chat_model: string;
  vision_model: string;
  tesseract_ocr_available: boolean;
  database_mode?: "persistent" | "ephemeral_sqlite";
  disclaimer: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  emergency_flagged: boolean;
  created_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface ChatTurnResponse {
  session: ChatSession;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  emergency_detected: boolean;
  emergency_reasons: string[];
  emergency_banner: string | null;
  ai_model: string;
  disclaimer: string;
}

export interface SymptomCheckPayload {
  age: number;
  gender?: string;
  main_symptom: string;
  duration: string;
  severity: "mild" | "moderate" | "severe";
  additional_symptoms?: string;
  relevant_context?: string;
}

export interface PossibleExplanation {
  title: string;
  description: string;
}

export interface SymptomCheckResult {
  activity_id: string;
  educational_overview: string;
  possible_explanations: PossibleExplanation[];
  recommended_next_steps: string[];
  warning_signs: string[];
  when_to_consult_doctor: string;
  questions_for_doctor: string[];
  emergency_detected: boolean;
  emergency_reasons: string[];
  emergency_banner: string | null;
  ai_model: string;
  disclaimer: string;
}

export interface LabMarker {
  name: string;
  value: string;
  unit: string;
  reference_range: string;
  status: "high" | "low" | "normal" | "unknown";
  explanation: string;
}

export interface MedicalTerm {
  term: string;
  simple_explanation: string;
}

export interface ReportSummary {
  id: string;
  report_id: string;
  plain_summary: string;
  lab_markers: LabMarker[];
  medical_terms: MedicalTerm[];
  questions_for_doctor: string[];
  warnings: string[];
  ai_model: string | null;
  disclaimer: string;
  created_at: string;
}

export interface MedicalReport {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  extraction_method: string;
  extracted_text: string | null;
  status: string;
  created_at: string;
  summary: ReportSummary | null;
}

export interface MedicalImage {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  image_context: string | null;
  analysis_summary: string | null;
  observations: string[];
  limitations: string | null;
  recommended_next_steps: string | null;
  ai_model: string | null;
  status: string;
  disclaimer: string;
  created_at: string;
}

export interface LibraryArticle {
  id: string;
  title: string;
  category: string;
  category_label?: string;
  read_time: string;
  summary: string;
  content: string;
  key_takeaways: string[];
  when_to_see_doctor: string;
  source_name: string;
  source_url: string;
}

export interface ActivityItem {
  id: string;
  activity_type: string;
  description: string;
  resource_type: string | null;
  resource_id: string | null;
  metadata_json: string | null;
  created_at: string;
}

export interface DashboardOverview {
  user: User;
  stats: {
    total_reports: number;
    summarized_reports: number;
    total_chat_sessions: number;
    total_chat_messages: number;
    total_images: number;
    total_symptom_checks: number;
  };
  recent_reports: Array<{
    id: string;
    original_filename: string;
    status: string;
    extraction_method: string;
    has_summary: boolean;
    created_at: string;
  }>;
  recent_chats: Array<{
    id: string;
    title: string;
    message_count: number;
    updated_at: string;
  }>;
  recent_activity: Array<{
    id: string;
    activity_type: string;
    description: string;
    created_at: string;
  }>;
  ai_status: {
    configured: boolean;
    ready?: boolean;
    mode?: AiMode;
    ollama_model?: string | null;
    provider: string;
    chat_model: string;
    vision_model: string;
  };
  database_mode?: "persistent" | "ephemeral_sqlite";
}
