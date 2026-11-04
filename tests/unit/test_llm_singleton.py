"""Unit tests for EnhancedLLMSingleton, SimpleMockLLM, get_singleton_llm."""

import os
import pytest
from core.llm_singleton import (
    EnhancedLLMSingleton,
    SimpleMockLLM,
    get_singleton_llm,
    get_langchain_llm,
    get_llm,
)


class TestSimpleMockLLM:
    def test_create_mock_llm(self):
        llm = SimpleMockLLM()
        assert llm is not None

    def test_mock_llm_call(self):
        llm = SimpleMockLLM()
        response = llm("Tell me about sales")
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Mock" in response

    def test_mock_llm_custom_name(self):
        llm = SimpleMockLLM(model_name="test_model")
        response = llm("Hello")
        assert "test_model" in response

    def test_mock_llm_type(self):
        llm = SimpleMockLLM()
        assert "mock" in llm._llm_type

    def test_mock_supports_stop_words(self):
        llm = SimpleMockLLM()
        assert llm.supports_stop_words() is True

    def test_mock_lower(self):
        llm = SimpleMockLLM()
        result = llm.lower()
        assert isinstance(result, str)


class TestEnhancedLLMSingleton:
    def test_singleton_pattern(self):
        s1 = EnhancedLLMSingleton()
        s2 = EnhancedLLMSingleton()
        assert s1 is s2

    def test_get_llm_mock_mode(self):
        singleton = EnhancedLLMSingleton()
        llm = singleton.get_llm()
        assert llm is not None

    def test_get_llm_task_type(self):
        singleton = EnhancedLLMSingleton()
        llm = singleton.get_llm(task_type="coding")
        assert llm is not None

    def test_model_configs_exist(self):
        assert "general" in EnhancedLLMSingleton.MODEL_CONFIGS
        assert "coding" in EnhancedLLMSingleton.MODEL_CONFIGS
        assert "analysis" in EnhancedLLMSingleton.MODEL_CONFIGS
        assert "creative" in EnhancedLLMSingleton.MODEL_CONFIGS

    def test_reset(self):
        singleton = EnhancedLLMSingleton()
        singleton.get_llm()
        singleton.reset()
        assert singleton._llm_instances == {}


class TestGetSingletonLLM:
    def test_get_singleton_llm_default(self):
        llm = get_singleton_llm()
        assert llm is not None

    def test_get_singleton_llm_with_task_type(self):
        llm = get_singleton_llm(task_type="creative")
        assert llm is not None

    def test_get_langchain_llm_alias(self):
        llm = get_langchain_llm()
        assert llm is not None

    def test_get_llm_alias(self):
        llm = get_llm()
        assert llm is not None

    def test_provider_env_var(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "mock")
        llm = get_singleton_llm()
        assert llm is not None

    def test_llm_is_callable(self):
        llm = get_singleton_llm()
        response = llm("Hello")
        assert isinstance(response, str)
