import { FormEvent, useEffect, useState } from "react";
import { AlertTriangle, Eye, Image as ImageIcon, Loader2, Trash2, UploadCloud } from "lucide-react";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { useBlobUrl } from "@/hooks/useBlobUrl";
import { useLanguage } from "@/hooks/useLanguage";
import { api } from "@/services/api";
import type { MedicalImage } from "@/types/api";
import { formatBytes, formatDateTime } from "@/utils/format";

export function MedicalImagePage() {
  const { language, t } = useLanguage();
  const [images, setImages] = useState<MedicalImage[]>([]);
  const [selectedImage, setSelectedImage] = useState<MedicalImage | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [contextText, setContextText] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const previewPath = selectedImage ? `/api/images/${selectedImage.id}/file` : null;
  const { blobUrl, loading: previewLoading } = useBlobUrl(previewPath);

  useEffect(() => {
    api
      .listImages()
      .then((list) => {
        setImages(list);
        if (list.length > 0) setSelectedImage(list[0]);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load images."))
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!file) {
      setError("Please select a JPG, JPEG, or PNG image first.");
      return;
    }
    const lower = file.name.toLowerCase();
    if (![".jpg", ".jpeg", ".png"].some((ext) => lower.endsWith(ext))) {
      setError("Only JPG, JPEG, and PNG images are supported.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    try {
      const created = await api.uploadImage(file, contextText, setUploadProgress);
      setImages((prev) => [created, ...prev]);
      setSelectedImage(created);
      setFile(null);
      setContextText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Image upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (imageId: string) => {
    setError(null);
    setAnalyzing(true);
    try {
      const updated = await api.analyzeImage(imageId, language);
      setImages((prev) => prev.map((img) => (img.id === updated.id ? updated : img)));
      setSelectedImage(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Vision AI analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDelete = async (imageId: string) => {
    setError(null);
    try {
      await api.deleteImage(imageId);
      const remaining = images.filter((img) => img.id !== imageId);
      setImages(remaining);
      if (selectedImage?.id === imageId) {
        setSelectedImage(remaining[0] || null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete image.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2.5 text-2xl font-bold text-slate-900">
          <ImageIcon className="h-6 w-6 text-medical-blue" /> {t("img.title")}
        </h1>
        <p className="mt-1 text-sm text-slate-600">{t("img.sub")}</p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-12">
        <div className="space-y-6 lg:col-span-5">
          <Card>
            <CardHeader>
              <CardTitle>{t("img.uploadTitle")}</CardTitle>
              <CardDescription>{t("img.uploadSub")}</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpload} className="space-y-4">
                <label className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-blue-200 bg-slate-50/70 p-6 text-center hover:border-medical-blue">
                  <UploadCloud className="h-8 w-8 text-medical-blue" />
                  <p className="mt-2 text-sm font-medium text-slate-800">
                    {file ? file.name : t("img.choose")}
                  </p>
                  <p className="text-xs text-slate-500">
                    {file ? formatBytes(file.size) : t("img.validated")}
                  </p>
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </label>

                <div className="space-y-1.5">
                  <Label htmlFor="img-ctx">{t("img.context")}</Label>
                  <Textarea
                    id="img-ctx"
                    rows={2}
                    value={contextText}
                    onChange={(e) => setContextText(e.target.value)}
                  />
                </div>

                {uploading && <Progress value={uploadProgress} />}

                <Button type="submit" className="w-full" disabled={uploading || !file}>
                  {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("img.uploadBtn")}
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t("img.uploadedList")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {loading ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-medical-blue" />
                </div>
              ) : images.length === 0 ? (
                <p className="text-sm text-slate-500">{t("img.none")}</p>
              ) : (
                images.map((img) => (
                  <div
                    key={img.id}
                    className={`flex items-center justify-between gap-2 rounded-xl border p-3 ${
                      selectedImage?.id === img.id
                        ? "border-medical-blue bg-blue-50/60"
                        : "border-slate-100 hover:bg-slate-50"
                    }`}
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedImage(img)}
                      className="min-w-0 flex-1 text-left"
                    >
                      <p className="truncate text-sm font-semibold text-slate-900">
                        {img.original_filename}
                      </p>
                      <p className="text-xs text-slate-500">{formatDateTime(img.created_at)}</p>
                    </button>
                    <Badge variant={img.status === "analyzed" ? "success" : "neutral"}>
                      {img.status}
                    </Badge>
                    <button
                      type="button"
                      onClick={() => handleDelete(img.id)}
                      className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
                      aria-label="Delete image"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6 lg:col-span-7">
          {!selectedImage ? (
            <Card className="p-8 text-center text-sm text-slate-500">{t("img.empty")}</Card>
          ) : (
            <Card>
              <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle>{selectedImage.original_filename}</CardTitle>
                  <CardDescription>
                    {formatBytes(selectedImage.file_size_bytes)} ·{" "}
                    {selectedImage.image_context || "—"}
                  </CardDescription>
                </div>
                <Button onClick={() => void handleAnalyze(selectedImage.id)} disabled={analyzing}>
                  {analyzing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> {t("img.analyzing")}
                    </>
                  ) : (
                    <>
                      <Eye className="h-4 w-4" />
                      {selectedImage.status === "analyzed" ? t("img.reAnalyze") : t("img.analyze")}
                    </>
                  )}
                </Button>
              </CardHeader>

              <CardContent className="space-y-5">
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                  {previewLoading ? (
                    <div className="flex h-56 items-center justify-center">
                      <Loader2 className="h-5 w-5 animate-spin text-medical-blue" />
                    </div>
                  ) : blobUrl ? (
                    <img
                      src={blobUrl}
                      alt={selectedImage.original_filename}
                      className="mx-auto max-h-80 rounded-lg object-contain"
                    />
                  ) : (
                    <p className="text-center text-xs text-slate-500">Preview unavailable.</p>
                  )}
                </div>

                {selectedImage.analysis_summary && (
                  <div className="space-y-4 text-sm text-slate-700">
                    <div className="rounded-xl bg-blue-50/70 p-4">
                      <div className="mb-1 flex items-center justify-between">
                        <h3 className="font-semibold text-slate-900">{t("img.summaryTitle")}</h3>
                        {selectedImage.ai_model && <Badge>{selectedImage.ai_model}</Badge>}
                      </div>
                      <p className="leading-relaxed">{selectedImage.analysis_summary}</p>
                    </div>

                    {selectedImage.observations.length > 0 && (
                      <div>
                        <h3 className="mb-1.5 font-semibold text-slate-900">{t("img.obsTitle")}</h3>
                        <ul className="list-disc space-y-1 pl-5">
                          {selectedImage.observations.map((obs, idx) => (
                            <li key={idx}>{obs}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4">
                      <h3 className="flex items-center gap-1.5 font-semibold text-amber-900">
                        <AlertTriangle className="h-4 w-4" /> {t("img.limitsTitle")}
                      </h3>
                      <p className="mt-1 text-amber-900">{selectedImage.limitations}</p>
                    </div>

                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                      <h3 className="font-semibold text-slate-900">{t("img.nextTitle")}</h3>
                      <p className="mt-1">{selectedImage.recommended_next_steps}</p>
                    </div>
                  </div>
                )}

                <DisclaimerBanner message={selectedImage.disclaimer} />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
