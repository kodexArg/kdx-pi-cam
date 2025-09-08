import pytest
import os
from typing import Dict, Any
from unittest.mock import patch


@pytest.fixture
def mock_env_vars() -> Dict[str, str]:
    """Fixture con variables de entorno de prueba."""
    return {
        "RTSP_URL": "rtsp://test-camera:554/stream",
        "BOT_TOKEN": "1234567890:TEST_BOT_TOKEN_FOR_TESTING",
        "CHAT_ID": "-1001234567890"
    }


@pytest.fixture
def clean_env():
    """Fixture que limpia variables de entorno antes y después del test."""
    critical_vars = ["RTSP_URL", "BOT_TOKEN", "CHAT_ID"]
    
    # Guardar valores originales
    original_values = {}
    for var in critical_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restaurar valores originales
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def set_test_env(mock_env_vars):
    """Fixture que establece variables de entorno de prueba."""
    with patch.dict(os.environ, mock_env_vars):
        yield mock_env_vars