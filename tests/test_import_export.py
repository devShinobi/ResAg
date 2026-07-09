import json
from pathlib import Path

from resag.agent import export_papers, import_papers, store_papers
from resag.cli import main


def test_export_and_import_papers(tmp_path):
    db_path = tmp_path / "papers.db"
    export_path = tmp_path / "papers.json"

    papers = [
        {
            "title": "Fraud detection in insurance claims",
            "abstract": "Uses machine learning to detect suspicious claims.",
            "authors": ["A. Lee"],
            "doi": "10.1000/abc",
            "url": "https://example.com/1",
        }
    ]

    store_papers(str(db_path), papers, query="insurance fraud detection")
    export_papers(str(db_path), str(export_path))

    exported = json.loads(export_path.read_text())
    assert exported[0]["title"] == "Fraud detection in insurance claims"

    imported_db = tmp_path / "restored.db"
    import_papers(str(imported_db), str(export_path), query="insurance fraud detection")

    restored_export = str(tmp_path / "restored.json")
    export_papers(str(imported_db), restored_export)
    imported = json.loads(Path(restored_export).read_text())
    assert imported[0]["title"] == "Fraud detection in insurance claims"


def test_cli_supports_import_and_list(tmp_path, capsys):
    export_path = tmp_path / "papers.json"
    db_path = tmp_path / "papers.db"
    imported_db = tmp_path / "imported.db"

    papers = [{
        "title": "Fraud detection in insurance claims",
        "abstract": "Uses machine learning to detect suspicious claims.",
        "authors": ["A. Lee"],
        "doi": "10.1000/abc",
        "url": "https://example.com/1",
    }]

    store_papers(str(db_path), papers, query="insurance fraud detection")
    export_papers(str(db_path), str(export_path))

    main(["insurance fraud detection", "--db-path", str(imported_db), "--import-from", str(export_path)])
    main(["insurance fraud detection", "--db-path", str(imported_db), "--list"])

    captured = capsys.readouterr()
    assert "Fraud detection in insurance claims" in captured.out


def test_cli_export_without_path_uses_default(tmp_path, capsys):
    db_path = tmp_path / "papers.db"
    store_papers(str(db_path), [{
        "title": "Fraud detection in insurance claims",
        "abstract": "Uses machine learning to detect suspicious claims.",
        "authors": ["A. Lee"],
        "doi": "10.1000/abc",
        "url": "https://example.com/1",
    }], query="insurance fraud detection")

    main(["insurance fraud detection", "--db-path", str(db_path), "--export"])

    captured = capsys.readouterr()
    assert "Exported papers" in captured.out


def test_cli_import_without_path_uses_default(tmp_path, capsys, monkeypatch):
    export_path = tmp_path / "papers_import.json"
    export_path.write_text(json.dumps([{
        "title": "Fraud detection in insurance claims",
        "abstract": "Uses machine learning to detect suspicious claims.",
        "authors": ["A. Lee"],
        "doi": "10.1000/abc",
        "url": "https://example.com/1",
        "query": "insurance fraud detection",
    }]))
    monkeypatch.chdir(tmp_path)

    imported_db = tmp_path / "imported.db"
    main(["insurance fraud detection", "--db-path", str(imported_db), "--import-from"])

    captured = capsys.readouterr()
    assert "Imported papers" in captured.out
