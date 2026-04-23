import docker
import logging
import os
import signal
import sys
import threading
import time
from typing import Set

from emustrings import Analysis
from emustrings.celery import celery_app
from emustrings.emulators import load_emulators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for graceful shutdown
shutdown_requested = False
shutdown_event = threading.Event()
running_analyses: Set[str] = set()
shutdown_timeout = int(os.getenv('SHUTDOWN_TIMEOUT', '30'))  # seconds


def register_running_analysis(aid: str):
    """Register an analysis as currently running."""
    running_analyses.add(aid)
    logger.debug(f"Registered running analysis: {aid}")


def unregister_running_analysis(aid: str):
    """Unregister a completed analysis."""
    running_analyses.discard(aid)
    logger.debug(f"Unregistered running analysis: {aid}")


def handle_sigterm(signum, frame):
    """
    Handle SIGTERM signal for graceful shutdown.

    This handler:
    1. Sets shutdown flag to stop accepting new tasks
    2. Waits for running analyses to complete
    3. Exits cleanly after timeout if needed
    """
    global shutdown_requested

    logger.info("SIGTERM received, initiating graceful shutdown...")
    logger.info(f"Currently running {len(running_analyses)} analyses")
    if running_analyses:
        logger.info(f"Waiting for: {', '.join(running_analyses)}")

    shutdown_requested = True
    shutdown_event.set()

    # Wait for running analyses with timeout
    start_time = time.time()
    while running_analyses and (time.time() - start_time) < shutdown_timeout:
        logger.info(f"Waiting for {len(running_analyses)} analyses to complete...")
        time.sleep(1)

    if running_analyses:
        logger.warning(f"Timeout reached, {len(running_analyses)} analyses still running")
        logger.warning("Forcing shutdown")
        sys.exit(1)
    else:
        logger.info("All analyses completed, shutting down gracefully")
        sys.exit(0)


def handle_sigint(signum, frame):
    """Handle SIGINT (Ctrl+C) same as SIGTERM."""
    handle_sigterm(signum, frame)


# Register signal handlers
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigint)

# Initialize Docker client and load emulators
docker_client = docker.from_env()
load_emulators(docker_client)


@celery_app.task(name="analyze_sample", ignore_result=True)
def analyze_sample(aid):
    """
    Celery task to analyze a sample.

    This task will:
    1. Check if shutdown is requested (reject new tasks)
    2. Register itself as running
    3. Run the analysis
    4. Unregister when complete
    """
    if shutdown_requested:
        logger.warning(f"Shutdown in progress, rejecting analysis {aid}")
        raise Exception("Service is shutting down, no new analyses accepted")

    register_running_analysis(aid)

    try:
        logger.info(f"Starting analysis {aid}")
        docker_client = docker.from_env()
        analysis = Analysis(aid)
        analysis.start(docker_client)
        logger.info(f"Analysis {aid} completed successfully")
    except Exception as e:
        logger.error(f"Analysis {aid} failed: {e}")
        raise
    finally:
        unregister_running_analysis(aid)


if __name__ == "__main__":
    logger.info("Daemon started, waiting for tasks...")
    logger.info(f"Shutdown timeout: {shutdown_timeout}s")

    # Keep main thread alive
    try:
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
    except KeyboardInterrupt:
        handle_sigint(None, None)
