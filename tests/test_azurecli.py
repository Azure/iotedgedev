import pytest

from iotedgedev.azurecli import get_query_argument_for_id_and_name

pytestmark = pytest.mark.unit


def get_terms(query):
    # These tests are all asserting that the query contains two terms enclosed in
    # [?], separated by ||
    # They don't care about the order. Tests will fail if the square brackets and ||
    # contract is violated, but we'd want them to fail in that case.
    return query[2:len(query)-1].split(" || ")


def test_lowercase_token_should_be_lowercase_for_name_and_id():
    token = "abc123"
    query = get_query_argument_for_id_and_name(token)
    terms = get_terms(query)

    assert len(terms) == 2
    assert "starts_with(@.id,'abc123')" in terms
    assert "contains(@.name,'abc123')" in terms


def test_mixedcase_token_should_be_lowercase_for_id_but_unmodified_for_name():
    token = "AbC123"
    query = get_query_argument_for_id_and_name(token)
    terms = get_terms(query)

    assert len(terms) == 2
    assert "starts_with(@.id,'abc123')" in terms
    assert "contains(@.name,'AbC123')" in terms
