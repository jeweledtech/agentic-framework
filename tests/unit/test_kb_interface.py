"""Unit tests for KnowledgeBaseInterface, MockKnowledgeBaseInterface."""

import pytest
from knowledge_bases.kb_interface import (
    KnowledgeBaseInterface,
    MockKnowledgeBaseInterface,
    get_kb_interface,
)


class TestMockKnowledgeBaseInterface:
    def test_create_mock_kb(self):
        kb = MockKnowledgeBaseInterface("sales")
        assert kb.department == "sales"

    def test_list_categories(self):
        kb = MockKnowledgeBaseInterface("sales")
        categories = kb.list_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "Customer_Personas" in categories

    def test_get_document(self):
        kb = MockKnowledgeBaseInterface("sales")
        doc = kb.get_document("Customer_Personas")
        assert isinstance(doc, str)
        assert "ICP" in doc or "Ideal Customer" in doc

    def test_get_document_missing_category(self):
        kb = MockKnowledgeBaseInterface("sales")
        doc = kb.get_document("Nonexistent_Category")
        assert "not found" in doc.lower()

    def test_search_knowledge_base(self):
        kb = MockKnowledgeBaseInterface("sales")
        results = kb.search_knowledge_base("icp coaching business")
        assert isinstance(results, dict)
        assert len(results) > 0

    def test_search_generic_query(self):
        kb = MockKnowledgeBaseInterface("sales")
        results = kb.search_knowledge_base("random query with no keywords")
        assert isinstance(results, dict)
        assert len(results) > 0  # Returns generic fallback

    def test_query_alias(self):
        kb = MockKnowledgeBaseInterface("sales")
        results = kb.query("competitor analysis")
        assert isinstance(results, dict)

    def test_search_competitor(self):
        kb = MockKnowledgeBaseInterface("sales")
        results = kb.search_knowledge_base("competitor analysis")
        assert "Competitor_Insights" in results


class TestGetKBInterface:
    def test_get_kb_interface_mock(self):
        kb = get_kb_interface("sales")
        assert kb is not None
        # In mock mode, should return MockKnowledgeBaseInterface
        assert isinstance(kb, (KnowledgeBaseInterface, MockKnowledgeBaseInterface))

    def test_get_kb_interface_different_departments(self):
        for dept in ["sales", "marketing", "product", "customer"]:
            kb = get_kb_interface(dept)
            assert kb is not None
            assert isinstance(kb.list_categories(), list)
