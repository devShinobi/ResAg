import json
import os
import re
from html import unescape
from typing import Any, Dict, List
from urllib.request import Request, urlopen

try:
    from springernature_api_client import SpringerNatureApiClient
except ImportError:  # pragma: no cover - optional dependency
    SpringerNatureApiClient = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)


class SpringerClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SPRINGER_API_KEY")

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not self.api_key or SpringerNatureApiClient is None:
            return self._demo_search(query, max_results=max_results)

        try:
            client = SpringerNatureApiClient(api_key=self.api_key)
            payload = client.search(query=query, limit=max_results)
            return parse_springer_results(payload)
        except Exception:
            return self._demo_search(query, max_results=max_results)

    def _demo_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        demo_papers = [
            {
                "title": "Insurance fraud detection using machine learning",
                "creators": [{"creator": "A. Rivera"}],
                "publicationName": "Springer Advances in Data Science",
                "publicationDate": "2023",
                "doi": "10.1007/s00100-023-00123-4",
                "url": [{"value": "https://example.com/insurance-fraud-ml"}],
                "abstract": "A review of machine learning methods for detecting insurance fraud from claims data.",
            },
            {
                "title": "Graph-based anomaly detection for insurance claims",
                "creators": [{"creator": "B. Chen"}],
                "publicationName": "Springer Journal of Applied Analytics",
                "publicationDate": "2022",
                "doi": "10.1007/s00200-022-00111-1",
                "url": [{"value": "https://example.com/insurance-graph-anomaly"}],
                "abstract": "A graph-based approach for identifying suspicious behavior patterns in insurance claims.",
            },
        ]
        if "insurance" not in query.lower():
            return []
        return parse_springer_results({"result": {"records": demo_papers[:max_results]}})


def parse_springer_results(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = payload.get("result", {}).get("records", [])
    papers: List[Dict[str, Any]] = []
    for record in records:
        url_value = record.get("url", [{}])[0].get("value") if record.get("url") else None
        papers.append(
            {
                "title": record.get("title"),
                "authors": [creator.get("creator") for creator in record.get("creators", []) if creator.get("creator")],
                "publication_name": record.get("publicationName"),
                "publication_date": record.get("publicationDate"),
                "doi": record.get("doi"),
                "url": url_value,
                "abstract": record.get("abstract"),
            }
        )
    return papers


def extract_text_from_html(html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_paper_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "ResAg/0.1"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="ignore")
    return extract_text_from_html(html)
