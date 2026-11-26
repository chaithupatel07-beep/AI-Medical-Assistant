import { FormEvent, useEffect, useState } from "react";
import {
  Activity,
  Download,
  FileText,
  FolderHeart,
  Image as ImageIcon,
  Loader2,
  MessageSquareHeart,
  Shield,
  Trash2,
  User as UserIcon,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import type { LanguageCode } from "@/i18n/types";
import { api, downloadProtectedFile } from "@/services/api";
import type { ActivityItem, ChatSession, MedicalImage, MedicalReport } from "@/types/api";
import { formatBytes, formatDateTime } from "@/utils/format";
import { evaluatePassword } from "@/utils/validation";

export function PersonalHealthPage() {
  const { user, setUserDirect } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [reports, setReports] = useState<MedicalReport[]>([]);
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [images, setImages] = useState<MedicalImage[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [age, setAge] = useState(user?.profile?.age ? String(user.profile.age) : "");
  const [gender, setGender] = useState(user?.profile?.gender || "");
  const [bloodType, setBloodType] = useState(user?.profile?.blood_type || "");
  const [allergies, setAllergies] = useState(user?.profile?.allergies || "");
  const [chronicConditions, setChronicConditions] = useState(
    user?.profile?.chronic_conditions || ""
  );
  const [emergencyContact, setEmergencyContact] = useState(
    user?.profile?.emergency_contact || ""
  );
  const [preferredUnits, setPreferredUnits] = useState<"metric" | "imperial">(
    user?.profile?.preferred_units || "metric"
  );
  const [preferredLang, setPreferredLang] = useState<LanguageCode>(
    user?.profile?.preferred_language || language
  );
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);

  const loadAll = () => {
    setLoading(true);
    Promise.all([
      api.listReports(),
      api.listChatSessions(),
      api.listImages(),
      api.listActivity(50),
    ])
      .then(([r, c, i, a]) => {
        setReports(r);
        setChats(c);
        setImages(i);
        setActivities(a);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load records."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    setPreferredLang(language);
  }, [language]);

  useEffect(() => {
    if (!user) return;
    setFullName(user.full_name || "");
    setAge(user.profile?.age ? String(user.profile.age) : "");
    setGender(user.profile?.gender || "");
    setBloodType(user.profile?.blood_type || "");
    setAllergies(user.profile?.allergies || "");
    setChronicConditions(user.profile?.chronic_conditions || "");
    setEmergencyContact(user.profile?.emergency_contact || "");
    setPreferredUnits(user.profile?.preferred_units || "metric");
    if (user.profile?.preferred_language) {
      setPreferredLang(user.profile.preferred_language);
    }
  }, [user]);

  const handleSaveProfile = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setFeedback(null);
    setSavingProfile(true);
    try {
      const updated = await api.updateProfile({
        full_name: fullName.trim(),
        age: age.trim() ? Number(age) : null,
        gender: gender.trim() || null,
        blood_type: bloodType.trim() || null,
        allergies: allergies.trim() || null,
        chronic_conditions: chronicConditions.trim() || null,
        emergency_contact: emergencyContact.trim() || null,
        preferred_units: preferredUnits,
        preferred_language: preferredLang,
      });
      setUserDirect(updated);
      setLanguage(preferredLang);
      setFeedback("Personal health profile updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile.");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setFeedback(null);
    const pwEval = evaluatePassword(newPassword);
    if (!pwEval.valid) {
      setError(pwEval.message);
      return;
    }

    setSavingPassword(true);
    try {
      const res = await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setCurrentPassword("");
      setNewPassword("");
      setFeedback(res.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to change password.");
    } finally {
      setSavingPassword(false);
    }
  };

  const deleteReport = async (id: string) => {
    setError(null);
    try {
      await api.deleteReport(id);
      setReports((prev) => prev.filter((r) => r.id !== id));
      setFeedback("Medical report deleted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete report.");
    }
  };

  const deleteChat = async (id: string) => {
    setError(null);
    try {
      await api.deleteChatSession(id);
      setChats((prev) => prev.filter((c) => c.id !== id));
      setFeedback("Conversation deleted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete conversation.");
    }
  };

  const deleteImage = async (id: string) => {
    setError(null);
    try {
      await api.deleteImage(id);
      setImages((prev) => prev.filter((img) => img.id !== id));
      setFeedback("Medical image deleted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete image.");
    }
  };

  const deleteActivity = async (id: string) => {
    setError(null);
    try {
      await api.deleteActivity(id);
      setActivities((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete activity entry.");
    }
  };

  const clearActivity = async () => {
    setError(null);
    try {
      await api.clearActivity();
      setActivities([]);
      setFeedback("Activity history cleared.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to clear activity history.");
    }
  };

  const handleDownload = async (path: string, filename: string) => {
    setError(null);
    try {
      await downloadProtectedFile(path, filename);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to download file.");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2.5 text-2xl font-bold text-slate-900">
          <FolderHeart className="h-6 w-6 text-medical-blue" /> {t("rec.title")}
        </h1>
        <p className="mt-1 text-sm text-slate-600">{t("rec.sub")}</p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {feedback && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {feedback}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-[240px] items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-medical-blue" />
        </div>
      ) : (
        <Tabs defaultValue="reports">
          <TabsList>
            <TabsTrigger value="reports">{t("rec.tabReports")} ({reports.length})</TabsTrigger>
            <TabsTrigger value="chats">{t("rec.tabChats")} ({chats.length})</TabsTrigger>
            <TabsTrigger value="images">{t("rec.tabImages")} ({images.length})</TabsTrigger>
            <TabsTrigger value="activity">{t("rec.tabActivity")} ({activities.length})</TabsTrigger>
            <TabsTrigger value="profile">{t("rec.tabProfile")}</TabsTrigger>
          </TabsList>

          <TabsContent value="reports">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-medical-blue" /> {t("rec.uploadedReports")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {reports.length === 0 ? (
                  <p className="text-sm text-slate-500">{t("rep.none")}</p>
                ) : (
                  reports.map((report) => (
                    <div
                      key={report.id}
                      className="flex flex-col justify-between gap-3 rounded-xl border border-slate-200 p-4 sm:flex-row sm:items-center"
                    >
                      <div>
                        <p className="font-semibold text-slate-900">{report.original_filename}</p>
                        <p className="text-xs text-slate-500">
                          {formatBytes(report.file_size_bytes)} · {formatDateTime(report.created_at)}
                        </p>
                        {report.summary && (
                          <p className="mt-1 line-clamp-2 text-xs text-slate-600">
                            {report.summary.plain_summary}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant={report.summary ? "success" : "neutral"}>
                          {report.status}
                        </Badge>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            void handleDownload(
                              `/api/reports/${report.id}/file`,
                              report.original_filename
                            )
                          }
                        >
                          <Download className="h-3.5 w-3.5" /> {t("rep.original")}
                        </Button>
                        {report.summary && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              void handleDownload(
                                `/api/reports/${report.id}/summary/download`,
                                `${report.original_filename}_summary.md`
                              )
                            }
                          >
                            <Download className="h-3.5 w-3.5" /> {t("rep.summaryMd")}
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => void deleteReport(report.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="chats">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquareHeart className="h-5 w-5 text-medical-blue" /> {t("rec.savedChats")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {chats.length === 0 ? (
                  <p className="text-sm text-slate-500">{t("dash.noChats")}</p>
                ) : (
                  chats.map((chat) => (
                    <div
                      key={chat.id}
                      className="flex flex-col justify-between gap-3 rounded-xl border border-slate-200 p-4 sm:flex-row sm:items-center"
                    >
                      <div>
                        <p className="font-semibold text-slate-900">{chat.title}</p>
                        <p className="text-xs text-slate-500">
                          {chat.message_count} · {formatDateTime(chat.updated_at)}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="secondary" asChild>
                          <Link to={`/dashboard/chat?session=${chat.id}`}>{t("dash.openChat")}</Link>
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => void deleteChat(chat.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="images">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ImageIcon className="h-5 w-5 text-medical-blue" /> {t("rec.uploadedImages")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {images.length === 0 ? (
                  <p className="text-sm text-slate-500">{t("img.none")}</p>
                ) : (
                  images.map((img) => (
                    <div
                      key={img.id}
                      className="flex flex-col justify-between gap-3 rounded-xl border border-slate-200 p-4 sm:flex-row sm:items-center"
                    >
                      <div>
                        <p className="font-semibold text-slate-900">{img.original_filename}</p>
                        <p className="text-xs text-slate-500">
                          {formatBytes(img.file_size_bytes)} · {formatDateTime(img.created_at)}
                        </p>
                        {img.analysis_summary && (
                          <p className="mt-1 line-clamp-2 text-xs text-slate-600">
                            {img.analysis_summary}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={img.status === "analyzed" ? "success" : "neutral"}>
                          {img.status}
                        </Badge>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => void deleteImage(img.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activity">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-medical-blue" /> {t("rec.activityTitle")}
                  </CardTitle>
                  <CardDescription>{t("rec.activitySub")}</CardDescription>
                </div>
                {activities.length > 0 && (
                  <Button size="sm" variant="outline" onClick={() => void clearActivity()}>
                    {t("rec.clearHistory")}
                  </Button>
                )}
              </CardHeader>
              <CardContent className="space-y-2">
                {activities.length === 0 ? (
                  <p className="text-sm text-slate-500">—</p>
                ) : (
                  activities.map((act) => (
                    <div
                      key={act.id}
                      className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 p-3 text-sm"
                    >
                      <div>
                        <p className="font-medium text-slate-900">{act.description}</p>
                        <p className="text-xs text-slate-500">
                          {act.activity_type} · {formatDateTime(act.created_at)}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => void deleteActivity(act.id)}
                        className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
                        aria-label="Delete activity entry"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserIcon className="h-5 w-5 text-medical-blue" /> {t("rec.profileTitle")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSaveProfile} className="space-y-4">
                    <div className="space-y-1.5">
                      <Label htmlFor="prof-name">{t("auth.fullName")}</Label>
                      <Input
                        id="prof-name"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        required
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="space-y-1.5">
                        <Label htmlFor="prof-age">{t("sym.age").replace(" *", "")}</Label>
                        <Input
                          id="prof-age"
                          type="number"
                          min={0}
                          max={130}
                          value={age}
                          onChange={(e) => setAge(e.target.value)}
                        />
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="prof-gender">{t("sym.gender")}</Label>
                        <Input
                          id="prof-gender"
                          value={gender}
                          onChange={(e) => setGender(e.target.value)}
                        />
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="prof-blood">{t("dash.bloodTypeLabel")}</Label>
                        <Input
                          id="prof-blood"
                          placeholder="O+"
                          value={bloodType}
                          onChange={(e) => setBloodType(e.target.value)}
                        />
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="prof-allergies">{t("dash.allergiesLabel")}</Label>
                      <Textarea
                        id="prof-allergies"
                        rows={2}
                        value={allergies}
                        onChange={(e) => setAllergies(e.target.value)}
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="prof-cond">{t("rec.chronic")}</Label>
                      <Textarea
                        id="prof-cond"
                        rows={2}
                        value={chronicConditions}
                        onChange={(e) => setChronicConditions(e.target.value)}
                      />
                    </div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                      <div className="space-y-1.5">
                        <Label htmlFor="prof-emerg">{t("rec.emergencyContact")}</Label>
                        <Input
                          id="prof-emerg"
                          value={emergencyContact}
                          onChange={(e) => setEmergencyContact(e.target.value)}
                        />
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="prof-units">{t("rec.preferredUnits")}</Label>
                        <select
                          id="prof-units"
                          value={preferredUnits}
                          onChange={(e) =>
                            setPreferredUnits(e.target.value as "metric" | "imperial")
                          }
                          className="flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm"
                        >
                          <option value="metric">Metric</option>
                          <option value="imperial">Imperial</option>
                        </select>
                      </div>
                      <div className="space-y-1.5">
                        <Label htmlFor="prof-lang">{t("rec.preferredLang")}</Label>
                        <select
                          id="prof-lang"
                          value={preferredLang}
                          onChange={(e) => setPreferredLang(e.target.value as LanguageCode)}
                          className="flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm"
                        >
                          <option value="en">English</option>
                          <option value="te">తెలుగు (Telugu)</option>
                          <option value="hi">हिन्दी (Hindi)</option>
                        </select>
                      </div>
                    </div>
                    <Button type="submit" disabled={savingProfile}>
                      {savingProfile ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        t("rec.saveProfile")
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-medical-cyan" /> {t("rec.securityTitle")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div className="space-y-1.5">
                      <Label htmlFor="sec-cur">{t("rec.currentPw")}</Label>
                      <Input
                        id="sec-cur"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="sec-new">{t("rec.newPw")}</Label>
                      <Input
                        id="sec-new"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                      />
                    </div>
                    <Button type="submit" variant="cyan" disabled={savingPassword}>
                      {savingPassword ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        t("rec.updatePassword")
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
