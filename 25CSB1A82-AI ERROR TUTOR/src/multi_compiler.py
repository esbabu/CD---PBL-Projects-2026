"""Multi-Compiler Support - Detects Python version and normalizes behavior."""
import sys
import platform


class CompilerDetector:
    """Detects which Python interpreter/compiler is running."""

    @staticmethod
    def detect():
        info = {
            "implementation": platform.python_implementation(),
            "version": sys.version_info[:3],
            "version_string": platform.python_version(),
            "platform": platform.platform(),
            "is_pypy": hasattr(sys, "pypy_version_info"),
            "supported": sys.version_info >= (3, 8),
        }
        return info

    @staticmethod
    def normalize_error_message(message: str) -> str:
        """Normalize error messages across Python versions."""
        replacements = {
            "is not subscriptable": "does not support indexing",
            "object is not callable": "is not callable",
            "unsupported operand type(s)": "unsupported operation",
        }
        for old, new in replacements.items():
            message = message.replace(old, new)
        return message.strip()