"""Flask API boundary for the in-memory compliance engine."""

from __future__ import annotations

import os
import hashlib
import hmac
import logging
import time
from typing import Any

from flask import Flask, jsonify, request

from compliance_engine.evaluator import ENGINE_VERSION, evaluate_document

MAX_REQUEST_BYTES = int(os.environ.get("MAX_ANALYSIS_REQUEST_BYTES", "1000000"))
DEFAULT_RATE_LIMIT = int(os.environ.get("ANALYSIS_RATE_LIMIT", "60"))
DEFAULT_RATE_WINDOW_SECONDS = int(os.environ.get("ANALYSIS_RATE_WINDOW_SECONDS", "60"))
logger = logging.getLogger("privacy_policy_analyzer.api")


def _error(status: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), status


def _validate_payload(payload: Any, max_request_bytes: int) -> str | None:
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."
    for field in ("document_id", "source_type", "text", "clauses"):
        if field not in payload:
            return f"Missing required field: {field}."
    if payload["source_type"] not in {"text", "html", "pdf"}:
        return "source_type must be text, html, or pdf."
    if not isinstance(payload["text"], str) or not payload["text"].strip():
        return "text must be a non-empty string."
    if len(payload["text"].encode("utf-8")) > max_request_bytes:
        return "text exceeds the maximum supported size."
    if not isinstance(payload["clauses"], list) or not payload["clauses"]:
        return "clauses must be a non-empty array."
    for index, clause in enumerate(payload["clauses"]):
        if not isinstance(clause, dict) or not clause.get("clause_id") or not str(clause.get("text", "")).strip():
            return f"clauses[{index}] requires non-empty clause_id and text."
    return None


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES
    app.config.from_mapping(
        ANALYSIS_API_TOKEN=os.environ.get("ANALYSIS_API_TOKEN", ""),
        RATE_LIMIT=DEFAULT_RATE_LIMIT,
        RATE_WINDOW_SECONDS=DEFAULT_RATE_WINDOW_SECONDS,
        RULESET_PATH=os.environ.get("ANALYSIS_RULESET_PATH") or None,
    )
    request_times: dict[str, list[float]] = {}

    def is_rate_limited(client_id: str) -> bool:
        now = time.monotonic()
        window_start = now - app.config["RATE_WINDOW_SECONDS"]
        recent = [stamp for stamp in request_times.get(client_id, []) if stamp > window_start]
        request_times[client_id] = recent
        if len(recent) >= app.config["RATE_LIMIT"]:
            return True
        recent.append(now)
        return False

    def authorized() -> bool:
        expected = app.config["ANALYSIS_API_TOKEN"]
        return not expected or hmac.compare_digest(request.headers.get("X-Analysis-Token", ""), expected)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "engine_version": ENGINE_VERSION})

    @app.post("/api/v1/analyses")
    def create_analysis():
        if not authorized():
            return _error(401, "unauthorized", "A valid analysis API token is required.")
        if is_rate_limited(request.remote_addr or "unknown"):
            return _error(429, "rate_limited", "Too many analysis requests. Try again shortly.")
        if not request.is_json:
            return _error(415, "unsupported_media_type", "Content-Type must be application/json.")
        payload = request.get_json(silent=True)
        error = _validate_payload(payload, app.config["MAX_CONTENT_LENGTH"])
        if error:
            return _error(400, "invalid_analysis_request", error)
        try:
            started = time.monotonic()
            result = evaluate_document(payload, catalog_path=app.config["RULESET_PATH"])
        except ValueError as exc:
            return _error(400, "invalid_analysis_request", str(exc))
        logger.info(
            "analysis_completed request_fingerprint=%s analysis_id=%s rule_set_version=%s findings=%d duration_ms=%d",
            hashlib.sha256(str(payload["document_id"]).encode("utf-8")).hexdigest()[:12],
            result["analysis_id"], result["rule_set_version"], len(result["findings"]), (time.monotonic() - started) * 1000,
        )
        return jsonify(result), 200

    @app.errorhandler(413)
    def request_too_large(_error_value):
        return _error(413, "request_too_large", "The request exceeds the maximum supported size.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
