"""
Tests for retry utilities.
"""

import pytest
import time
from unittest.mock import Mock, patch

from emustrings.utils.retry import retry_with_backoff, is_retryable_docker_error


class TestRetryWithBackoff:
    """Test retry decorator functionality."""

    def test_successful_call_no_retry(self):
        """Test that successful calls don't trigger retries."""
        mock_func = Mock(return_value="success")

        @retry_with_backoff(max_retries=3, backoff_seconds=0.1)
        def wrapped_func():
            return mock_func()

        result = wrapped_func()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_failure_then_success(self):
        """Test that retries happen on failure then succeed."""
        mock_func = Mock(side_effect=[Exception("fail1"), Exception("fail2"), "success"])

        @retry_with_backoff(max_retries=3, backoff_seconds=0.01)
        def wrapped_func():
            return mock_func()

        result = wrapped_func()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_max_retries_exceeded(self):
        """Test that exception is raised after max retries."""
        mock_func = Mock(side_effect=Exception("always fails"))

        @retry_with_backoff(max_retries=3, backoff_seconds=0.01)
        def wrapped_func():
            return mock_func()

        with pytest.raises(Exception, match="always fails"):
            wrapped_func()

        assert mock_func.call_count == 3

    def test_specific_exception_types(self):
        """Test that only specified exceptions trigger retry."""
        mock_func = Mock(side_effect=[ValueError("fail"), "success"])

        @retry_with_backoff(max_retries=3, backoff_seconds=0.01, exceptions=(ValueError,))
        def wrapped_func():
            return mock_func()

        result = wrapped_func()
        assert result == "success"
        assert mock_func.call_count == 2

    def test_unexpected_exception_not_retried(self):
        """Test that unexpected exceptions are not retried."""
        mock_func = Mock(side_effect=ValueError("unexpected"))

        @retry_with_backoff(max_retries=3, backoff_seconds=0.01, exceptions=(TypeError,))
        def wrapped_func():
            return mock_func()

        with pytest.raises(ValueError, match="unexpected"):
            wrapped_func()

        assert mock_func.call_count == 1

    def test_backoff_timing(self):
        """Test that backoff delays increase exponentially."""
        delays = []

        original_sleep = time.sleep

        def mock_sleep(duration):
            delays.append(duration)
            return original_sleep(0.001)  # Fast sleep for testing

        mock_func = Mock(side_effect=[Exception("fail1"), Exception("fail2"), "success"])

        with patch('emustrings.utils.retry.time.sleep', side_effect=mock_sleep):
            @retry_with_backoff(max_retries=3, backoff_seconds=0.1)
            def wrapped_func():
                return mock_func()

            wrapped_func()

        # Check exponential backoff: 0.1, 0.2
        assert len(delays) == 2
        assert delays[0] == pytest.approx(0.1, rel=0.01)
        assert delays[1] == pytest.approx(0.2, rel=0.01)

    def test_max_delay_cap(self):
        """Test that delay doesn't exceed max_delay."""
        delays = []

        def mock_sleep(duration):
            delays.append(duration)

        mock_func = Mock(side_effect=[Exception("fail")] * 5 + ["success"])

        with patch('emustrings.utils.retry.time.sleep', side_effect=mock_sleep):
            @retry_with_backoff(max_retries=6, backoff_seconds=1.0, max_delay=3.0)
            def wrapped_func():
                return mock_func()

            wrapped_func()

        # Check that delay is capped at max_delay
        assert all(d <= 3.0 for d in delays)

    def test_on_retry_callback(self):
        """Test that on_retry callback is called."""
        callback_calls = []

        def on_retry_callback(exception, attempt):
            callback_calls.append((str(exception), attempt))

        mock_func = Mock(side_effect=[Exception("fail"), "success"])

        @retry_with_backoff(max_retries=3, backoff_seconds=0.01, on_retry=on_retry_callback)
        def wrapped_func():
            return mock_func()

        wrapped_func()

        assert len(callback_calls) == 1
        assert callback_calls[0][0] == "fail"
        assert callback_calls[0][1] == 1

    def test_function_metadata_preserved(self):
        """Test that function metadata is preserved."""
        @retry_with_backoff(max_retries=3)
        def my_function():
            """My docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_retry_config_attached(self):
        """Test that retry config is attached to function."""
        @retry_with_backoff(max_retries=5, backoff_seconds=2.0, max_delay=30.0)
        def my_function():
            return "result"

        assert my_function._retry_config["max_retries"] == 5
        assert my_function._retry_config["backoff_seconds"] == 2.0
        assert my_function._retry_config["max_delay"] == 30.0


class TestIsRetryableDockerError:
    """Test Docker error classification."""

    def test_connection_error_is_retryable(self):
        """Test that connection errors are retryable."""
        error = Exception("Connection refused")
        assert is_retryable_docker_error(error) is True

    def test_timeout_error_is_retryable(self):
        """Test that timeout errors are retryable."""
        error = Exception("Read timeout")
        assert is_retryable_docker_error(error) is True

    def test_service_unavailable_is_retryable(self):
        """Test that 503 errors are retryable."""
        error = Exception("503 Service Unavailable")
        assert is_retryable_docker_error(error) is True

    def test_not_found_error_is_retryable(self):
        """Test that container not found is retryable."""
        error = Exception("No such container")
        assert is_retryable_docker_error(error) is True

    def test_permanent_error_not_retryable(self):
        """Test that permanent errors are not retryable."""
        error = Exception("Image not found")
        assert is_retryable_docker_error(error) is False

    def test_empty_error_not_retryable(self):
        """Test that empty errors are not retryable."""
        error = Exception("")
        assert is_retryable_docker_error(error) is False
