import json
import os
import re
import sqlite3
from collections import Counter
from typing import Any, Dict, List, Sequence


def _normalize_tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def deduplicate_papers(papers: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    deduped: List[Dict[str, Any]] = []
    for paper in papers:
        title = str(paper.get("title", "") or "").strip().lower()
        doi = str(paper.get("doi", "") or "").strip().lower()
        key = (title, doi) if title or doi else ("", "")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(paper))
    return deduped


def rank_papers(papers: Sequence[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    query_terms = set(_normalize_tokens(query))
    ranked: List[Dict[str, Any]] = []
    for paper in papers:
        text_blob = " ".join(
            [
                str(paper.get("title", "") or ""),
                str(paper.get("abstract", "") or ""),
                str(paper.get("publication_name", "") or ""),
            ]
        )
        tokens = _normalize_tokens(text_blob)
        overlap = sum(1 for token in tokens if token in query_terms)
        score = overlap + (len(query_terms & set(tokens)) * 0.5)
        paper_copy = dict(paper)
        paper_copy["relevance_score"] = round(score, 3)
        ranked.append(paper_copy)

    return sorted(ranked, key=lambda item: item.get("relevance_score", 0), reverse=True)


def store_papers(db_path: str, papers: Sequence[Dict[str, Any]], query: str) -> str:
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    unique_papers = deduplicate_papers(papers)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                authors TEXT,
                publication_name TEXT,
                publication_date TEXT,
                doi TEXT,
                url TEXT,
                abstract TEXT,
                query TEXT,
                relevance_score REAL
            )
            """
        )
        conn.execute("DELETE FROM papers WHERE query = ?", (query,))
        for paper in rank_papers(unique_papers, query=query):
            conn.execute(
                """
                INSERT INTO papers (
                    title, authors, publication_name, publication_date, doi, url, abstract, query, relevance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    paper.get("title"),
                    json.dumps(paper.get("authors", [])),
                    paper.get("publication_name"),
                    paper.get("publication_date"),
                    paper.get("doi"),
                    paper.get("url"),
                    paper.get("abstract"),
                    query,
                    paper.get("relevance_score", 0),
                ),
            )
        conn.commit()
    return db_path


def list_papers(db_path: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT title, authors, publication_name, publication_date, doi, url, abstract, query, relevance_score
            FROM papers
            ORDER BY id
            """
        ).fetchall()

    papers: List[Dict[str, Any]] = []
    for row in rows:
        papers.append(
            {
                "title": row[0],
                "authors": json.loads(row[1]) if row[1] else [],
                "publication_name": row[2],
                "publication_date": row[3],
                "doi": row[4],
                "url": row[5],
                "abstract": row[6],
                "query": row[7],
                "relevance_score": row[8],
            }
        )
    return papers


def export_papers(db_path: str, export_path: str) -> str:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT title, authors, publication_name, publication_date, doi, url, abstract, query, relevance_score
            FROM papers
            ORDER BY id
            """
        ).fetchall()

    papers: List[Dict[str, Any]] = []
    for row in rows:
        papers.append(
            {
                "title": row[0],
                "authors": json.loads(row[1]) if row[1] else [],
                "publication_name": row[2],
                "publication_date": row[3],
                "doi": row[4],
                "url": row[5],
                "abstract": row[6],
                "query": row[7],
                "relevance_score": row[8],
            }
        )

    os.makedirs(os.path.dirname(export_path) or ".", exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as handle:
        json.dump(papers, handle, indent=2)
    return export_path


def import_papers(db_path: str, export_path: str, query: str | None = None) -> str:
    with open(export_path, "r", encoding="utf-8") as handle:
        papers = json.load(handle)

    if query is not None:
        papers = [paper for paper in papers if paper.get("query") == query or not paper.get("query")]

    if not papers:
        store_papers(db_path, [], query=query or "imported")
        return db_path

    store_papers(db_path, papers, query=query or "imported")
    return db_path


def build_literature_summary(papers: Sequence[Dict[str, Any]], query: str) -> str:
    ranked = rank_papers(papers, query=query)
    top = ranked[:3]
    if not top:
        return f"No papers found for {query}."

    themes = Counter()
    for paper in top:
        for token in _normalize_tokens(paper.get("abstract", "") + " " + paper.get("title", "")):
            if token not in set(_normalize_tokens(query)) and len(token) > 4:
                themes[token] += 1

    theme_list = ", ".join([word for word, _ in themes.most_common(8)])
    sections = [
        f"Literature review summary for '{query}':",
        "",
        "Key themes:",
        f"- {theme_list or 'No additional themes detected'}",
        "",
        "Representative studies:",
    ]
    for paper in top:
        title = paper.get("title", "Untitled")
        abstract = paper.get("abstract", "")
        sections.append(f"- {title}: {abstract[:220]}{'...' if len(abstract) > 220 else ''}")

    return "\n".join(sections)
