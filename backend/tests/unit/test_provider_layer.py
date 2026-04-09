import asyncio

import pytest

from app.providers.factory import create_provider


def test_create_provider_mock_default_mode():
    provider = create_provider(mode="mock")
    response = asyncio.run(provider.generate("hello"))

    assert response.text == "Mock response"
    assert response.metadata["source"] == "mock"


def test_create_provider_invalid_mode():
    with pytest.raises(ValueError, match="Unsupported PROVIDER_MODE"):
        create_provider(mode="invalid")
