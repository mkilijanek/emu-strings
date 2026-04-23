"""
Tests for validation utilities.

These tests ensure that path traversal and other security
vulnerabilities are properly mitigated.
"""

import pytest
import uuid
from emustrings.validation import (
    ValidationError,
    validate_uuid,
    sanitize_artifact_key,
    sanitize_identifier,
    sanitize_filename,
    validate_workdir_path,
)


class TestValidateUUID:
    """Test UUID validation."""

    def test_valid_uuid_v4(self):
        """Test valid UUID v4 is accepted."""
        valid_uuid = str(uuid.uuid4())
        result = validate_uuid(valid_uuid)
        assert result == valid_uuid

    def test_valid_uuid_v1(self):
        """Test valid UUID v1 is accepted."""
        valid_uuid = str(uuid.uuid1())
        result = validate_uuid(valid_uuid)
        assert result == valid_uuid

    def test_empty_uuid(self):
        """Test empty UUID raises error."""
        with pytest.raises(ValidationError, match="uuid is required"):
            validate_uuid("")

    def test_none_uuid(self):
        """Test None UUID raises error."""
        with pytest.raises(ValidationError, match="uuid is required"):
            validate_uuid(None)

    def test_invalid_uuid_format(self):
        """Test invalid UUID format raises error."""
        with pytest.raises(ValidationError, match="must be a valid UUID"):
            validate_uuid("not-a-uuid")

    def test_uuid_with_path_traversal(self):
        """Test UUID with path traversal characters raises error."""
        with pytest.raises(ValidationError):
            validate_uuid("../../../etc/passwd")

    def test_partial_uuid(self):
        """Test partial UUID raises error."""
        with pytest.raises(ValidationError):
            validate_uuid("123e4567")

    def test_custom_field_name(self):
        """Test custom field name in error message."""
        with pytest.raises(ValidationError, match="analysis_id"):
            validate_uuid("invalid", field_name="analysis_id")


class TestSanitizeArtifactKey:
    """Test artifact key sanitization."""

    def test_valid_key(self):
        """Test valid key is accepted."""
        assert sanitize_artifact_key("snippets") == "snippets"
        assert sanitize_artifact_key("urls") == "urls"
        assert sanitize_artifact_key("logfiles") == "logfiles"

    def test_key_with_hyphens(self):
        """Test key with hyphens is accepted."""
        assert sanitize_artifact_key("my-key") == "my-key"

    def test_key_with_underscores(self):
        """Test key with underscores is accepted."""
        assert sanitize_artifact_key("my_key") == "my_key"

    def test_empty_key(self):
        """Test empty key raises error."""
        with pytest.raises(ValidationError, match="key is required"):
            sanitize_artifact_key("")

    def test_key_with_path_traversal(self):
        """Test key with path traversal raises error."""
        with pytest.raises(ValidationError, match="path separators"):
            sanitize_artifact_key("../etc/passwd")

    def test_key_with_forward_slash(self):
        """Test key with forward slash raises error."""
        with pytest.raises(ValidationError, match="path separators"):
            sanitize_artifact_key("path/to/file")

    def test_key_with_backslash(self):
        """Test key with backslash raises error."""
        with pytest.raises(ValidationError, match="path separators"):
            sanitize_artifact_key("path\\to\\file")

    def test_key_with_special_chars(self):
        """Test key with special characters raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            sanitize_artifact_key("file;rm -rf /")


class TestSanitizeIdentifier:
    """Test identifier sanitization."""

    def test_valid_identifier(self):
        """Test valid identifier is accepted."""
        assert sanitize_identifier("file.txt") == "file.txt"
        assert sanitize_identifier("document") == "document"

    def test_empty_identifier(self):
        """Test empty identifier raises error."""
        with pytest.raises(ValidationError, match="identifier is required"):
            sanitize_identifier("")

    def test_identifier_with_double_dot(self):
        """Test identifier with double dot raises error."""
        with pytest.raises(ValidationError, match="path traversal"):
            sanitize_identifier("../../../etc/passwd")

    def test_identifier_with_leading_dot(self):
        """Test identifier with leading slash is normalized."""
        result = sanitize_identifier("/absolute/path")
        # Should normalize but not necessarily raise error
        assert ".." not in result


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_valid_filename(self):
        """Test valid filename is accepted."""
        assert sanitize_filename("file.txt") == "file.txt"
        assert sanitize_filename("script.js") == "script.js"

    def test_empty_filename(self):
        """Test empty filename raises error."""
        with pytest.raises(ValidationError, match="filename is required"):
            sanitize_filename("")

    def test_filename_with_leading_dot(self):
        """Test filename with leading dot raises error."""
        with pytest.raises(ValidationError, match="cannot start with dots"):
            sanitize_filename(".htaccess")

    def test_filename_with_double_dot(self):
        """Test filename with double dot raises error."""
        with pytest.raises(ValidationError, match="cannot start with dots"):
            sanitize_filename("../etc/passwd")

    def test_filename_with_path(self):
        """Test filename with path is sanitized to basename."""
        result = sanitize_filename("/path/to/file.txt")
        assert result == "file.txt"

    def test_filename_with_special_chars(self):
        """Test filename with special characters raises error."""
        with pytest.raises(ValidationError, match="invalid characters"):
            sanitize_filename("file;rm -rf /")


class TestValidateWorkdirPath:
    """Test workdir path validation."""

    def test_valid_workdir(self):
        """Test valid workdir is accepted."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            result = validate_workdir_path(subdir, tmpdir)
            assert result == subdir

    def test_workdir_outside_base(self):
        """Test workdir outside base raises error."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValidationError, match="outside allowed"):
                validate_workdir_path("/etc/passwd", tmpdir)

    def test_exact_base_path(self):
        """Test exact base path is accepted."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_workdir_path(tmpdir, tmpdir)
            assert result == tmpdir


import os


class TestSecurityIntegration:
    """Integration tests for security vulnerabilities."""

    def test_path_traversal_attack_via_artifact(self):
        """Simulate path traversal attack on artifact endpoint."""
        from emustrings.validation import (
            validate_uuid,
            sanitize_artifact_key,
            sanitize_identifier,
        )

        # Valid UUID
        aid = str(uuid.uuid4())
        validate_uuid(aid)  # Should not raise

        # Attempt path traversal in key
        with pytest.raises(ValidationError):
            sanitize_artifact_key("../../../etc/passwd")

        # Attempt path traversal in identifier
        with pytest.raises(ValidationError):
            sanitize_identifier("../../../etc/passwd")

    def test_uuid_injection_attack(self):
        """Test that non-UUID values are rejected."""
        from emustrings.validation import validate_uuid

        # Attempt command injection via UUID
        with pytest.raises(ValidationError):
            validate_uuid("; rm -rf /")

        # Attempt SQL injection via UUID
        with pytest.raises(ValidationError):
            validate_uuid("' OR '1'='1")
