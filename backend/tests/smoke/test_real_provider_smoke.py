import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("PROVIDER_MODE", "mock").lower() != "real" or not os.environ.get("OPENAI_API_KEY", ""),
    reason="Real provider smoke requires PROVIDER_MODE=real and OPENAI_API_KEY",
)


def test_real_provider_smoke_placeholder():
    # Real smoke behavior is exercised in tests/test_real_backends.py with retry/timeout.
    assert True
