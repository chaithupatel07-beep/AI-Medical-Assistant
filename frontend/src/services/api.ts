import type {
  ActivityItem,
  AuthResponse,
  ChatSession,
  ChatSessionDetail,
  ChatTurnResponse,
  DashboardOverview,
  HealthStatus,
  LibraryArticle,
  MedicalImage,
  MedicalReport,
  SymptomCheckPayload,
  SymptomCheckResult,
  User,
} from "@/types/api";

const TOKEN_STORAGE_KEY = "ai_med_assistant_token";
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");

export function buildApiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setAuthToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(buildApiUrl(path), { ...options, headers });
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const errJson = await res.json();
      if (typeof errJson?.detail === "string") {
        detail = errJson.detail;
      } else if (Array.isArray(errJson?.detail) && errJson.detail[0]?.msg) {
        detail = errJson.detail.map((d: { msg: string }) => d.msg).join(" ");
      }
    } catch {
      // keep default detail
    }
    if (res.status === 401 && token && !path.includes("/api/auth/login")) {
      setAuthToken(null);
    }
    throw new ApiError(detail, res.status);
  }

  return (await res.json()) as T;
}

function uploadWithProgress<T>(
  path: string,
  formData: FormData,
  onProgress?: (percent: number) => void
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", buildApiUrl(path));
    const token = getAuthToken();
    if (token) {
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    }
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    xhr.onload = () => {
      try {
        const parsed = JSON.parse(xhr.responseText || "{}");
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(parsed as T);
        } else {
          reject(new ApiError(parsed?.detail || `Upload failed (${xhr.status})`, xhr.status));
        }
      } catch {
        reject(new ApiError(`Upload failed with status ${xhr.status}`, xhr.status));
      }
    };
    xhr.onerror = () => reject(new ApiError("Network error while uploading file.", 0));
    xhr.send(formData);
  });
}

export async function fetchProtectedBlob(path: string): Promise<Blob> {
  const token = getAuthToken();
  const res = await fetch(buildApiUrl(path), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) {
    throw new ApiError("Unable to retrieve protected file.", res.status);
  }
  return await res.blob();
}

export async function downloadProtectedFile(path: string, fallbackFilename: string): Promise<void> {
  const blob = await fetchProtectedBlob(path);
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fallbackFilename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export const api = {
  health: () => request<HealthStatus>("/api/health"),

  register: (payload: { email: string; full_name: string; password: string }) =>
    request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (payload: { email: string; password: string }) =>
    request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  logout: () => request<{ message: string }>("/api/auth/logout", { method: "POST" }),

  forgotPassword: (email: string) =>
    request<{ message: string; delivery_mode: string; reset_token?: string }>(
      "/api/auth/forgot-password",
      {
        method: "POST",
        body: JSON.stringify({ email }),
      }
    ),

  resetPassword: (payload: { token: string; new_password: string }) =>
    request<{ message: string }>("/api/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  me: () => request<User>("/api/auth/me"),

  getDashboardOverview: () => request<DashboardOverview>("/api/dashboard/overview"),

  updateProfile: (payload: Record<string, unknown>) =>
    request<User>("/api/users/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  changePassword: (payload: { current_password: string; new_password: string }) =>
    request<{ message: string }>("/api/users/change-password", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listActivity: (limit = 50) => request<ActivityItem[]>(`/api/users/activity?limit=${limit}`),

  deleteActivity: (activityId: string) =>
    request<{ message: string }>(`/api/users/activity/${activityId}`, { method: "DELETE" }),

  clearActivity: () => request<{ message: string }>("/api/users/activity", { method: "DELETE" }),

  getSuggestedQuestions: (lang = "en") =>
    request<{ questions: string[] }>(`/api/chat/suggested-questions?lang=${encodeURIComponent(lang)}`),

  listChatSessions: () => request<ChatSession[]>("/api/chat/sessions"),

  createChatSession: (title?: string) =>
    request<ChatSession>("/api/chat/sessions", {
      method: "POST",
      body: JSON.stringify({ title }),
    }),

  getChatSession: (sessionId: string) =>
    request<ChatSessionDetail>(`/api/chat/sessions/${sessionId}`),

  sendChatMessage: (sessionId: string, content: string, language = "en") =>
    request<ChatTurnResponse>(`/api/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content, language }),
    }),

  clearChatSession: (sessionId: string) =>
    request<ChatSessionDetail>(`/api/chat/sessions/${sessionId}/clear`, {
      method: "POST",
    }),

  deleteChatSession: (sessionId: string) =>
    request<{ message: string }>(`/api/chat/sessions/${sessionId}`, { method: "DELETE" }),

  checkSymptoms: (payload: SymptomCheckPayload & { language?: string }) =>
    request<SymptomCheckResult>("/api/symptoms/check", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getSymptomHistory: () => request<ActivityItem[]>("/api/symptoms/history"),

  uploadReport: (file: File, onProgress?: (percent: number) => void) => {
    const fd = new FormData();
    fd.append("file", file);
    return uploadWithProgress<MedicalReport>("/api/reports/upload", fd, onProgress);
  },

  summarizeReport: (reportId: string, lang = "en") =>
    request<MedicalReport>(`/api/reports/${reportId}/summarize?lang=${encodeURIComponent(lang)}`, {
      method: "POST",
    }),

  listReports: () => request<MedicalReport[]>("/api/reports"),

  getReport: (reportId: string) => request<MedicalReport>(`/api/reports/${reportId}`),

  deleteReport: (reportId: string) =>
    request<{ message: string }>(`/api/reports/${reportId}`, { method: "DELETE" }),

  uploadImage: (file: File, imageContext: string, onProgress?: (percent: number) => void) => {
    const fd = new FormData();
    fd.append("file", file);
    if (imageContext.trim()) {
      fd.append("image_context", imageContext.trim());
    }
    return uploadWithProgress<MedicalImage>("/api/images/upload", fd, onProgress);
  },

  analyzeImage: (imageId: string, lang = "en") =>
    request<MedicalImage>(`/api/images/${imageId}/analyze?lang=${encodeURIComponent(lang)}`, {
      method: "POST",
    }),

  listImages: () => request<MedicalImage[]>("/api/images"),

  deleteImage: (imageId: string) =>
    request<{ message: string }>(`/api/images/${imageId}`, { method: "DELETE" }),

  listLibraryArticles: (category?: string, query?: string, lang = "en") => {
    const params = new URLSearchParams();
    if (category && category !== "All") params.set("category", category);
    if (query?.trim()) params.set("q", query.trim());
    params.set("lang", lang);
    const qs = params.toString();
    return request<{
      categories: string[];
      category_labels?: Record<string, string>;
      articles: LibraryArticle[];
      total: number;
    }>(`/api/library/articles?${qs}`);
  },
};
