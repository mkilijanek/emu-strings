"""
Pytest configuration and fixtures for emu-strings tests.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def temp_workdir(tmp_path):
    """Create a temporary working directory."""
    return tmp_path / "workdir"


@pytest.fixture
def sample_jscript_code():
    """Return a sample JScript code for testing."""
    return b'''
    var WScript = new ActiveXObject("WScript.Shell");
    WScript.Run("calc.exe");
    '''


@pytest.fixture
def sample_vbscript_code():
    """Return a sample VBScript code for testing."""
    return b'''
    Set objShell = CreateObject("WScript.Shell")
    objShell.Run "calc.exe"
    '''


@pytest.fixture
def mock_uuid():
    """Return a valid UUID for testing."""
    return "12345678-1234-5678-1234-567812345678"
