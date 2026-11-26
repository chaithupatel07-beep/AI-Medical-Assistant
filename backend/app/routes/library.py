"""Health Information Library routes with English, Telugu, and Hindi support."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.safety import normalize_language
from app.services.library_data import ARTICLES, CATEGORIES, CATEGORY_LABELS, localize_article

router = APIRouter(prefix="/api/library", tags=["Health Library"])


@router.get("/categories")
def get_categories(lang: str = Query("en")):
    code = normalize_language(lang)
    return {
        "categories": CATEGORIES,
        "category_labels": {cat: CATEGORY_LABELS[cat][code] for cat in CATEGORIES},
    }


@router.get("/articles")
def list_articles(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    lang: str = Query("en"),
):
    code = normalize_language(lang)
    localized = [localize_article(a, code) for a in ARTICLES]

    if category and category.lower() != "all":
        localized = [a for a in localized if str(a["category"]).lower() == category.lower()]

    if q and q.strip():
        needle = q.strip().lower()
        localized = [
            a
            for a in localized
            if needle in str(a["title"]).lower()
            or needle in str(a["summary"]).lower()
            or needle in str(a["content"]).lower()
            or needle in str(a["category"]).lower()
            or needle in str(a.get("category_label", "")).lower()
        ]

    return {
        "categories": CATEGORIES,
        "category_labels": {cat: CATEGORY_LABELS[cat][code] for cat in CATEGORIES},
        "articles": localized,
        "total": len(localized),
    }


@router.get("/articles/{article_id}")
def get_article(article_id: str, lang: str = Query("en")):
    code = normalize_language(lang)
    for article in ARTICLES:
        if article["id"] == article_id:
            return localize_article(article, code)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
