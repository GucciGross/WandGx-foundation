from web_research import SearchResult


def test_search_result_dict_shape():
    result = SearchResult(title="Example", url="https://example.com", snippet="Demo")
    assert result.to_dict()["title"] == "Example"
    assert result.to_dict()["provider"] == "searxng"
