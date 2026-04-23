"""
Validation utilities for emu-strings.

This module provides validation functions for user inputs,
including UUID validation and path sanitization to prevent
path traversal attacks.
"""

import uuid
import os
import re
from typing import Optional


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


def validate_uuid(value: str, field_name: str = "uuid") -> str:
    """
    Validate that a string is a valid UUID.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Returns:
        The validated UUID string

    Raises:
        ValidationError: If the value is not a valid UUID
    """
    if not value:
        raise ValidationError(f"{field_name} is required")

    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValidationError(f"{field_name} must be a valid UUID")


def sanitize_artifact_key(key: str) -> str:
    """
    Sanitize artifact key to prevent path traversal.

    Args:
        key: The artifact key to sanitize

    Returns:
        Sanitized key

    Raises:
        ValidationError: If the key contains path traversal attempts
    """
    if not key:
        raise ValidationError("artifact key is required")

    # Check for path traversal attempts
    if '..' in key or '/' in key or '\\' in key:
        raise ValidationError("artifact key cannot contain path separators")

    # Only allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', key):
        raise ValidationError("artifact key contains invalid characters")

    return key


def sanitize_identifier(identifier: str) -> str:
    """
    Sanitize identifier to prevent path traversal.

    Args:
        identifier: The identifier to sanitize

    Returns:
        Sanitized identifier

    Raises:
        ValidationError: If the identifier contains path traversal attempts
    """
    if not identifier:
        raise ValidationError("identifier is required")

    # Check for path traversal attempts
    if '..' in identifier:
        raise ValidationError("identifier cannot contain path traversal")

    # Normalize the path and ensure it's within the expected directory
    normalized = os.path.normpath(identifier)
    if normalized.startswith(os.sep) or '..' in normalized:
        raise ValidationError("identifier contains invalid path")

    return identifier


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal.

    Similar to werkzeug.secure_filename but with additional checks.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename

    Raises:
        ValidationError: If the filename is unsafe
    """
    if not filename:
        raise ValidationError("filename is required")

    # Remove path components
    filename = os.path.basename(filename)

    # Check for path traversal in the basename
    if '..' in filename or filename.startswith('.'):
        raise ValidationError("filename cannot start with dots")

    # Only allow safe characters
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise ValidationError("filename contains invalid characters")

    return filename


def validate_workdir_path(workdir: str, base_path: str) -> str:
    """
    Validate that a workdir path is within the expected base path.

    This prevents path traversal attacks where an attacker might
    try to access directories outside the intended scope.

    Args:
        workdir: The workdir path to validate
        base_path: The expected base path

    Returns:
        The validated absolute path

    Raises:
        ValidationError: If the path is outside the base path
    """
    # Convert to absolute paths
    abs_workdir = os.path.abspath(workdir)
    abs_base = os.path.abspath(base_path)

    # Ensure workdir starts with base_path
    if not abs_workdir.startswith(abs_base + os.sep) and abs_workdir != abs_base:
        raise ValidationError(f"path is outside allowed directory: {base_path}")

    return abs_workdir
