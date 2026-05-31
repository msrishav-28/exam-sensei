import { supabase } from "./supabase";

const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000/api/v1";

// ---------------------------------------------------------------------------
// Types (mirror the backend response shapes in backend/app_v2.py)
// ---------------------------------------------------------------------------

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  current_stage: string;
  career_paths: string[] | null;
  active_exams: string[] | null;
  is_verified: boolean;
}

export interface Exam {
  id: number;
  name: string;
  code: string;
  body: string;
  exam_type: string;
  important_dates: Record<string, unknown> | null;
}

export interface Recommendation {
  type: string;
  exam: string | null;
  score: number;
  reasoning: string;
}

export interface RecommendationsResponse {
  user_stage: string;
  career_paths: string[] | null;
  recommendations: Recommendation[];
  next_actions: string[];
  error?: string;
}

export interface Gamification {
  level: number;
  xp_points: number;
  streak_days: number;
  achievements: string[];
}

export interface ChatResponse {
  response: string;
  intent: string;
  confidence: number;
  suggested_actions: string[];
  session_id: string;
  provider: string;
}

export interface StudyPlanTopic {
  name: string;
  subject: string;
  priority_score: number;
  estimated_days: number;
  difficulty: string;
  weightage: number;
}

export interface WeeklyPlanItem {
  day: string;
  topic: string;
  focus_area: string;
  estimated_hours: number;
  difficulty: string;
}

export interface StudyPlan {
  exam_code: string;
  total_days: number;
  prioritized_topics: StudyPlanTopic[];
  weekly_plan: Record<string, WeeklyPlanItem[]>;
  estimated_completion: string;
  success_probability: number;
  error?: string;
}

export interface ProfileUpdate {
  strengths?: string[];
  weaknesses?: string[];
  study_hours_per_day?: number;
  study_consistency?: number;
  interests?: string[];
  career_paths?: string[];
  active_exams?: string[];
}

// ---------------------------------------------------------------------------
// Core request helper — attaches the Supabase access token, unwraps the
// backend's { detail: { message, details } } error envelope.
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  status: number;
  details: unknown;
  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function authHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; auth?: boolean } = {},
): Promise<T> {
  const { method = "GET", body, auth = true } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) Object.assign(headers, await authHeader());

  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Network error — is the backend reachable?");
  }

  const text = await res.text();
  const payload = text ? safeJson(text) : null;

  if (!res.ok) {
    const detail = (payload as { detail?: { message?: string; details?: unknown } } | null)?.detail;
    const message =
      (typeof detail === "object" && detail?.message) ||
      (typeof detail === "string" ? detail : null) ||
      `Request failed (${res.status})`;
    throw new ApiError(res.status, message, (detail as { details?: unknown })?.details);
  }

  return payload as T;
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Typed endpoints (1:1 with backend routes)
// ---------------------------------------------------------------------------

export const api = {
  getMe: () => request<UserProfile>("/auth/me"),

  listExams: (params?: { skip?: number; limit?: number; exam_type?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip != null) q.set("skip", String(params.skip));
    if (params?.limit != null) q.set("limit", String(params.limit));
    if (params?.exam_type) q.set("exam_type", params.exam_type);
    const qs = q.toString();
    return request<Exam[]>(`/exams${qs ? `?${qs}` : ""}`, { auth: false });
  },

  getExam: (id: number) => request<Exam>(`/exams/${id}`, { auth: false }),

  getProfile: (userId: string) => request<UserProfile>(`/users/${userId}`),

  updateProfile: (userId: string, body: ProfileUpdate) =>
    request<{ message: string }>(`/users/${userId}/profile`, { method: "PUT", body }),

  chat: (userId: string, message: string, sessionId?: string) =>
    request<ChatResponse>(`/users/${userId}/chat`, {
      method: "POST",
      body: { message, session_id: sessionId ?? null },
    }),

  getRecommendations: (userId: string) =>
    request<RecommendationsResponse>(`/users/${userId}/recommendations`),

  generateStudyPlan: (userId: string, examCode: string, daysAvailable = 90) =>
    request<StudyPlan>(`/users/${userId}/study-plan`, {
      method: "POST",
      body: { exam_code: examCode, days_available: daysAvailable },
    }),

  getGamification: (userId: string) =>
    request<Gamification>(`/users/${userId}/gamification`),
};
