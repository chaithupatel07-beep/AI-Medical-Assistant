import { KeyRound } from "lucide-react";

export function AiConfigNotice({ configured }: { configured: boolean }) {
  if (configured) return null;
  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
      <KeyRound className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />
      <div>
        <p className="font-semibold">Server AI API Key Not Configured Yet</p>
        <p className="mt-0.5 text-amber-800">
          To enable live AI Chat, Symptom Guidance, Report Summarization, and Medical Image Vision
          Analysis, set <code className="rounded bg-amber-100 px-1.5 py-0.5">OPENAI_API_KEY</code>{" "}
          in <code className="rounded bg-amber-100 px-1.5 py-0.5">backend/.env</code> and restart
          the FastAPI server. API keys stay strictly on the server.
        </p>
      </div>
    </div>
  );
}
