import sqlite3

from resag.agent import build_literature_summary, rank_papers, store_papers
from resag.springer import SpringerClient


def test_store_and_rank_papers(tmp_path):
    db_path = tmp_path / "papers.db"
    papers = [
        {
            "title": "Fraud detection in insurance claims using machine learning",
            "abstract": "This paper studies machine learning for fraud detection in insurance claims.",
            "authors": ["Jane Doe"],
            "doi": "10.1000/abc",
            "url": "https://example.com/1",
        },
        {
            "title": "Climate modeling with neural networks",
            "abstract": "This paper explores neural networks for climate modeling.",
            "authors": ["John Smith"],
            "doi": "10.1000/def",
            "url": "https://example.com/2",
        },
    ]

    store_papers(str(db_path), papers, query="insurance fraud detection")

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT title, relevance_score FROM papers ORDER BY relevance_score DESC").fetchall()

    assert rows[0][0] == "Fraud detection in insurance claims using machine learning"
    assert rows[0][1] >= rows[1][1]

    ranked = rank_papers(papers, query="insurance fraud detection")
    assert ranked[0]["title"] == "Fraud detection in insurance claims using machine learning"


def test_build_literature_summary_includes_key_points():
    papers = [
        {
            "title": "Fraud detection in insurance claims",
            "abstract": "Uses anomaly detection and supervised learning to detect suspicious claims.",
        },
        {
            "title": "Graph-based fraud analysis",
            "abstract": "Uses graph neural networks to model suspicious behavior patterns.",
        },
    ]

    summary = build_literature_summary(papers, query="insurance fraud detection")

    assert "insurance fraud detection" in summary.lower()
    assert "Fraud detection in insurance claims" in summary
    assert "Graph-based fraud analysis" in summary


def test_demo_search_is_available_without_api_key():
    client = SpringerClient(api_key=None)
    papers = client.search("insurance fraud detection", max_results=2)

    assert len(papers) >= 1
    assert any("insurance" in paper["title"].lower() for paper in papers)
