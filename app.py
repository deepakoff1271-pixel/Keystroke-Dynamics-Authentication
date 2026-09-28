"""Flask application for the finished keystroke dynamics project."""

from __future__ import annotations

import os
import sys
from flask import Flask, jsonify, render_template, request

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)

from analyzer import (  # noqa: E402
    compute_correlation_analysis,
    compute_correlation_kda,
    compute_tsne,
    compute_variance_analysis,
    get_all_analysis,
    run_knn_fast,
)
from data_processor import (  # noqa: E402
    DATA_DIR,
    PASSWORDS,
    generate_synthetic_data,
    save_collected_keystrokes,
)

app = Flask(__name__)


def ensure_data() -> None:
    """Generate the baseline dataset once so the dashboard always has data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    has_defence = any(name.startswith("defence_") and name.endswith(".csv") for name in os.listdir(DATA_DIR))
    has_attack = any(name.startswith("attack_") and name.endswith(".csv") for name in os.listdir(DATA_DIR))
    if not (has_defence and has_attack):
        generate_synthetic_data()


ensure_data()


@app.route("/")
def index():
    return render_template("index.html", passwords=PASSWORDS, active_page="home")


@app.route("/collect")
def collect():
    return render_template("collect.html", passwords=PASSWORDS, active_page="collect")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", passwords=PASSWORDS, active_page="dashboard")


@app.route("/api/passwords")
def api_passwords():
    return jsonify(PASSWORDS)


@app.route("/api/save_keystrokes", methods=["POST"])
def api_save_keystrokes():
    payload = request.get_json(silent=True) or {}
    password = payload.get("password")
    participant_id = payload.get("participant_id", "guest")
    session_type = payload.get("session_type", "attack")
    metrics = payload.get("metrics", [])

    if not password:
        return jsonify({"error": "password is required"}), 400
    if not metrics:
        return jsonify({"error": "metrics are required"}), 400

    success = save_collected_keystrokes(password, participant_id, session_type, metrics)
    if not success:
        return jsonify({"error": "unknown password"}), 400

    return jsonify({"status": "saved", "entries_saved": len(metrics)})


@app.route("/api/analyze")
def api_analyze():
    password = request.args.get("password", "observer")
    return jsonify(get_all_analysis(password))


@app.route("/api/variance")
def api_variance():
    return jsonify({name: compute_variance_analysis(name) for name in PASSWORDS})


@app.route("/api/correlation")
def api_correlation():
    password = request.args.get("password", "observer")
    return jsonify(compute_correlation_analysis(password))


@app.route("/api/knn")
def api_knn():
    password = request.args.get("password", "observer")
    k = int(request.args.get("k", 3))
    return jsonify(run_knn_fast(password, k=k))


@app.route("/api/correlation_kda")
def api_correlation_kda():
    password = request.args.get("password", "observer")
    return jsonify(compute_correlation_kda(password))


@app.route("/api/tsne")
def api_tsne():
    password = request.args.get("password", "observer")
    perplexity = int(request.args.get("perplexity", 30))
    return jsonify(compute_tsne(password, perplexity=perplexity))


@app.route("/api/summary")
def api_summary():
    summary = []
    for password_name, password_info in PASSWORDS.items():
        variance = compute_variance_analysis(password_name)
        summary.append(
            {
                "password": password_name,
                "keystrokes": password_info["keystrokes"],
                "dimensions": password_info["dimensions"],
                "entropy": password_info["entropy"],
                "avg_std": variance.get("Average", 0),
            }
        )
    return jsonify(summary)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
