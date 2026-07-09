# ResAg

ResAg is a lightweight research assistant for discovering scholarly papers and preparing them for literature review.

## Features
- Search Springer metadata for papers matching a topic such as "insurance fraud detection"
- Parse search results into structured paper records
- Extract readable text from downloaded HTML paper pages
- Provide a simple CLI for repeated research workflows

## Setup
```bash
cd /workspaces/ResAg
python -m pip install -r requirements.txt
```

## Usage
```bash
python -m resag.cli "insurance fraud detection" --max-results 5 --api-key YOUR_SPRINGER_API_KEY
```

## Notes
- A Springer API key is required for live searches.
- The current implementation is intentionally simple and can be extended to support more sources (e.g. arXiv, IEEE, PubMed) and local PDF parsing.
