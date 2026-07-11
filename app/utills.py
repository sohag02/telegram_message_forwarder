import importlib
import pkgutil
import sys
from app.logger import logger

def import_submodules(package_name: str) -> None:
    """Dynamically import all submodules of a package."""
    package = sys.modules.get(package_name)
    if not package:
        try:
            package = importlib.import_module(package_name)
            logger.info(f"Imported module {package_name}")
        except ImportError as e:
            logger.error("Failed to import base package %s: %s", package_name, e)
            return

    if not hasattr(package, "__path__"):
        return

    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            importlib.import_module(module_name)
            logger.info(f"Imported module {module_name}")
        except Exception as e:
            logger.error("Failed to import module %s: %s", module_name, e)
