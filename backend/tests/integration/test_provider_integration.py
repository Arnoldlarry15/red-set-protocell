import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import asyncio

from app.providers.factory import create_provider


def test_provider_mock_mode_pipeline_behavior():
    provider = create_provider(mode="mock", mock_text="Integration mock response")
    response = asyncio.run(provider.generate("pipeline prompt"))

    assert response.text == "Integration mock response"
    assert response.metadata["source"] == "mock"
    assert response.metadata["prompt_length"] == len("pipeline prompt")
