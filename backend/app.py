"""Flask API for plain-language privacy policy summaries."""

from __future__ import annotations

import hmac
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from flask import Flask, jsonify, request

from ml.openai_nlp import NLPConfigurationError, NLPProviderError, OpenAIPolicyAnalyzer

MAX_REQUEST_BYTES = int(os.environ.get("MAX_ANALYSIS_REQUEST_BYTES", "1000000"))
DEFAULT_RATE_LIMIT = int(os.environ.get("ANALYSIS_RATE_LIMIT", "60"))
DEFAULT_RATE_WINDOW_SECONDS = int(os.environ.get("ANALYSIS_RATE_WINDOW_SECONDS", "60"))
DISCLAIMER = (
    "AI-generated reading aid, not legal advice or a legal compliance determination. "
    "Check important details against the complete policy."
)
logger = logging.getLogger("clearpolicy.api")


def _error(status: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), status


def _validate_payload(payload: Any, max_request_bytes: int) -> str | None:
    if not isinstance(payload, dict):
        return "Request body must be a JSON object."
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return "text must be a non-empty string."
    if len(text.encode("utf-8")) > max_request_bytes:
        return "text exceeds the maximum supported size."
    return None


def create_app(config_overrides: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES
    app.config.from_mapping(
        ANALYSIS_API_TOKEN=os.environ.get("ANALYSIS_API_TOKEN", ""),
        RATE_LIMIT=DEFAULT_RATE_LIMIT,
        RATE_WINDOW_SECONDS=DEFAULT_RATE_WINDOW_SECONDS,
        OPENAI_MODEL=os.environ.get("OPENAI_MODEL", "gpt-6-luna"),
        OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY", ""),
    )
    if config_overrides:
        app.config.update(config_overrides)

    analyzer = app.config.get("AI_ANALYZER") or OpenAIPolicyAnalyzer(
        model=app.config["OPENAI_MODEL"],
        api_key=app.config["OPENAI_API_KEY"],
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
        return jsonify({"status": "ok", "ai_model": analyzer.model})

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

        analysis_id = "analysis-" + uuid4().hex[:12]
        started = time.monotonic()
        try:
            summary = analyzer.analyze_text(payload["text"])
        except NLPConfigurationError as exc:
            return _error(503, "ai_analysis_not_configured", str(exc))
        except NLPProviderError:
            logger.warning("summary_generation_failed provider=openai model=%s", analyzer.model)
            return _error(
                502,
                "ai_analysis_unavailable",
                "The AI summary could not be generated. Check the backend configuration and try again.",
            )

        result = {
            "analysis_id": analysis_id,
            "analyzed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "model": analyzer.model,
            **summary,
            "disclaimer": DISCLAIMER,
        }
        logger.info(
            "summary_generated analysis_id=%s model=%s duration_ms=%d",
            analysis_id,
            analyzer.model,
            (time.monotonic() - started) * 1000,
        )
        return jsonify(result), 200

    @app.errorhandler(413)
    def request_too_large(_error_value):
        return _error(413, "request_too_large", "The policy text exceeds the maximum supported size.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
