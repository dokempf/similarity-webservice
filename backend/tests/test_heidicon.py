from similarity_webservice.heidicon import extract_heidicon_content


def test_extract_heidicon_content():
    images = extract_heidicon_content("DANAM Similarity Search")

    assert len(images) > 0
