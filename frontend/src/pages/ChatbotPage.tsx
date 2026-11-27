import { FormEvent, useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Bot,
  Eraser,
  Loader2,
  MessageSquarePlus,
  Send,
  Sparkles,
  Trash2,
  User as UserIcon,
} from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { AiConfigNotice } from "@/components/AiConfigNotice";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useLanguage } from "@/hooks/useLanguage";
import { api } from "@/services/api";
import type { AiMode, ChatMessage, ChatSession } from "@/types/api";
import { formatDateTime } from "@/utils/format";

export function ChatbotPage() {
  const { language, t } = useLanguage();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSessionId = searchParams.get("session");

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(initialSessionId);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const [aiConfigured, setAiConfigured] = useState(true);
  const [aiMode, setAiMode] = useState<AiMode | undefined>(undefined);
  const [emergencyBanner, setEmergencyBanner] = useState<string | null>(null);
  const [emergencyReasons, setEmergencyReasons] = useState<string[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  useEffect(() => {
    Promise.all([api.listChatSessions(), api.health()])
      .then(([sessionList, health]) => {
        setSessions(sessionList);
        setAiConfigured(health.ai_configured);
        setAiMode(health.ai_mode);

        if (initialSessionId && sessionList.some((s) => s.id === initialSessionId)) {
          setActiveSessionId(initialSessionId);
        } else if (sessionList.length > 0) {
          setActiveSessionId(sessionList[0].id);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to initialize chat."))
      .finally(() => setLoadingSessions(false));
  }, [initialSessionId]);

  useEffect(() => {
    api
      .getSuggestedQuestions(language)
      .then((res) => setSuggestedQuestions(res.questions))
      .catch(() => {});
  }, [language]);

  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }
    setLoadingMessages(true);
    setError(null);
    api
      .getChatSession(activeSessionId)
      .then((detail) => {
        setMessages(detail.messages);
        const hasFlag = detail.messages.some((m) => m.emergency_flagged);
        if (!hasFlag) {
          setEmergencyBanner(null);
          setEmergencyReasons([]);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load conversation."))
      .finally(() => setLoadingMessages(false));
  }, [activeSessionId]);

  const handleNewSession = async () => {
    setError(null);
    try {
      const created = await api.createChatSession("New Health Conversation");
      setSessions((prev) => [created, ...prev]);
      setActiveSessionId(created.id);
      setSearchParams({ session: created.id });
      setMessages([]);
      setEmergencyBanner(null);
      setEmergencyReasons([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create chat session.");
    }
  };

  const handleClearSession = async () => {
    if (!activeSessionId) return;
    setError(null);
    try {
      const cleared = await api.clearChatSession(activeSessionId);
      setMessages(cleared.messages);
      setSessions((prev) => prev.map((s) => (s.id === cleared.id ? cleared : s)));
      setEmergencyBanner(null);
      setEmergencyReasons([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not clear conversation.");
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    setError(null);
    try {
      await api.deleteChatSession(sessionId);
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setSessions(remaining);
      if (activeSessionId === sessionId) {
        const nextId = remaining[0]?.id || null;
        setActiveSessionId(nextId);
        if (nextId) {
          setSearchParams({ session: nextId });
        } else {
          setSearchParams({});
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete conversation.");
    }
  };

  const sendText = async (textToSend: string) => {
    const trimmed = textToSend.trim();
    if (!trimmed || sending) return;

    setError(null);
    setSending(true);
    try {
      let targetSessionId = activeSessionId;
      if (!targetSessionId) {
        const created = await api.createChatSession("New Health Conversation");
        setSessions((prev) => [created, ...prev]);
        targetSessionId = created.id;
        setActiveSessionId(created.id);
        setSearchParams({ session: created.id });
      }

      const turn = await api.sendChatMessage(targetSessionId, trimmed, language);
      setInput("");
      setMessages((prev) => [...prev, turn.user_message, turn.assistant_message]);
      setSessions((prev) => {
        const filtered = prev.filter((s) => s.id !== turn.session.id);
        return [turn.session, ...filtered];
      });
      if (turn.emergency_detected) {
        setEmergencyBanner(turn.emergency_banner);
        setEmergencyReasons(turn.emergency_reasons);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message.");
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    void sendText(input);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t("chat.title")}</h1>
          <p className="text-sm text-slate-600">{t("chat.sub")}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleNewSession}>
            <MessageSquarePlus className="h-4 w-4" /> {t("chat.newChat")}
          </Button>
          {activeSessionId && (
            <Button variant="outline" onClick={handleClearSession} disabled={messages.length === 0}>
              <Eraser className="h-4 w-4" /> {t("chat.clearChat")}
            </Button>
          )}
        </div>
      </div>

      <AiConfigNotice configured={aiConfigured} mode={aiMode} />

      {emergencyBanner && (
        <DisclaimerBanner
          variant="emergency"
          message={emergencyBanner}
          reasons={emergencyReasons}
        />
      )}

      <div className="grid gap-4 lg:grid-cols-12">
        <Card className="flex max-h-[650px] flex-col p-3 lg:col-span-4">
          <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
            {t("chat.history")}
          </p>
          {loadingSessions ? (
            <div className="flex flex-1 items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-medical-blue" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="px-2 py-6 text-sm text-slate-500">{t("chat.noSessions")}</p>
          ) : (
            <div className="flex-1 space-y-1.5 overflow-y-auto pr-1">
              {sessions.map((s) => (
                <div
                  key={s.id}
                  className={`group flex items-center justify-between gap-2 rounded-xl border p-2.5 transition-colors ${
                    activeSessionId === s.id
                      ? "border-medical-blue bg-blue-50/70"
                      : "border-transparent hover:bg-slate-50"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => {
                      setActiveSessionId(s.id);
                      setSearchParams({ session: s.id });
                    }}
                    className="min-w-0 flex-1 text-left"
                  >
                    <p className="truncate text-sm font-semibold text-slate-900">{s.title}</p>
                    <p className="text-xs text-slate-500">
                      {s.message_count} · {formatDateTime(s.updated_at)}
                    </p>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDeleteSession(s.id)}
                    className="rounded-lg p-1.5 text-slate-400 opacity-70 hover:bg-red-50 hover:text-red-600 group-hover:opacity-100"
                    aria-label="Delete conversation"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card className="flex h-[650px] flex-col overflow-hidden lg:col-span-8">
          <div className="flex-1 space-y-4 overflow-y-auto p-4 sm:p-6">
            {loadingMessages ? (
              <div className="flex h-full items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-medical-blue" />
              </div>
            ) : messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center space-y-5 text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-medical-blue">
                  <Sparkles className="h-7 w-7" />
                </div>
                <div className="max-w-md space-y-1">
                  <h2 className="text-lg font-bold text-slate-900">{t("chat.emptyTitle")}</h2>
                  <p className="text-sm text-slate-500">{t("chat.emptySub")}</p>
                </div>
                <div className="flex max-w-xl flex-wrap justify-center gap-2">
                  {suggestedQuestions.map((q) => (
                    <button
                      key={q}
                      type="button"
                      onClick={() => void sendText(q)}
                      className="rounded-full border border-blue-200 bg-blue-50/60 px-3.5 py-1.5 text-xs font-medium text-medical-blue transition hover:bg-blue-100"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => {
                const isUser = msg.role === "user";
                return (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
                  >
                    {!isUser && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-medical-blue to-medical-cyan text-white">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                        isUser
                          ? "bg-medical-blue text-white"
                          : "border border-slate-200 bg-slate-50/80 text-slate-800"
                      }`}
                    >
                      {msg.emergency_flagged && (
                        <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-red-600">
                          <AlertTriangle className="h-3.5 w-3.5" /> {t("chat.emergencyFlag")}
                        </div>
                      )}
                      {isUser ? (
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                      ) : (
                        <MarkdownRenderer content={msg.content} />
                      )}
                    </div>
                    {isUser && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-700">
                        <UserIcon className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                );
              })
            )}

            {sending && (
              <div className="flex items-center gap-3 text-sm text-slate-500">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-50 text-medical-blue">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
                <span>{t("chat.thinking")}</span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-slate-100 bg-white p-4">
            {error && (
              <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="flex items-end gap-2">
              <Textarea
                rows={2}
                placeholder={t("chat.placeholder")}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void sendText(input);
                  }
                }}
                className="min-h-[56px] resize-none"
              />
              <Button type="submit" disabled={sending || !input.trim()} className="h-12 px-4">
                {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </form>
            <p className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
              {t("chat.footerNote")} · {t("footer.compliance")}
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
