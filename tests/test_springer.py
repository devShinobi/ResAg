from resag.springer import parse_springer_results


def test_parse_springer_results_extracts_metadata():
    sample_payload = {
        "query": {"apiKey": "demo"},
        "result": {
            "records": [
                {
                    "title": "Fraud detection in insurance claims using machine learning",
                    "creators": [{"creator": "Jane Doe"}, {"creator": "John Smith"}],
                    "publicationName": "Springer Nature Journal",
                    "publicationDate": "2024-01-01",
                    "doi": "10.1007/s00100-024-00123-4",
                    "url": [{"value": "https://link.springer.com/article/10.1007/s00100-024-00123-4"}],
                    "abstract": "A review of fraud detection techniques for insurance claims.",
                }
            ]
        },
    }

    papers = parse_springer_results(sample_payload)

    assert len(papers) == 1
    assert papers[0]["title"] == "Fraud detection in insurance claims using machine learning"
    assert papers[0]["authors"] == ["Jane Doe", "John Smith"]
    assert papers[0]["doi"] == "10.1007/s00100-024-00123-4"
