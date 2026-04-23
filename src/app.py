import json
import logging
import os
import time
from functools import wraps
from io import BytesIO

from flask import Flask, jsonify, request

from emustrings import Analysis, Sample
from emustrings.celery import celery_app
from emustrings.validation import (
    ValidationError,
    validate_uuid,
    validate_workdir_path,
    sanitize_artifact_key,
    sanitize_identifier,
)
from pymongo import MongoClient
from redis import Redis
import redis

logging.basicConfig(level=logging.INFO)

app = Flask("emu-strings", static_folder='/app/build')

# Configuration
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default

# Simple in-memory rate limiting storage
rate_limit_store = {}


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


def rate_limit(max_requests=10, window=60):
    """
    Rate limiting decorator.

    Args:
        max_requests: Maximum requests allowed in the window
        window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr or 'unknown'
            current_time = time.time()

            # Clean old entries
            if client_ip in rate_limit_store:
                rate_limit_store[client_ip] = [
                    t for t in rate_limit_store[client_ip]
                    if current_time - t < window
                ]
            else:
                rate_limit_store[client_ip] = []

            # Check limit
            if len(rate_limit_store[client_ip]) >= max_requests:
                logging.warning("Rate limit exceeded for IP: %s", client_ip)
                return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

            # Record request
            rate_limit_store[client_ip].append(current_time)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def check_file_size(file_storage):
    """
    Check if uploaded file size is within limits.

    Args:
        file_storage: Flask FileStorage object

    Raises:
        ValidationError: If file size exceeds limit
    """
    # Seek to end to get size
    file_storage.seek(0, 2)  # Seek to end
    size = file_storage.tell()
    file_storage.seek(0)  # Reset to beginning

    if size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size ({size} bytes) exceeds maximum allowed ({MAX_FILE_SIZE} bytes)"
        )

    return size


@app.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle validation errors with 400 Bad Request."""
    return jsonify({"error": str(e)}), 400


@app.errorhandler(RateLimitError)
def handle_rate_limit_error(e):
    """Handle rate limit errors with 429 Too Many Requests."""
    return jsonify({"error": str(e)}), 429


@app.route("/health")
def health():
    """Liveness probe - returns 200 if app is running."""
    return jsonify({"status": "healthy", "service": "emu-strings"})


@app.route("/ready")
def ready():
    """Readiness probe - checks dependencies."""
    checks = {}

    # Check MongoDB
    try:
        client = MongoClient(Analysis.MONGODB_URL, serverSelectionTimeoutMS=2000)
        client.server_info()
        checks["mongodb"] = "ok"
    except Exception as e:
        checks["mongodb"] = f"error: {str(e)}"
        return jsonify({"status": "not ready", "checks": checks}), 503

    # Check Redis
    try:
        redis_client = redis.Redis(host='redis', port=6379, socket_connect_timeout=2)
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
        return jsonify({"status": "not ready", "checks": checks}), 503

    return jsonify({"status": "ready", "checks": checks})


@app.route("/api/analysis")
def analysis_list():
    last_id = request.args.get('lastId')
    return jsonify(Analysis.list_analyses(last_id))


@app.route("/api/analysis/<aid>")
def get_analysis(aid):
    entry = Analysis.get_analysis(aid)
    if entry is None:
        return "{}"
    return jsonify(entry.to_dict())


@app.route("/api/analysis/sample/<aid>")
def get_analysis_by_sample(aid):
    entry = Analysis.get_analysis(aid)
    if entry is None:
        return "{}"
    return jsonify(entry.to_dict())


@app.route("/api/analysis/<aid>/<key>/<identifier>")
def get_artifact(aid, key, identifier):
    # Validate inputs to prevent path traversal
    validate_uuid(aid, "analysis_id")
    sanitize_artifact_key(key)
    sanitize_identifier(identifier)

    entry = Analysis.get_analysis(aid)
    if entry is None:
        return jsonify({"error": "Analysis not found"}), 404

    return entry.storage.load_element(key, identifier)


@app.route("/api/submit", methods=["POST"])
@rate_limit(max_requests=10, window=60)  # 10 requests per minute
def submit_analysis():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "File not specified"}), 400

        # Check file size before processing
        try:
            check_file_size(file)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 413  # Payload Too Large

        # Create BytesIO pseudo-file and store file from request
        strfd = BytesIO()
        file.save(strfd)
        # Add sample to analysis
        code = strfd.getvalue()
        # Create new analysis
        analysis = Analysis()
        options = json.loads(request.form.get("options", "{}"))
        language = options.get("language", "auto-detect")
        if language == "auto-detect":
            language = None
        sample = Sample(code, file.filename, language)
        # Add sample code to analysis
        analysis.add_sample(sample, options)
        # Spawn task to daemon
        celery_app.send_task("analyze_sample", args=(str(analysis.aid),))
        # Return analysis id
        return jsonify({"aid": str(analysis.aid)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def page_not_found(*args):
    return app.send_static_file("index.html")


@app.route('/')
@app.route('/<path:path>')
def send_files(path='index.html'):
    return app.send_static_file(path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
