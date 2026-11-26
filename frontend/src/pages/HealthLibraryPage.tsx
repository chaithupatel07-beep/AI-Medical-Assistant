import { useEffect, useState } from "react";
import { BookOpen, ExternalLink, Loader2, Search, X } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { DisclaimerBanner } from "@/components/DisclaimerBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useLanguage } from "@/hooks/useLanguage";
import { api } from "@/services/api";
import type { LibraryArticle } from "@/types/api";

export function HealthLibraryPage() {
  const { language, t } = useLanguage();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialCategory = searchParams.get("category") || "All";

  const [categories, setCategories] = useState<string[]>([]);
  const [categoryLabels, setCategoryLabels] = useState<Record<string, string>>({});
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [query, setQuery] = useState("");
  const [articles, setArticles] = useState<LibraryArticle[]>([]);
  const [activeArticle, setActiveArticle] = useState<LibraryArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .listLibraryArticles(selectedCategory, query, language)
      .then((res) => {
        setCategories(res.categories);
        setCategoryLabels(res.category_labels || {});
        setArticles(res.articles);
        if (activeArticle) {
          const updated = res.articles.find((a) => a.id === activeArticle.id);
          if (updated) setActiveArticle(updated);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load library."))
      .finally(() => setLoading(false));
  }, [selectedCategory, query, language]);

  const selectCategory = (cat: string) => {
    setSelectedCategory(cat);
    if (cat === "All") {
      searchParams.delete("category");
      setSearchParams(searchParams);
    } else {
      setSearchParams({ category: cat });
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-6 sm:px-0">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2.5 text-2xl font-bold text-slate-900 sm:text-3xl">
            <BookOpen className="h-7 w-7 text-medical-blue" /> {t("lib.title")}
          </h1>
          <p className="mt-1 text-sm text-slate-600">{t("lib.sub")}</p>
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input
            placeholder={t("lib.search")}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {["All", ...categories].map((cat) => (
          <Button
            key={cat}
            size="sm"
            variant={selectedCategory === cat ? "default" : "outline"}
            onClick={() => selectCategory(cat)}
          >
            {cat === "All" ? t("lib.all") : categoryLabels[cat] || cat}
          </Button>
        ))}
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-[220px] items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-medical-blue" />
        </div>
      ) : articles.length === 0 ? (
        <Card className="p-8 text-center text-sm text-slate-500">{t("lib.none")}</Card>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <Card key={article.id} className="flex flex-col justify-between hover:shadow-soft">
              <CardHeader>
                <div className="flex items-center justify-between gap-2">
                  <Badge variant="cyan">{article.category_label || article.category}</Badge>
                  <span className="text-xs text-slate-500">{article.read_time}</span>
                </div>
                <CardTitle className="mt-2 text-lg">{article.title}</CardTitle>
                <CardDescription className="line-clamp-3">{article.summary}</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-2 pt-2">
                <span className="text-xs font-medium text-slate-500">{article.source_name}</span>
                <Button size="sm" variant="secondary" onClick={() => setActiveArticle(article)}>
                  {t("lib.readArticle")}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {activeArticle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                <Badge variant="cyan">{activeArticle.category_label || activeArticle.category}</Badge>
                <h2 className="text-2xl font-bold text-slate-900">{activeArticle.title}</h2>
                <p className="text-xs text-slate-500">
                  {activeArticle.read_time} · {activeArticle.source_name}
                </p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setActiveArticle(null)}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="mt-5 space-y-4 text-sm leading-relaxed text-slate-700">
              {activeArticle.content.split("\n\n").map((para, idx) => (
                <p key={idx}>{para}</p>
              ))}

              <div className="rounded-xl bg-blue-50/70 p-4">
                <h3 className="font-semibold text-slate-900">{t("lib.takeaways")}</h3>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  {activeArticle.key_takeaways.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4">
                <h3 className="font-semibold text-amber-900">{t("lib.whenDoctor")}</h3>
                <p className="mt-1 text-amber-900">{activeArticle.when_to_see_doctor}</p>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
                <a
                  href={activeArticle.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm font-semibold text-medical-blue hover:underline"
                >
                  {t("lib.openSource")} ({activeArticle.source_name}) <ExternalLink className="h-4 w-4" />
                </a>
                <Button variant="outline" onClick={() => setActiveArticle(null)}>
                  {t("lib.close")}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <DisclaimerBanner />
    </div>
  );
}
