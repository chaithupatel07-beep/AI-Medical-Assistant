"""Health Information Library routes."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.services.library_data import ARTICLES, CATEGORIES

router = APIRouter(prefix="/api/library", tags=["Health Library"])


@router.get("/categories")
def get_categories():
    return {"categories": CATEGORIES}


@router.get("/articles")
def list_articles(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    items = ARTICLES
    if category and category.lower() != "all":
        items = [a for a in items if str(a["category"]).lower() == category.lower()]
    if q and q.strip():
        needle = q.strip().lower()
        items = [
            a
            for a in items
            if needle in str(a["title"]).lower()
            or needle in str(a["summary"]).lower()
            or needle in str(a["content"]).lower()
            or needle in str(a["category"]).lower()
        ]
    return {"categories": CATEGORIES, "articles": items, "total": len(items)}


@router.get("/articles/{article_id}")
def get_article(article_id: str):
    for article in ARTICLES:
        if article["id"] == article_id:
            return article
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
