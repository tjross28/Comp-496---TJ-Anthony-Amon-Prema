"""Flask API boundary for the in-memory compliance engine."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

from compliance_engine.evaluator import ENGINE_VERSION, evaluate_document

MAX_REQUEST_BYTES = int(os.environ.get("MAX_ANALYSIS_REQUEST_BYTES", "1000000"))


def _error(status: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), status


def _validate_payload(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."
    for field in ("document_id", "source_type", "text", "clauses"):
        if field not in payload:
            return f"Missing required field: {field}."
    if payload["source_type"] not in {"text", "html", "pdf"}:
        return "source_type must be text, html, or pdf."
    if not isinstance(payload["text"], str) or not payload["text"].strip():
        return "text must be a non-empty string."
    if len(payload["text"]) > MAX_REQUEST_BYTES:
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

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "engine_version": ENGINE_VERSION})

    @app.post("/api/v1/analyses")
    def create_analysis():
        if not request.is_json:
            return _error(415, "unsupported_media_type", "Content-Type must be application/json.")
        payload = request.get_json(silent=True)
        error = _validate_payload(payload)
        if error:
            return _error(400, "invalid_analysis_request", error)
        try:
            result = evaluate_document(payload)
        except ValueError as exc:
            return _error(400, "invalid_analysis_request", str(exc))
        return jsonify(result), 200

    @app.errorhandler(413)
    def request_too_large(_error_value):
        return _error(413, "request_too_large", "The request exceeds the maximum supported size.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
