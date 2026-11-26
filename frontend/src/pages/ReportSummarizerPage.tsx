import { DragEvent, useEffect, useState } from "react";
import {
  Download,
  FileText,
  Loader2,
  Sparkles,
  Trash2,
  UploadCloud,
} from "lucide-react";
import { AiConfigNotice } from "@/components/AiConfigNotice";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useBlobUrl } from "@/hooks/useBlobUrl";
import { api, downloadProtectedFile } from "@/services/api";
import type { LabMarker, MedicalReport } from "@/types/api";
import { formatBytes, formatDateTime } from "@/utils/format";

const ALLOWED_EXT = [".pdf", ".jpg", ".jpeg", ".png"];

function statusBadgeVariant(status: LabMarker["status"]) {
  if (status === "high") return "danger";
  if (status === "low") return "warning";
  if (status === "normal") return "success";
  return "neutral";
}

export function ReportSummarizerPage() {
  const [reports, setReports] = useState<MedicalReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<MedicalReport | null>(null);
  const [aiConfigured, setAiConfigured] = useState(true);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [summarizing, setSummarizing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const previewPath = selectedReport ? `/api/reports/${selectedReport.id}/file` : null;
  const { blobUrl, loading: previewLoading } = useBlobUrl(previewPath);

  useEffect(() => {
    Promise.all([api.listReports(), api.health()])
      .then(([list, health]) => {
        setReports(list);
        setAiConfigured(health.ai_configured);
        if (list.length > 0) setSelectedReport(list[0]);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load reports."))
      .finally(() => setLoading(false));
  }, []);

  const handleFileUpload = async (file: File) => {
    setError(null);
    const lower = file.name.toLowerCase();
    if (!ALLOWED_EXT.some((ext) => lower.endsWith(ext))) {
      setError("Unsupported file format. Please upload a PDF, JPG, JPEG, or PNG report.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    try {
      const created = await api.uploadReport(file, setUploadProgress);
      setReports((prev) => [created, ...prev]);
      setSelectedReport(created);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void handleFileUpload(file);
  };

  const handleSummarize = async (reportId: string) => {
    setError(null);
    setSummarizing(true);
    try {
      const updated = await api.summarizeReport(reportId);
      setReports((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      setSelectedReport(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to summarize medical report.");
    } finally {
      setSummarizing(false);
    }
  };

  const handleDelete = async (reportId: string) => {
    setError(null);
    try {
      await api.deleteReport(reportId);
      const remaining = reports.filter((r) => r.id !== reportId);
      setReports(remaining);
      if (selectedReport?.id === reportId) {
        setSelectedReport(remaining[0] || null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete report.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2.5 text-2xl font-bold text-slate-900">
          <FileText className="h-6 w-6 text-medical-blue" /> Medical Report Summarizer
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Upload PDF, JPG, JPEG, or PNG reports to extract text, inspect lab markers against
          report-supplied reference ranges, and generate plain-English summaries.
        </p>
      </div>

      <AiConfigNotice configured={aiConfigured} />

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <Card>
        <CardContent className="p-6">
          <label
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
              dragging
                ? "border-medical-blue bg-blue-50/70"
                : "border-blue-200 bg-slate-50/60 hover:border-medical-blue"
            }`}
          >
            <UploadCloud className="h-10 w-10 text-medical-blue" />
            <p className="mt-3 text-sm font-semibold text-slate-900">
              Drag & drop a medical report here, or click to browse
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Accepted formats: PDF, JPG, JPEG, PNG (Max 10 MB)
            </p>
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void handleFileUpload(file);
                e.currentTarget.value = "";
              }}
            />
          </label>

          {uploading && (
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-xs font-medium text-slate-600">
                <span>Uploading and extracting report text...</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} />
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle className="text-base">Your Uploaded Reports</CardTitle>
            <CardDescription>Select a report to view preview & summary</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {loading ? (
              <div className="flex justify-center py-6">
                <Loader2 className="h-5 w-5 animate-spin text-medical-blue" />
              </div>
            ) : reports.length === 0 ? (
              <p className="text-sm text-slate-500">No medical reports uploaded yet.</p>
            ) : (
              reports.map((report) => (
                <div
                  key={report.id}
                  className={`flex items-center justify-between gap-2 rounded-xl border p-3 ${
                    selectedReport?.id === report.id
                      ? "border-medical-blue bg-blue-50/60"
                      : "border-slate-100 hover:bg-slate-50"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => setSelectedReport(report)}
                    className="min-w-0 flex-1 text-left"
                  >
                    <p className="truncate text-sm font-semibold text-slate-900">
                      {report.original_filename}
                    </p>
                    <p className="text-xs text-slate-500">
                      {formatBytes(report.file_size_bytes)} · {formatDateTime(report.created_at)}
                    </p>
                  </button>
                  <Badge variant={report.summary ? "success" : "neutral"}>{report.status}</Badge>
                  <button
                    type="button"
                    onClick={() => handleDelete(report.id)}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
                    aria-label="Delete report"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <div className="space-y-6 lg:col-span-8">
          {!selectedReport ? (
            <Card className="p-8 text-center text-sm text-slate-500">
              Upload or select a medical report to preview extracted values and generate an AI
              educational summary.
            </Card>
          ) : (
            <>
              <Card>
                <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle>{selectedReport.original_filename}</CardTitle>
                    <CardDescription>
                      Extraction: {selectedReport.extraction_method} ·{" "}
                      {formatBytes(selectedReport.file_size_bytes)}
                    </CardDescription>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        void downloadProtectedFile(
                          `/api/reports/${selectedReport.id}/file`,
                          selectedReport.original_filename
                        )
                      }
                    >
                      <Download className="h-4 w-4" /> Original
                    </Button>
                    {selectedReport.summary && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          void downloadProtectedFile(
                            `/api/reports/${selectedReport.id}/summary/download`,
                            `${selectedReport.original_filename}_summary.md`
                          )
                        }
                      >
                        <Download className="h-4 w-4" /> Summary (.md)
                      </Button>
                    )}
                    <Button
                      size="sm"
                      onClick={() => void handleSummarize(selectedReport.id)}
                      disabled={summarizing}
                    >
                      {summarizing ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" /> Summarizing...
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-4 w-4" />
                          {selectedReport.summary ? "Regenerate AI Summary" : "Summarize with AI"}
                        </>
                      )}
                    </Button>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Secure File Preview
                    </p>
                    {previewLoading ? (
                      <div className="flex h-48 items-center justify-center">
                        <Loader2 className="h-5 w-5 animate-spin text-medical-blue" />
                      </div>
                    ) : blobUrl ? (
                      selectedReport.mime_type === "application/pdf" ? (
                        <iframe
                          src={blobUrl}
                          title={selectedReport.original_filename}
                          className="h-72 w-full rounded-lg border border-slate-200 bg-white"
                        />
                      ) : (
                        <img
                          src={blobUrl}
                          alt={selectedReport.original_filename}
                          className="mx-auto max-h-72 rounded-lg object-contain"
                        />
                      )
                    ) : (
                      <p className="text-xs text-slate-500">Preview unavailable.</p>
                    )}
                  </div>

                  <div>
                    <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Extracted Report Text
                    </p>
                    {selectedReport.extracted_text ? (
                      <pre className="max-h-44 overflow-auto whitespace-pre-wrap rounded-xl border border-slate-200 bg-white p-3 font-mono text-xs text-slate-700">
                        {selectedReport.extracted_text}
                      </pre>
                    ) : (
                      <p className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                        No embedded text was found. For scanned PDFs or images, configure{" "}
                        <code>OPENAI_API_KEY</code> (Vision OCR) or install Tesseract OCR.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {selectedReport.summary && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>AI Educational Report Summary</CardTitle>
                      {selectedReport.summary.ai_model && (
                        <Badge>{selectedReport.summary.ai_model}</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-5 text-sm text-slate-700">
                    <div className="rounded-xl bg-blue-50/70 p-4 leading-relaxed">
                      {selectedReport.summary.plain_summary}
                    </div>

                    {selectedReport.summary.lab_markers.length > 0 && (
                      <div>
                        <h3 className="mb-2 font-semibold text-slate-900">
                          Laboratory Markers (Using Report-Supplied Reference Ranges Only)
                        </h3>
                        <div className="overflow-x-auto rounded-xl border border-slate-200">
                          <table className="w-full text-left text-xs sm:text-sm">
                            <thead className="bg-slate-50 text-slate-600">
                              <tr>
                                <th className="p-3 font-semibold">Marker</th>
                                <th className="p-3 font-semibold">Value</th>
                                <th className="p-3 font-semibold">Reference Range</th>
                                <th className="p-3 font-semibold">Status</th>
                                <th className="p-3 font-semibold">Simple Explanation</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {selectedReport.summary.lab_markers.map((marker, idx) => (
                                <tr key={idx}>
                                  <td className="p-3 font-medium text-slate-900">{marker.name}</td>
                                  <td className="p-3">
                                    {marker.value} {marker.unit}
                                  </td>
                                  <td className="p-3 text-slate-600">{marker.reference_range}</td>
                                  <td className="p-3">
                                    <Badge variant={statusBadgeVariant(marker.status)}>
                                      {marker.status.toUpperCase()}
                                    </Badge>
                                  </td>
                                  <td className="p-3 text-slate-600">{marker.explanation}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    {selectedReport.summary.medical_terms.length > 0 && (
                      <div>
                        <h3 className="mb-2 font-semibold text-slate-900">Medical Terms Explained</h3>
                        <div className="grid gap-2.5 sm:grid-cols-2">
                          {selectedReport.summary.medical_terms.map((item, idx) => (
                            <div key={idx} className="rounded-xl border border-slate-200 p-3">
                              <p className="font-semibold text-slate-900">{item.term}</p>
                              <p className="mt-1 text-xs text-slate-600">
                                {item.simple_explanation}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedReport.summary.questions_for_doctor.length > 0 && (
                      <div>
                        <h3 className="mb-1.5 font-semibold text-slate-900">
                          Questions to Ask Your Doctor
                        </h3>
                        <ul className="list-disc space-y-1 pl-5">
                          {selectedReport.summary.questions_for_doctor.map((q, idx) => (
                            <li key={idx}>{q}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <DisclaimerBanner message={selectedReport.summary.disclaimer} />
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
