import pytest
from typing import List, Tuple


class TestDependenciesValidation:
    """Test para verificar que todas las dependencias estén instaladas y disponibles."""
    
    def test_core_dependencies_available(self) -> None:
        """Verificar que todas las dependencias principales estén disponibles."""
        core_dependencies = [
            ("telegram", "python-telegram-bot"),
            ("ffmpeg", "ffmpeg-python"),
            ("cv2", "opencv-python"),
            ("numpy", "numpy"),
            ("PIL", "pillow"),
            ("pydantic", "pydantic"),
            ("dotenv", "python-dotenv"),
            ("psutil", "psutil"),
        ]
        
        missing_dependencies = self._check_dependencies(core_dependencies)
        
        if missing_dependencies:
            missing_list = ", ".join(missing_dependencies)
            pytest.fail(
                f"Las siguientes dependencias principales no están disponibles: {missing_list}. "
                f"Ejecuta 'uv sync' para instalar todas las dependencias."
            )
    
    def test_dev_dependencies_available(self) -> None:
        """Verificar que todas las dependencias de desarrollo estén disponibles."""
        dev_dependencies = [
            ("pytest", "pytest"),
            ("pytest_asyncio", "pytest-asyncio"),
        ]
        
        missing_dependencies = self._check_dependencies(dev_dependencies)
        
        if missing_dependencies:
            missing_list = ", ".join(missing_dependencies)
            pytest.fail(
                f"Las siguientes dependencias de desarrollo no están disponibles: {missing_list}. "
                f"Ejecuta 'uv sync --dev' para instalar dependencias de desarrollo."
            )
    
    def _check_dependencies(self, dependencies: List[Tuple[str, str]]) -> List[str]:
        """Verificar lista de dependencias y retornar las que faltan."""
        missing = []
        
        for import_name, package_name in dependencies:
            try:
                __import__(import_name)
            except ImportError:
                missing.append(package_name)
        
        return missing
    
    def test_python_version_compatibility(self) -> None:
        """Verificar que la versión de Python sea compatible."""
        import sys
        
        python_version = sys.version_info
        required_major, required_minor = 3, 11
        
        if python_version.major < required_major or (
            python_version.major == required_major and python_version.minor < required_minor
        ):
            pytest.fail(
                f"Python {required_major}.{required_minor}+ es requerido. "
                f"Versión actual: {python_version.major}.{python_version.minor}.{python_version.micro}"
            )