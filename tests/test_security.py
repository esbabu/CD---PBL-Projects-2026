"""
Pytest Security Test Suite for CodeSecurityValidator
Covers:
  1. Expected to be blocked (direct imports, direct calls, aliases, direct function imports, block list members)
  2. Expected to be allowed (math/print, strings/comments with blocked words, harmless functions sharing names)
  3. Expected to produce warnings (file read/write)
  4. Syntax-error fallback (malformed blocked code, malformed harmless code, comments/strings in malformed code)
"""

import pytest
from src.security import CodeSecurityValidator, SecurityStatus


@pytest.fixture
def validator():
    return CodeSecurityValidator()


# ───────────────────────────────────────────────────────────────────
# 1. Expected to be BLOCKED
# ───────────────────────────────────────────────────────────────────

def test_blocked_direct_import_subprocess(validator):
    """Direct import of a prohibited module must be blocked."""
    code = "import subprocess\nsubprocess.run(['ls'])"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Importing subprocess should be blocked"
    assert validator.status == SecurityStatus.BLOCKED
    assert any(w.category == 'dangerous_import' for w in warnings)


def test_blocked_direct_import_socket(validator):
    """Direct import of prohibited networking module must be blocked."""
    code = "import socket\ns = socket.socket()"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Importing socket should be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_direct_import_ctypes(validator):
    """Direct import of low-level ctypes must be blocked."""
    code = "import ctypes"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Importing ctypes should be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_direct_call_eval(validator):
    """Calling eval() directly must be blocked."""
    code = "result = eval('2 + 2')"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling eval() should be blocked"
    assert validator.status == SecurityStatus.BLOCKED
    assert any(w.category == 'dangerous_function' for w in warnings)


def test_blocked_direct_call_exec(validator):
    """Calling exec() directly must be blocked."""
    code = "exec(\"print('hacked')\")"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling exec() should be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_direct_call_compile(validator):
    """Calling compile() directly must be blocked."""
    code = "c = compile('x = 1', '<string>', 'exec')"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling compile() should be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_aliased_module_import_os(validator):
    """Prohibited method accessed through an aliased module import must be blocked."""
    code = "import os as my_os\nmy_os.system('rm -rf /')"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling system() through module alias 'my_os' must be blocked"
    assert validator.status == SecurityStatus.BLOCKED
    assert any(w.level == SecurityStatus.BLOCKED for w in warnings)


def test_blocked_aliased_module_import_shutil(validator):
    """Prohibited method accessed through aliased shutil must be blocked."""
    code = "import shutil as sh\nsh.rmtree('/tmp/data')"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling rmtree() through module alias 'sh' must be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_direct_function_import_os_system(validator):
    """Prohibited function imported directly from os must be blocked."""
    code = "from os import system\nsystem('echo dangerous')"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Importing or calling 'system' directly from os must be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_direct_function_import_aliased(validator):
    """Prohibited function imported with an alias must be blocked."""
    code = "from os import system as sys_exec\nsys_exec('ls')"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling aliased prohibited function 'sys_exec' must be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_direct_function_import_from_blocked_module(validator):
    """Importing any function directly from a blocked module must be blocked."""
    code = "from subprocess import Popen\nproc = Popen(['ls'])"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Importing from subprocess must be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_blocked_sys_exit(validator):
    """Calling sys.exit() must be blocked."""
    code = "import sys\nsys.exit(1)"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Calling sys.exit() must be blocked"
    assert validator.status == SecurityStatus.BLOCKED


# ───────────────────────────────────────────────────────────────────
# 2. Expected to be ALLOWED
# ───────────────────────────────────────────────────────────────────

def test_allowed_arithmetic_and_print(validator):
    """Harmless arithmetic and printing must be allowed with PASSED status."""
    code = """
a = 10
b = 25
total = a + b
print(f"Total is: {total}")
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Harmless arithmetic should be safe"
    assert validator.status == SecurityStatus.PASSED
    assert len(warnings) == 0


def test_allowed_harmless_strings_with_prohibited_words(validator):
    """String literals containing prohibited words must NOT be blocked or warned."""
    code = """
message = "Remember not to use eval() or import subprocess in learning code."
error_guide = "The system command was: os.system('echo hi')"
print(message)
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Strings mentioning prohibited operations must be allowed"
    assert validator.status == SecurityStatus.PASSED
    assert not any(w.level == SecurityStatus.BLOCKED for w in warnings)


def test_allowed_harmless_comments_with_prohibited_words(validator):
    """Comments containing prohibited words must NOT be blocked or warned."""
    code = """
# import subprocess
# eval("2 + 2")
# os.system('rm -rf /')
# f = open('notes.txt')
x = 42
print(x)
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Comments mentioning blocked operations must be allowed"
    assert validator.status == SecurityStatus.PASSED
    assert len(warnings) == 0


def test_allowed_user_defined_function_sharing_prohibited_name(validator):
    """User-defined function named 'system' that does not import os.system must NOT be blocked."""
    code = """
def system(mode):
    return f"Operating in mode: {mode}"

status = system("safe_mode")
print(status)
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Locally defined function named 'system' must not be falsely blocked"
    assert validator.status == SecurityStatus.PASSED
    assert not any(w.level == SecurityStatus.BLOCKED for w in warnings)


def test_allowed_user_class_method_sharing_name(validator):
    """User-defined method named 'system' on a custom class must NOT be blocked."""
    code = """
class SolarSystem:
    def __init__(self, name):
        self.name = name

    def system(self):
        return f"{self.name} system"

s = SolarSystem("Milky Way")
print(s.system())
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Custom class method named 'system' must be allowed"
    assert validator.status == SecurityStatus.PASSED


# ───────────────────────────────────────────────────────────────────
# 3. Expected to produce WARNINGS
# ───────────────────────────────────────────────────────────────────

def test_warning_file_open(validator):
    """Calling open() must generate a WARNING without being blocked."""
    code = """
with open('sample.txt', 'r') as f:
    data = f.read()
print(data)
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "File access should be allowed to run, but with warning"
    assert validator.status == SecurityStatus.WARNING
    assert any(w.level == SecurityStatus.WARNING and w.category == 'file_open' for w in warnings)
    assert not any(w.level == SecurityStatus.BLOCKED for w in warnings)


def test_warning_file_write(validator):
    """Calling write() on a file handle must generate a WARNING."""
    code = """
f = open('output.txt', 'w')
f.write('Generated report line')
"""
    is_safe, warnings = validator.validate(code)
    assert is_safe, "File write should be permitted with warning"
    assert validator.status == SecurityStatus.WARNING
    assert any(w.category == 'file_write' for w in warnings)


# ───────────────────────────────────────────────────────────────────
# 4. Syntax-error fallback
# ───────────────────────────────────────────────────────────────────

def test_fallback_blocked_malformed_import(validator):
    """Malformed code containing a blocked import must be blocked via fallback scan."""
    code = "import subprocess\nif True"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Malformed code importing subprocess must be blocked"
    assert validator.status == SecurityStatus.BLOCKED
    assert any(w.level == SecurityStatus.BLOCKED for w in warnings)


def test_fallback_blocked_malformed_eval(validator):
    """Malformed code containing an eval() call must be blocked via fallback scan."""
    code = "eval('malformed' +\nif x == 1:"
    is_safe, warnings = validator.validate(code)
    assert not is_safe, "Malformed code calling eval() must be blocked"
    assert validator.status == SecurityStatus.BLOCKED


def test_fallback_allowed_malformed_harmless(validator):
    """Malformed code that is harmless must NOT be falsely blocked."""
    code = "def calculate(a, b\n    return a + b"
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Harmless malformed syntax should not be blocked"
    assert validator.status in (SecurityStatus.PASSED, SecurityStatus.WARNING)
    assert not any(w.level == SecurityStatus.BLOCKED for w in warnings)


def test_fallback_allowed_malformed_with_string_containing_blocked_word(validator):
    """Malformed code with a prohibited keyword inside a string must not be blocked."""
    code = "print('import subprocess'\nif True"
    is_safe, warnings = validator.validate(code)
    assert is_safe, "Prohibited word inside string in malformed code must not trigger block"
    assert validator.status in (SecurityStatus.PASSED, SecurityStatus.WARNING)
    assert not any(w.level == SecurityStatus.BLOCKED for w in warnings)
