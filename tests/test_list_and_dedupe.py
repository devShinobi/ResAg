from resag.agent import deduplicate_papers, list_papers, store_papers


def test_deduplicate_and_list_papers(tmp_path):
    db_path = tmp_path / "papers.db"
    papers = [
        {
            "title": "Fraud detection in insurance claims",
            "abstract": "Uses machine learning to detect suspicious claims.",
            "doi": "10.1000/abc",
        },
        {
            "title": "Fraud detection in insurance claims",
            "abstract": "Duplicate record",
            "doi": "10.1000/abc",
        },
        {
            "title": "Graph-based anomaly detection",
            "abstract": "A different paper",
            "doi": "10.1000/def",
        },
    ]

    store_papers(str(db_path), papers, query="insurance fraud detection")
    deduped = deduplicate_papers(papers)
    assert len(deduped) == 2

    rows = list_papers(str(db_path))
    assert len(rows) == 2
    assert rows[0]["title"] == "Fraud detection in insurance claims"
