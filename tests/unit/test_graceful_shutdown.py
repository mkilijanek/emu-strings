"""
Tests for graceful shutdown functionality.
"""

import pytest
import signal
import threading
import time
from unittest.mock import patch, MagicMock

from emustrings import daemon


class TestGracefulShutdown:
    """Test graceful shutdown behavior."""

    def setup_method(self):
        """Reset global state before each test."""
        daemon.shutdown_requested = False
        daemon.shutdown_event.clear()
        daemon.running_analyses.clear()

    def test_register_running_analysis(self):
        """Test registering a running analysis."""
        daemon.register_running_analysis("test-aid-1")

        assert "test-aid-1" in daemon.running_analyses
        assert len(daemon.running_analyses) == 1

    def test_unregister_running_analysis(self):
        """Test unregistering a completed analysis."""
        daemon.register_running_analysis("test-aid-1")
        daemon.unregister_running_analysis("test-aid-1")

        assert "test-aid-1" not in daemon.running_analyses
        assert len(daemon.running_analyses) == 0

    def test_unregister_nonexistent_analysis(self):
        """Test unregistering an analysis that was never registered."""
        # Should not raise
        daemon.unregister_running_analysis("nonexistent")

    def test_handle_sigterm_sets_shutdown_flag(self):
        """Test that SIGTERM handler sets shutdown flag."""
        assert daemon.shutdown_requested is False

        with pytest.raises(SystemExit) as exc_info:
            daemon.handle_sigterm(signal.SIGTERM, None)

        assert daemon.shutdown_requested is True
        assert exc_info.value.code == 0  # Graceful exit

    def test_analyze_sample_rejects_during_shutdown(self):
        """Test that new analyses are rejected during shutdown."""
        daemon.shutdown_requested = True

        with pytest.raises(Exception, match="shutting down"):
            daemon.analyze_sample("test-aid")

    def test_analyze_sample_registers_and_unregisters(self):
        """Test that analysis task registers and unregisters itself."""
        daemon.shutdown_requested = False

        # Mock the actual analysis
        with patch.object(daemon, 'Analysis') as mock_analysis:
            mock_analysis_instance = MagicMock()
            mock_analysis.return_value = mock_analysis_instance

            with patch.object(daemon, 'docker_client'):
                # Call the task
                daemon.analyze_sample("test-aid")

        # Should be registered then unregistered
        # Note: In real execution, if analysis succeeds, it's unregistered
        assert "test-aid" not in daemon.running_analyses

    def test_sigterm_with_running_analyses(self):
        """Test SIGTERM handling with running analyses."""
        daemon.register_running_analysis("aid-1")
        daemon.register_running_analysis("aid-2")

        # Set a short timeout for testing
        with patch.object(daemon, 'shutdown_timeout', 1):
            with pytest.raises(SystemExit) as exc_info:
                daemon.handle_sigterm(signal.SIGTERM, None)

        # Should exit with code 1 due to timeout
        assert exc_info.value.code == 1

    def test_sigint_handler_same_as_sigterm(self):
        """Test that SIGINT handler works like SIGTERM."""
        assert daemon.shutdown_requested is False

        with pytest.raises(SystemExit):
            daemon.handle_sigint(signal.SIGINT, None)

        assert daemon.shutdown_requested is True


class TestShutdownIntegration:
    """Integration tests for shutdown behavior."""

    def setup_method(self):
        """Reset global state."""
        daemon.shutdown_requested = False
        daemon.shutdown_event.clear()
        daemon.running_analyses.clear()

    def test_complete_shutdown_flow(self):
        """Test complete shutdown flow with analyses."""
        # Register some analyses
        daemon.register_running_analysis("aid-1")
        daemon.register_running_analysis("aid-2")

        # Simulate analyses completing
        def complete_analyses():
            time.sleep(0.1)
            daemon.unregister_running_analysis("aid-1")
            time.sleep(0.1)
            daemon.unregister_running_analysis("aid-2")

        # Start completion in background
        thread = threading.Thread(target=complete_analyses)
        thread.start()

        # Trigger shutdown with longer timeout
        with patch.object(daemon, 'shutdown_timeout', 5):
            with pytest.raises(SystemExit) as exc_info:
                daemon.handle_sigterm(signal.SIGTERM, None)

        thread.join()

        # Should exit cleanly
        assert exc_info.value.code == 0

    def test_analyze_sample_exception_handling(self):
        """Test that exceptions in analysis task are handled."""
        daemon.shutdown_requested = False

        with patch.object(daemon, 'Analysis') as mock_analysis:
            mock_analysis.side_effect = Exception("Analysis failed")

            with patch.object(daemon, 'docker_client'):
                with pytest.raises(Exception, match="Analysis failed"):
                    daemon.analyze_sample("test-aid")

        # Should still unregister even on exception
        assert "test-aid" not in daemon.running_analyses
