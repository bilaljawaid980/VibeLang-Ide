from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from ai.assistant import AIAssistant
from compiler.compiler import compile_source

load_dotenv()

app = Flask(__name__)
assistant = AIAssistant()


@app.get("/")
def index():
    return render_template("index.html", ai_enabled=assistant.is_configured(), ai_model=os.getenv("AI_MODEL", "openai/gpt-4.1-nano"))


@app.get("/health")
def health_route():
    return jsonify(
        {
            "success": True,
            "service": "vibelang-compiler",
            "ai": assistant.config_summary(),
        }
    )


@app.post("/compile")
def compile_route():
    payload = request.get_json(silent=True) or {}
    source_code = payload.get("source_code", "")
    result = compile_source(source_code)
    return jsonify(result)


@app.post("/ai/explain-error")
def explain_error_route():
    if not assistant.is_configured():
        return jsonify({"success": False, "message": "AI Gateway is not configured."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        text = assistant.explain_error(payload.get("source_code", ""), payload.get("error", {}))
        return jsonify({"success": True, "text": text})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.post("/ai/explain-code")
def explain_code_route():
    if not assistant.is_configured():
        return jsonify({"success": False, "message": "AI Gateway is not configured."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        text = assistant.explain_code(payload.get("source_code", ""), payload.get("tac", []))
        return jsonify({"success": True, "text": text})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.post("/ai/generate-code")
def generate_code_route():
    if not assistant.is_configured():
        return jsonify({"success": False, "message": "AI Gateway is not configured."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        text = assistant.natural_language_to_vibelang(payload.get("prompt", ""))
        return jsonify({"success": True, "text": text})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.post("/ai/suggest-fix")
def suggest_fix_route():
    if not assistant.is_configured():
        return jsonify({"success": False, "message": "AI Gateway is not configured."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        text = assistant.suggest_fix(payload.get("source_code", ""), payload.get("errors", []))
        return jsonify({"success": True, "text": text})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "development").lower() == "development"
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=debug)
