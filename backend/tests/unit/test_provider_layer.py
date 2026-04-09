import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import asyncio

from app.providers.factory import create_provider


def test_create_provider_mock_default_mode():
    provider = create_provider(mode="mock")
    response = asyncio.run(provider.generate("hello"))

    assert response.text == "Mock response"
    assert response.metadata["source"] == "mock"


def test_create_provider_invalid_mode():
    try:
        create_provider(mode="invalid")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unsupported PROVIDER_MODE" in str(exc)
